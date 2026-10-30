# Thaw-CN 简体中文翻译

本目录保存 Thaw-CN 的简体中文翻译批次和术语表。翻译直接写入
`Thaw/Resources/Localizable.xcstrings`，不使用上游的 Crowdin 流程。

## 目录

- `glossary.json`：术语表。
- `style-guide.md`：语气、标点、占位符规则。
- `skip.json`：有意保留英文的条目及原因。
- `batches/*.json`：按 UI 区域拆分的翻译批次，便于审查和同步上游。
- `review.csv`：由脚本生成的对照表（不提交也可）。

## 命令

```sh
# 1. 列出还没翻译的条目
python3 scripts/localization/xcstrings_zh.py extract --out /tmp/zh-keys.json

# 2. 应用一批翻译（写入 needs_review 状态）
python3 scripts/localization/xcstrings_zh.py apply \
  --catalog Thaw/Resources/Localizable.xcstrings \
  --batch l10n/zh-Hans/batches/01-menus.json

# 3. 校验
python3 scripts/localization/xcstrings_zh.py validate \
  --catalog Thaw/Resources/Localizable.xcstrings --strict

# 4. 审核通过，状态改为 translated
python3 scripts/localization/xcstrings_zh.py approve \
  --catalog Thaw/Resources/Localizable.xcstrings \
  --batch l10n/zh-Hans/batches/01-menus.json
```

## 批次格式

```json
{
  "base_catalog_sha256": "可选：生成批次时的目录哈希",
  "state": "needs_review",
  "entries": {
    "英文 key": "中文译文"
  }
}
```

## 同步上游

合并上游后：

1. 重新构建一次，让 Xcode 把新增源字符串提取进目录；
2. 运行 `extract`，新条目会出现在 `needs_translation` 中；
3. 翻译新条目并 `validate --strict`；
4. 检查 `git diff` 只改动了 `zh-Hans`。
