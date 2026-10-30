# Thaw-CN @VERSION@（非官方简体中文版）

基于 [thaw-app/Thaw](https://github.com/thaw-app/Thaw) 的 `development` 分支构建，
现有应用版本 **@VERSION@（build @BUILD@）**。
本项目不是官方版本，上游不提供支持。

## 安装

1. 退出官方 Thaw。
2. 打开 DMG，把 **Thaw.app** 拖到“应用程序”。
3. 首次启动如提示“无法验证开发者”，到“系统设置 → 隐私与安全性”点击“仍要打开”。
4. 授予辅助功能、菜单栏布局访问权限；屏幕录制可选。

安装前建议备份官方偏好：

```sh
defaults export com.stonerl.Thaw ~/Desktop/thaw-backup.plist
```

## 本次内容

- 完整简体中文界面：1875 条字符串中 1851 条为中文。
- 中文 README、引导界面和双屏说明。
- 按显示器检测 macOS 未绘制的可见项目，并在该显示器的 Thaw 工具栏中提供入口。
- 修复从副屏打开 Thaw 工具栏时仍开到活动显示器的问题。
- 关闭 Sparkle 自动更新，避免官方英文版覆盖。

## 已知限制

- 本构建为 **ad-hoc 签名、未公证**；Gatekeeper 可能要求手动放行。
- Bundle ID 与官方 Thaw 相同，不能共存。
- macOS 27.0.1 不会把微信、输入法菜单、万年历绘制到副屏菜单栏；
  本版会在该屏的 Thaw 工具栏中提供访问入口（详见 README 的双屏说明）。
- Control Center 控件在无 App Group 授权的 ad-hoc 构建中可能不可用。

## 校验

下载后可用 `SHA256SUMS.txt` 校验文件：

```sh
shasum -a 256 -c SHA256SUMS.txt
```

## 许可证与署名

GPL-3.0；上游版权归 Toni Förster 等人所有。详见仓库的 LICENSE、LICENSE-EXCEPTION 和 NOTICE。
“Thaw” 为上游项目名称，本项目仅作描述性使用，不主张商标权。
