# 与上游 Thaw 同步

本 fork 基于上游 `thaw-app/Thaw` 的 `development` 分支。

- 基线提交：`aea430e11d2875f9a484ef206d5f4987f8aa41ac`（2026-10-29）
- 上游仓库：<https://github.com/thaw-app/Thaw>

## 同步步骤

```sh
git remote add upstream https://github.com/thaw-app/Thaw.git   # 只需一次
git fetch upstream
git switch development
git merge upstream/development
```

合并后：

1. 解决 `Thaw/Resources/Localizable.xcstrings` 的冲突：**以中文译文为准**，保留上游新增的英文 key，再补翻译。
2. 用 Xcode 构建一次，让 `SWIFT_EMIT_LOC_STRINGS` 把新增源字符串提取进目录。
3. 运行翻译校验：

```sh
python3 scripts/localization/xcstrings_zh.py extract --out /tmp/zh-keys.json
python3 scripts/localization/xcstrings_zh.py validate \
  --catalog Thaw/Resources/Localizable.xcstrings --strict
```

4. 翻译 `needs_translation` 中的新条目，放入 `l10n/zh-Hans/batches/`，再跑一次 `validate --strict`。
5. 检查 `git diff`：除 `zh-Hans` 外，其他语言不应变化。
6. 更新 `NOTICE` 中的基线提交。

## 冲突原则

- 上游代码改动优先；本 fork 的修改应尽量小并集中在：
  - `Thaw/Resources/Localizable.xcstrings`（中文）
  - `l10n/`、`scripts/localization/`
  - `README.md`、`README.en.md`、`NOTICE`、`UPSTREAM.md`、`CHANGELOG-CN.md`
  - 关闭 Sparkle 的相关改动
  - 双屏菜单栏改进
- 不要为了减少冲突而丢弃上游的修复。
