# Obsidian / Claudian 配置复用

`profile.json` 是从 Notes 导出的通用配置，随 Git 保存。新库应用后，仍有自己的配置和会话；这不是 Obsidian 的全局配置开关。

## 模板包含什么

- Obsidian 编辑器和外观偏好、核心插件、社区插件启用列表、快捷键（来源库有配置时）。
- Claudian 模型选择、推理强度、语言、界面偏好，以及各 provider 的通用模型偏好。
- 当前启用插件的版本和文件校验值。插件程序从这台 Mac 已安装的来源库复制，不需要再次下载。

模板不包含环境变量、凭据、CLI 路径、外部上下文路径、项目路径、权限模式、自定义系统提示词、会话和窗口布局。原始 `.claudian` 继续被 Git 排除；模板通过字段白名单导出。插件的 `data.json` 不复制，以免覆盖目标库账号、同步状态或项目设置。

## 换库时应用

在 Notes 的终端运行（需要 Python 3.9 或更新版本）：

```bash
# 先查看将更新的文件；把路径替换为实际目标库
python3 scripts/vault_config.py apply "/目标库的完整路径" --dry-run

# 关闭目标库，再应用；随后重新打开目标库
python3 scripts/vault_config.py apply "/目标库的完整路径"
```

目标文件夹必须已经存在，且与 Notes 独立。工具在 Mac 上检查目标库是否打开，拒绝向打开的库写入；应用前把受影响的原配置备份到 `~/ObsidianBackups/config-apply-*`。写入失败时还原已修改的文件。

已有库中同名的通用偏好会更新，已有的环境变量、本机路径、会话、插件数据文件保留。目标库自行启用的社区插件和核心插件也保留。自定义主题和 CSS 片段需另外安装或复制。

目前模板记录 Claudian 和 Git 插件。将来如果从 Git 克隆这个仓库到新电脑，插件程序不会随 Git 下载：先在来源库通过 Obsidian 安装插件，再重新导出模板。工具会核对插件文件校验值，版本或内容不一致时停止，避免混用旧模板和新程序。

## 更新模板

在 Notes 调整通用设置或升级插件后运行：

```bash
python3 scripts/vault_config.py export
git diff -- config-templates/obsidian/profile.json
```

确认变化后，将模板提交到 Git。只有运行 `apply` 时才更新其他库，不进行后台双向同步。

## 备份分工

- Git：笔记、Obsidian 通用配置、可复用模板、插件版本信息。
- 完整目录备份：插件程序、原始 Claudian 配置、机器环境和会话。退出 iCloud 或迁移前，完整复制 Notes 到 iCloud 外；需要包含隐藏目录。

本次整理前的完整备份保存在 Mac 本地 `~/ObsidianBackups/git-cleanup-*`；它是一次性快照，尚未设置每日自动备份。

恢复一次应用前的配置时，查看该备份中的 `manifest.json`：`files` 中值为 `true` 的文件可从 `before/` 按相对路径放回目标库；值为 `false` 的文件是应用时新建的。先关闭目标库，再恢复。备份可能含目标库原有凭据，应留在本机。
