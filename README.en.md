# Thaw-CN (Unofficial Simplified Chinese edition)

This is an **unofficial Simplified Chinese fork** of [Thaw](https://github.com/thaw-app/Thaw), the open-source menu bar manager for macOS.

> Not affiliated with or endorsed by the upstream team. Upstream does not support this build. The Chinese README is the primary document: [README.md](README.md).

## What this fork changes

- Complete Simplified Chinese UI (1851 of 1875 catalog entries; the rest are placeholders, brands, units, or the empty key).
- Chinese README and fork documentation.
- Sparkle automatic updates are disabled, so the upstream appcast cannot replace this build with the official English one.
- Dual-display menu bar improvements for macOS 27 (see the Chinese README).

## Requirements

- macOS 27.
- Xcode 27 to build from source.

## Build

```sh
git clone https://github.com/maowei-cmd/Thaw-CN.git
cd Thaw-CN
./scripts/devrun.sh --debug
```

Or build a Release app with Xcode. The app uses the upstream bundle identifier `com.stonerl.Thaw`, so it cannot coexist with the official Thaw; quit the official app and back up its preferences first:

```sh
defaults export com.stonerl.Thaw ~/Desktop/thaw-backup.plist
```

## Localization

The catalog lives in `Thaw/Resources/Localizable.xcstrings`. The review workflow, glossary, and validation tools are in [`l10n/zh-Hans`](l10n/zh-Hans/README.md) and `scripts/localization/`.

## License and attribution

GPL-3.0. See [LICENSE](LICENSE), [LICENSE-EXCEPTION](LICENSE-EXCEPTION), and [NOTICE](NOTICE).

Upstream: <https://github.com/thaw-app/Thaw> · Website: <https://www.getthaw.app>

“Thaw” is the upstream project's name and is used here descriptively, without any trademark claim.
