# 简体中文文案规范

本 fork 直接维护 `Thaw/Resources/Localizable.xcstrings`，不使用上游的 Crowdin 流程。

## 基本规则

- 源语言是英文；只修改 `localizations.zh-Hans`，其他语言保持原样。
- 称呼使用“你”，不用“您”；语气简洁、直接，与 macOS 系统中文一致。
- 使用全角标点：，。！？：；（）“”《》；省略号用 `…`。
- 中文与拉丁品牌、数字、单位之间保留一个半角空格，例如 `Thaw 工具栏`、`macOS 27`、`3 个`。
- 产品名、命令、路径、URL、键盘符号、格式占位符保持英文原样。
- Apple 官方术语优先：菜单栏、控制中心、时钟、访达、聚焦、隔空投送、专注模式、时间机器、无线局域网、蓝牙、辅助功能、屏幕录制、通知中心、锁定屏幕、输入法菜单。
- 区域名固定为：显示 / 隐藏 / 永久隐藏（`SectionNameLocalizationTests` 会断言）。
- `Thaw Bar` 统一译为 “Thaw 工具栏”；不确定时可保留 “Thaw 工具栏”。

## 占位符

- 保留 `%@`、`%lld`、`%d`、`%lf`、`%%`、`%02X` 等格式符。
- 可以使用位置参数（`%1$@`）调整语序，但索引必须从 1 连续到 n，且每个参数都被引用。
- 不翻译占位符本身，不合并/拆分参数。
- 带 `^[...](inflect: true)` 的源字符串：中文译文不要包含该注解。

## 复数

- 中文只使用 `variations.plural.other`；不要保留 `one/few/many`。
- 数量词按中文习惯处理，例如 `%lld items` → `%lld 个项目`。

## Markdown

- 保留 `**粗体**` 的成对标记；链接只翻译方括号内的文字，URL 原样保留；行内代码反引号原样保留。

## 长度

- 按钮、菜单项尽量简短；说明文字可以完整表达，但避免冗长。
- 设置页的标题/开关名优先使用 2–8 个汉字。

## 常见译法

| 英文 | 中文 |
| --- | --- |
| menu bar | 菜单栏 |
| menu bar item | 菜单栏项目 |
| section | 区域 |
| Visible / Hidden / Always Hidden | 显示 / 隐藏 / 永久隐藏 |
| Thaw Bar | Thaw 工具栏 |
| display / screen | 显示器 / 屏幕 |
| Space | 空间 |
| notch | 刘海 |
| Zen Mode | 禅模式 |
| Simple Mode | 简单模式 |
| profile | 配置 |
| spacing | 间距 |
| reveal / conceal | 显示 / 隐藏 |
| rehide | 重新隐藏 |
| overflow | 溢出 |
| stranded | 滞留 |
| permissions | 权限 |
| Full Disk Access | 完全磁盘访问权限 |
| Menu Bar Layout Access | 菜单栏布局访问权限 |
