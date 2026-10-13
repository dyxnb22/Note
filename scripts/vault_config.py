#!/usr/bin/env python3
"""Export portable preferences and apply them to a closed, separate vault."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
PROFILE = Path("config-templates/obsidian/profile.json")
PLUGIN_FILES = {"manifest.json", "main.js", "styles.css"}
APP_FIELDS = {
    "promptDelete", "alwaysUpdateLinks", "vimMode", "showLineNumber",
    "strictLineBreaks", "readableLineLength", "spellcheck", "defaultViewMode",
    "livePreview", "tabSize", "useTab", "foldHeading", "foldIndent",
    "propertiesInDocument", "showFrontmatter", "autoPairBrackets",
    "autoPairMarkdown", "useMarkdownLinks", "newLinkFormat",
}
APPEARANCE_FIELDS = {
    "accentColor", "baseFontSize", "cssTheme", "theme", "textFont",
    "monospaceFont", "interfaceFont", "enabledCssSnippets", "showInlineTitle",
    "showViewHeader", "showRibbon", "nativeMenus", "translucency",
}
CLAUDIAN_FIELDS = {
    "model", "thinkingBudget", "effortLevel", "serviceTier",
    "enableAutoTitleGeneration", "titleGenerationLocale", "titleGenerationModel",
    "keyboardNavigation", "requireCommandOrControlEnterToSend", "locale",
    "settingsProvider", "savedProviderModel", "savedProviderEffort",
    "savedProviderServiceTier", "savedProviderThinkingBudget", "maxWarmAgentProcesses",
    "enableAutoScroll", "showMessageTimestamps", "deferMathRenderingDuringStreaming",
    "expandFileEditsByDefault", "chatViewPlacement", "enableZenMode",
    "enableDualPane", "dualPaneSide", "restoreTabsOnStartup",
    "sessionManagerOrganization", "sessionManagerSort", "sessionAutoArchiveAfter",
}
PROVIDER_FIELDS = {
    "enabled", "loadUserSettings", "defaultModel", "lastModel", "visibleModels",
    "modelAliases", "preferredReasoningByModel", "preferredThinkingByModel",
    "reasoningSummary", "enableUltraEffort", "selectedMode", "toolMode",
}
OBS_FIELDS = {
    "app.json": APP_FIELDS,
    "appearance.json": APPEARANCE_FIELDS,
    "core-plugins.json": None,
    "community-plugins.json": None,
    "hotkeys.json": None,
}


def read_json(path: Path, default=None):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def json_bytes(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()


def pick(value: dict, fields: set) -> dict:
    return {key: val for key, val in value.items() if key in fields}


def portable_claudian(settings: dict) -> dict:
    result = pick(settings, CLAUDIAN_FIELDS)
    result["providerConfigs"] = {
        name: pick(config, PROVIDER_FIELDS)
        for name, config in settings.get("providerConfigs", {}).items()
        if isinstance(config, dict)
    }
    return result


def validate(profile: dict) -> None:
    if profile.get("formatVersion") != 1:
        raise ValueError("不支持的模板格式")
    for name, value in profile["obsidian"].items():
        if name not in OBS_FIELDS:
            raise ValueError(f"不支持的 Obsidian 配置: {name}")
        if OBS_FIELDS[name] is not None and pick(value, OBS_FIELDS[name]) != value:
            raise ValueError(f"配置含非通用字段: {name}")
        if name == "community-plugins.json" and not isinstance(value, list):
            raise ValueError("插件启用列表必须是数组")
        if name != "community-plugins.json" and not isinstance(value, dict):
            raise ValueError(f"配置必须是对象: {name}")
    if portable_claudian(profile["claudian"]) != profile["claudian"]:
        raise ValueError("Claudian 模板含环境、路径、会话或其他未支持字段")
    for plugin_id, meta in profile["plugins"].items():
        if not re.fullmatch(r"[A-Za-z0-9_-]+", plugin_id):
            raise ValueError("插件 ID 无效")
        if not {"manifest.json", "main.js"}.issubset(meta["files"]):
            raise ValueError(f"插件程序不完整: {plugin_id}")
        if not set(meta["files"]).issubset(PLUGIN_FILES):
            raise ValueError(f"插件包含未支持的文件: {plugin_id}")
    text = json_bytes(profile).decode()
    if re.search(r"/Users/|/home/|[A-Za-z]:\\\\|-----BEGIN .*PRIVATE KEY|"
                 r"\bsk-(?:proj-|ant-api\d+-)?[A-Za-z0-9_-]{30,}|"
                 r"\bgh[pousr]_[A-Za-z0-9]{30,}", text):
        raise ValueError("模板含疑似本机路径或凭据；未写入，请检查通用字段")


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temporary = tempfile.mkstemp(prefix=".config-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def export_profile(source: Path) -> dict:
    obsidian = {}
    for name, fields in OBS_FIELDS.items():
        value = read_json(source / ".obsidian" / name)
        if value is not None:
            obsidian[name] = pick(value, fields) if fields is not None else value
    plugins = {}
    for plugin_id in obsidian.get("community-plugins.json", []):
        if not re.fullmatch(r"[A-Za-z0-9_-]+", plugin_id):
            raise ValueError("插件 ID 无效")
        folder = source / ".obsidian/plugins" / plugin_id
        manifest = read_json(folder / "manifest.json")
        if not manifest or manifest.get("id") != plugin_id:
            raise ValueError(f"缺少插件或插件 ID 不匹配: {plugin_id}")
        plugins[plugin_id] = {
            "version": manifest["version"],
            "files": {
                name: hashlib.sha256((folder / name).read_bytes()).hexdigest()
                for name in sorted(PLUGIN_FILES) if (folder / name).is_file()
            },
        }
    profile = {
        "formatVersion": 1,
        "obsidian": obsidian,
        "claudian": portable_claudian(read_json(
            source / ".claudian/claudian-settings.json", {})),
        "plugins": plugins,
    }
    validate(profile)
    atomic_write(source / PROFILE, json_bytes(profile))
    return profile


def merge(target, defaults):
    if isinstance(target, dict) and isinstance(defaults, dict):
        result = dict(target)
        for key, value in defaults.items():
            result[key] = merge(result.get(key), value)
        return result
    return defaults


def assert_closed(target: Path) -> None:
    registry = Path.home() / "Library/Application Support/obsidian/obsidian.json"
    if sys.platform != "darwin" or not registry.exists():
        raise ValueError("此工具的打开状态检查支持 macOS；请在 Mac 上应用模板")
    running = subprocess.run(["pgrep", "-x", "Obsidian"], capture_output=True).returncode == 0
    vaults = read_json(registry, {}).get("vaults", {}).values()
    if running and any(Path(v.get("path", "")).resolve() == target
                       and v.get("open") for v in vaults):
        raise ValueError("目标库正被 Obsidian 打开；请关闭目标库后再应用")


def destination(target: Path, relative: Path) -> Path:
    path = target / relative
    if not path.resolve().is_relative_to(target):
        raise ValueError(f"目标配置路径指向库外: {relative}")
    for item in [path, *path.parents]:
        if item == target:
            break
        if item.is_symlink():
            raise ValueError(f"目标配置包含软链接: {relative}")
    return path


def apply_profile(source: Path, target: Path, backup_root: Path, dry_run=False):
    source, target = source.resolve(), target.resolve()
    if not target.is_dir():
        raise ValueError("目标文件夹不存在；请先创建笔记库文件夹")
    if target.is_relative_to(source) or source.is_relative_to(target):
        raise ValueError("目标库必须与来源库独立，不能相同或相互嵌套")
    profile = read_json(source / PROFILE)
    if profile is None:
        raise ValueError("没有配置模板；请先运行 export")
    validate(profile)
    changes = {}
    for name, value in profile["obsidian"].items():
        relative = Path(".obsidian") / name
        existing = read_json(destination(target, relative))
        if name == "community-plugins.json":
            value = list(dict.fromkeys((existing or []) + value))
        elif name == "core-plugins.json":
            value = merge(existing or {}, value)
            for key, enabled in (existing or {}).items():
                if enabled is True:
                    value[key] = True
        else:
            value = merge(existing or {}, value)
        changes[relative] = json_bytes(value)
    for plugin_id, meta in profile["plugins"].items():
        for name, expected in meta["files"].items():
            relative = Path(".obsidian/plugins") / plugin_id / name
            file = source / relative
            if not file.is_file():
                raise ValueError(f"来源库缺少 {plugin_id}/{name}；请先安装插件再 export")
            data = file.read_bytes()
            if hashlib.sha256(data).hexdigest() != expected:
                raise ValueError(f"来源插件已变化: {plugin_id}；请重新 export")
            changes[relative] = data
    relative = Path(".claudian/claudian-settings.json")
    changes[relative] = json_bytes(merge(read_json(destination(target, relative), {}),
                                        profile["claudian"]))
    before = {}
    for relative in changes:
        path = destination(target, relative)
        before[relative] = path.read_bytes() if path.exists() else None
    changes = {p: data for p, data in changes.items() if before[p] != data}
    if dry_run or not changes:
        return sorted(map(str, changes)), None
    assert_closed(target)
    backup = backup_root / ("config-apply-" + datetime.now().strftime("%Y%m%d-%H%M%S")
                            + "-" + uuid4().hex[:8])
    if backup.resolve().is_relative_to(target):
        raise ValueError("备份目录不能位于目标库中")
    backup.mkdir(parents=True, mode=0o700)
    for relative in changes:
        if before[relative] is not None:
            atomic_write(backup / "before" / relative, before[relative])
    atomic_write(backup / "manifest.json", json_bytes({
        "target": str(target),
        "files": {str(p): before[p] is not None for p in changes},
    }))
    written = []
    try:
        for relative, data in changes.items():
            path = destination(target, relative)
            current = path.read_bytes() if path.exists() else None
            if current != before[relative]:
                raise ValueError(f"目标配置在应用期间被改动: {relative}")
            atomic_write(path, data)
            written.append(relative)
    except Exception:
        for relative in reversed(written):
            if before[relative] is None:
                destination(target, relative).unlink()
            else:
                atomic_write(destination(target, relative), before[relative])
        raise
    return sorted(map(str, changes)), backup


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("export", help="从当前 Notes 导出通用配置模板")
    apply = sub.add_parser("apply", help="把模板和已安装插件复制到独立的目标库")
    apply.add_argument("target", type=Path)
    apply.add_argument("--dry-run", action="store_true", help="预览，不写入任何文件")
    args = parser.parse_args()
    try:
        if args.command == "export":
            profile = export_profile(ROOT)
            print(f"已导出模板: {ROOT / PROFILE}；插件数: {len(profile['plugins'])}")
        else:
            files, backup = apply_profile(ROOT, args.target.expanduser(),
                                         Path.home() / "ObsidianBackups", args.dry_run)
            print("将更新:" if args.dry_run else "已更新:")
            for name in files:
                print(f"- {name}")
            if backup:
                print(f"原配置备份: {backup}")
            elif not files:
                print("目标库已经一致，无需更新")
        return 0
    except (ValueError, OSError, TypeError, KeyError) as error:
        print(f"未完成: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
