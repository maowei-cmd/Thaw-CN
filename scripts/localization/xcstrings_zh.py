#!/usr/bin/env python3
"""Maintain the zh-Hans translations in Thaw's string catalog.

The catalog is Xcode's JSON format. This tool edits only
`strings.*.localizations.zh-Hans`, preserves key order and every other
language byte-for-byte, and validates the result before it is committed.

Commands:
  extract        list keys and the translation work still to do
  apply          write a batch of translations
  approve        flip needs_review to translated
  validate       check the catalog (--strict for release)
  report         write a CSV review sheet

Examples:
  python3 scripts/localization/xcstrings_zh.py extract \
      --catalog Thaw/Resources/Localizable.xcstrings --out /tmp/zh-keys.json
  python3 scripts/localization/xcstrings_zh.py apply \
      --catalog Thaw/Resources/Localizable.xcstrings --batch l10n/zh-Hans/batches/01.json
  python3 scripts/localization/xcstrings_zh.py validate \
      --catalog Thaw/Resources/Localizable.xcstrings --strict
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

CJK = re.compile(r"[\u4e00-\u9fff]")
PLACEHOLDER = re.compile(
    r"%(?:(\d+)\$)?([-+ #0']*)(\d+)?(?:\.(\d+))?(hh|h|ll|l|q|L|z|t|j)?([@diuUxXoOfFeEgGcCsSpaA%])"
)
MARKDOWN_LINK = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
INFLECT = re.compile(r"\^\[([^\]]*)\]\(inflect:\s*true\)")
DEFAULT_STATE = "translated"


def eprint(*args: object) -> None:
    print(*args, file=sys.stderr)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_catalog(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_catalog(data: dict) -> str:
    """Serialize like Xcode: two-space indent, " : " separator, no trailing newline."""

    def esc(value: str) -> str:
        return json.dumps(value, ensure_ascii=False)

    def dump(obj, indent: int = 0) -> str:
        pad = " " * indent
        if isinstance(obj, dict):
            if not obj:
                return "{\n\n" + pad + "}"
            body = ",\n".join(
                " " * (indent + 2) + esc(key) + " : " + dump(value, indent + 2)
                for key, value in obj.items()
            )
            return "{\n" + body + "\n" + pad + "}"
        if isinstance(obj, list):
            if not obj:
                return "[\n\n" + pad + "]"
            body = ",\n".join(" " * (indent + 2) + dump(value, indent + 2) for value in obj)
            return "[\n" + body + "\n" + pad + "]"
        if isinstance(obj, bool):
            return "true" if obj else "false"
        if obj is None:
            return "null"
        if isinstance(obj, (int, float)):
            return json.dumps(obj)
        if isinstance(obj, str):
            return esc(obj)
        raise TypeError(f"unsupported value {type(obj)!r}")

    return dump(data)


def write_catalog(path: Path, data: dict) -> None:
    path.write_text(dump_catalog(data), encoding="utf-8")


def zh_entry(entry: dict) -> dict | None:
    return entry.get("localizations", {}).get("zh-Hans")


def zh_value(entry: dict) -> tuple[str, str]:
    """Return (value, state) for zh-Hans, flattening plurals to their "other" case."""
    loc = zh_entry(entry)
    if not loc:
        return "", ""
    if "stringUnit" in loc:
        unit = loc["stringUnit"]
        return unit.get("value", ""), unit.get("state", "")
    plural = loc.get("variations", {}).get("plural", {})
    unit = plural.get("other", {}).get("stringUnit", {})
    return unit.get("value", ""), unit.get("state", "")


def has_plural(entry: dict) -> bool:
    if "variations" in entry:
        return True
    return any("variations" in localization for localization in entry.get("localizations", {}).values())


def source_has_plural(entry: dict) -> bool:
    return "variations" in (entry.get("localizations", {}).get("en") or {})


def placeholders(text: str) -> tuple[list[str], list[int]]:
    """Formats without their positional index, plus every positional index seen."""
    formats: list[str] = []
    positions: list[int] = []
    for match in PLACEHOLDER.finditer(text):
        position, flags, width, precision, length, conversion = match.groups()
        if conversion == "%":
            continue
        if position:
            positions.append(int(position))
        formats.append("%" + (flags or "") + (width or "") + (("." + precision) if precision else "") + (length or "") + conversion)
    return formats, positions


def check_placeholders(key: str, value: str) -> list[str]:
    problems: list[str] = []
    expected, expected_positions = placeholders(key)
    actual, actual_positions = placeholders(value)
    if sorted(expected) != sorted(actual):
        problems.append(f"placeholder mismatch: source={expected} zh={actual}")
    if actual_positions:
        wanted = list(range(1, len(actual) + 1))
        if sorted(actual_positions) != wanted:
            problems.append(f"positional indices are not 1..{len(actual)}: {actual_positions}")
    if expected_positions and not actual_positions:
        problems.append("source uses positional placeholders but zh does not")
    return problems


def check_markdown(key: str, value: str) -> list[str]:
    problems: list[str] = []
    # The inflection annotation is a SwiftUI modifier, not a Markdown link.
    key = INFLECT.sub(lambda match: match.group(1), key)
    if key.count("**") != value.count("**"):
        problems.append("bold markers differ")
    if key.count("`") != value.count("`"):
        problems.append("inline-code markers differ")
    source_links = [url for _, url in MARKDOWN_LINK.findall(key)]
    value_links = [url for _, url in MARKDOWN_LINK.findall(value)]
    if sorted(source_links) != sorted(value_links):
        problems.append(f"link URLs differ: source={source_links} zh={value_links}")
    return problems


def check_inflect(key: str, value: str) -> list[str]:
    if INFLECT.search(key):
        if "inflect: true" in value or INFLECT.search(value):
            return ["zh must not contain the inflect annotation"]
    return []


def check_whitespace(key: str, value: str) -> list[str]:
    problems: list[str] = []
    for name, char in (("newline", "\n"), ("tab", "\t")):
        if key.count(char) != value.count(char):
            problems.append(f"{name} count differs")
    if key.strip() != key and value.strip() == value:
        problems.append("source has outer whitespace but zh does not")
    return problems


def iter_entries(data: dict):
    for key, entry in data.get("strings", {}).items():
        yield key, entry


def load_skip(path: Path | None) -> dict[str, str]:
    if not path or not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    return raw.get("skip", raw) if isinstance(raw, dict) else {}


def cmd_extract(args: argparse.Namespace) -> int:
    path = Path(args.catalog)
    raw = path.read_bytes()
    data = json.loads(raw.decode("utf-8"))
    skip = load_skip(Path(args.skip) if args.skip else None)
    entries = []
    for key, entry in iter_entries(data):
        value, state = zh_value(entry)
        formats, _ = placeholders(key)
        entries.append(
            {
                "key": key,
                "zh": value,
                "state": state,
                "comment": entry.get("comment", ""),
                "extractionState": entry.get("extractionState", ""),
                "plural": source_has_plural(entry) or has_plural(entry),
                "placeholders": formats,
                "markdown": bool(MARKDOWN_LINK.search(key) or "**" in key or "`" in key),
                "inflect": bool(INFLECT.search(key)),
                "needs_translation": key != "" and (not value.strip() or not CJK.search(value)) and key not in skip,
                "skip": key in skip,
            }
        )
    out = {
        "catalog_sha256": sha256(raw),
        "sourceLanguage": data.get("sourceLanguage"),
        "version": data.get("version"),
        "total": len(entries),
        "needs_translation": sum(1 for entry in entries if entry["needs_translation"]),
        "entries": entries,
    }
    if args.out:
        Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        eprint(f"wrote {args.out}: {out['needs_translation']} of {out['total']} keys need translation")
    else:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def set_zh_value(entry: dict, value: str, state: str) -> None:
    loc = entry.setdefault("localizations", {}).setdefault("zh-Hans", {})
    if has_plural(entry):
        plural = loc.setdefault("variations", {}).setdefault("plural", {})
        plural.clear()
        plural["other"] = {"stringUnit": {"state": state, "value": value}}
        loc.pop("stringUnit", None)
    else:
        loc["stringUnit"] = {"state": state, "value": value}
        loc.pop("variations", None)


def cmd_apply(args: argparse.Namespace) -> int:
    path = Path(args.catalog)
    raw = path.read_bytes()
    data = json.loads(raw.decode("utf-8"))
    batch = json.loads(Path(args.batch).read_text(encoding="utf-8"))
    expected_sha = batch.get("base_catalog_sha256")
    if expected_sha and expected_sha != sha256(raw):
        eprint(f"error: catalog changed since the batch was made (expected {expected_sha[:12]}, got {sha256(raw)[:12]})")
        return 2
    entries = batch.get("entries", batch)
    state = batch.get("state") or args.state or "needs_review"
    strings = data.get("strings", {})
    applied = 0
    unknown: list[str] = []
    for key, value in entries.items():
        entry = strings.get(key)
        if entry is None:
            unknown.append(key)
            continue
        if not isinstance(value, str):
            eprint(f"error: {key!r} value must be a string")
            return 2
        set_zh_value(entry, value, state)
        applied += 1
    if unknown:
        eprint(f"error: {len(unknown)} key(s) are not in the catalog:")
        for key in unknown[:20]:
            eprint(f"  {key!r}")
        return 2
    write_catalog(path, data)
    eprint(f"applied {applied} translations with state {state!r}")
    return 0


def cmd_apply_list(args: argparse.Namespace) -> int:
    """Apply translations supplied as parallel key/value arrays.

    This keeps long keys out of hand-written batches: generate the key list with
    `extract`, write the values in the same order, and apply them here.
    """
    keys = json.loads(Path(args.keys).read_text(encoding="utf-8"))
    values = json.loads(Path(args.values).read_text(encoding="utf-8"))
    if len(keys) != len(values):
        eprint(f"error: {len(keys)} keys but {len(values)} values")
        return 2
    entries = dict(zip(keys, values, strict=True))
    batch = {"state": args.state or "needs_review", "entries": entries}
    path = Path(args.catalog)
    raw = path.read_bytes()
    data = json.loads(raw.decode("utf-8"))
    strings = data.get("strings", {})
    unknown = [key for key in entries if key not in strings]
    if unknown:
        eprint(f"error: {len(unknown)} key(s) are not in the catalog:")
        for key in unknown[:20]:
            eprint(f"  {key!r}")
        return 2
    for key, value in entries.items():
        if not isinstance(value, str):
            eprint(f"error: {key!r} value must be a string")
            return 2
        set_zh_value(strings[key], value, batch["state"])
    if args.batch_out:
        out = Path(args.batch_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(batch, ensure_ascii=False, indent=2), encoding="utf-8")
        eprint(f"wrote {out}")
    write_catalog(path, data)
    eprint(f"applied {len(entries)} translations with state {batch['state']!r}")
    return 0


def cmd_approve(args: argparse.Namespace) -> int:
    path = Path(args.catalog)
    data = json.loads(path.read_bytes().decode("utf-8"))
    wanted: set[str] | None = None
    if args.batch:
        batch = json.loads(Path(args.batch).read_text(encoding="utf-8"))
        wanted = set(batch.get("entries", batch).keys())
    changed = 0
    for key, entry in iter_entries(data):
        if wanted is not None and key not in wanted:
            continue
        loc = zh_entry(entry)
        if not loc:
            continue
        units = []
        if "stringUnit" in loc:
            units.append(loc["stringUnit"])
        for case in loc.get("variations", {}).get("plural", {}).values():
            if "stringUnit" in case:
                units.append(case["stringUnit"])
        for unit in units:
            if unit.get("state") in {"needs_review", "new"}:
                unit["state"] = DEFAULT_STATE
                changed += 1
    write_catalog(path, data)
    eprint(f"approved {changed} string unit(s)")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    path = Path(args.catalog)
    raw = path.read_bytes()
    data = json.loads(raw.decode("utf-8"))
    skip = load_skip(Path(args.skip) if args.skip else None)
    errors: list[str] = []
    warnings: list[str] = []
    counts = {"total": 0, "chinese": 0, "missing": 0, "empty": 0, "new": 0, "needs_review": 0}
    strings = data.get("strings", {})
    for key, entry in iter_entries(data):
        counts["total"] += 1
        value, state = zh_value(entry)
        if zh_entry(entry) is None:
            counts["missing"] += 1
            errors.append(f"{key!r}: no zh-Hans localization")
            continue
        if not value.strip():
            if key == "":
                counts["empty"] += 1
                continue
            counts["empty"] += 1
            errors.append(f"{key!r}: empty zh-Hans value")
            continue
        if state == "new":
            counts["new"] += 1
            errors.append(f"{key!r}: state is still 'new'")
        if state == "needs_review":
            counts["needs_review"] += 1
            if args.strict:
                errors.append(f"{key!r}: state is still 'needs_review'")
        if CJK.search(value):
            counts["chinese"] += 1
        elif key not in skip:
            errors.append(f"{key!r}: value has no Chinese characters: {value!r}")
        for problem in (
            check_placeholders(key, value)
            + check_markdown(key, value)
            + check_inflect(key, value)
            + check_whitespace(key, value)
        ):
            errors.append(f"{key!r}: {problem}")
        zh = zh_entry(entry) or {}
        if "variations" in zh:
            cases = set(zh["variations"].get("plural", {}))
            if cases - {"other"}:
                errors.append(f"{key!r}: zh-Hans plural has cases other than 'other': {sorted(cases)}")
            if "other" not in cases:
                errors.append(f"{key!r}: zh-Hans plural has no 'other' case")
        if len(value) > max(40, len(key) * 3 + 40):
            warnings.append(f"{key!r}: zh-Hans value is much longer than the source")

    if data.get("sourceLanguage") != "en":
        errors.append(f"sourceLanguage is {data.get('sourceLanguage')!r}, expected 'en'")
    if args.baseline:
        baseline = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
        for key, entry in iter_entries(baseline):
            current = strings.get(key)
            if current is None:
                errors.append(f"{key!r}: key disappeared")
                continue
            for language, localization in entry.get("localizations", {}).items():
                if language == "zh-Hans":
                    continue
                if current.get("localizations", {}).get(language) != localization:
                    errors.append(f"{key!r}: non-zh-Hans language {language!r} changed")
                for field in ("comment", "extractionState"):
                    if current.get(field) != entry.get(field):
                        errors.append(f"{key!r}: {field} changed")
        if list(baseline.get("strings", {})) != list(strings)[: len(baseline.get("strings", {}))]:
            errors.append("key order changed")
        for key in list(strings)[len(baseline.get("strings", {})) :]:
            if key in baseline.get("strings", {}):
                errors.append(f"{key!r}: key was reordered")

    if errors:
        for error in errors[:80]:
            eprint(f"ERROR {error}")
        if len(errors) > 80:
            eprint(f"... and {len(errors) - 80} more errors")
    for warning in warnings[:20]:
        eprint(f"WARN {warning}")
    print(json.dumps(counts, indent=2))
    if errors:
        eprint(f"validation failed with {len(errors)} error(s)")
        return 1
    eprint("validation passed")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    data = json.loads(Path(args.catalog).read_bytes().decode("utf-8"))
    with Path(args.out).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["state", "key", "zh-Hans", "comment"])
        for key, entry in iter_entries(data):
            value, state = zh_value(entry)
            writer.writerow([state, key, value, entry.get("comment", "")])
    eprint(f"wrote {args.out}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    extract = sub.add_parser("extract")
    extract.add_argument("--catalog", default="Thaw/Resources/Localizable.xcstrings")
    extract.add_argument("--skip", default="l10n/zh-Hans/skip.json")
    extract.add_argument("--out")
    extract.set_defaults(func=cmd_extract)

    apply = sub.add_parser("apply")
    apply.add_argument("--catalog", default="Thaw/Resources/Localizable.xcstrings")
    apply.add_argument("--batch", required=True)
    apply.add_argument("--state")
    apply.set_defaults(func=cmd_apply)

    apply_list = sub.add_parser("apply-list")
    apply_list.add_argument("--catalog", default="Thaw/Resources/Localizable.xcstrings")
    apply_list.add_argument("--keys", required=True)
    apply_list.add_argument("--values", required=True)
    apply_list.add_argument("--state")
    apply_list.add_argument("--batch-out")
    apply_list.set_defaults(func=cmd_apply_list)

    approve = sub.add_parser("approve")
    approve.add_argument("--catalog", default="Thaw/Resources/Localizable.xcstrings")
    approve.add_argument("--batch")
    approve.set_defaults(func=cmd_approve)

    validate = sub.add_parser("validate")
    validate.add_argument("--catalog", default="Thaw/Resources/Localizable.xcstrings")
    validate.add_argument("--skip", default="l10n/zh-Hans/skip.json")
    validate.add_argument("--baseline")
    validate.add_argument("--strict", action="store_true")
    validate.set_defaults(func=cmd_validate)

    report = sub.add_parser("report")
    report.add_argument("--catalog", default="Thaw/Resources/Localizable.xcstrings")
    report.add_argument("--out", default="l10n/zh-Hans/review.csv")
    report.set_defaults(func=cmd_report)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
