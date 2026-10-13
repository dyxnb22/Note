"""Exercise export and cross-vault application in disposable vaults."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import vault_config as config


class VaultConfigTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.source = self.root / "source"
        self.target = self.root / "target"
        self.target.mkdir()
        self.put(self.source, ".obsidian/app.json", {
            "promptDelete": True, "attachmentFolderPath": "project-only"})
        self.put(self.source, ".obsidian/core-plugins.json", {
            "file-explorer": True, "sync": False})
        self.put(self.source, ".obsidian/community-plugins.json", ["realclaudian"])
        self.put(self.source, ".obsidian/plugins/realclaudian/manifest.json", {
            "id": "realclaudian", "version": "1.0.0"})
        (self.source / ".obsidian/plugins/realclaudian/main.js").write_text("fixture")
        self.put(self.source, ".claudian/claudian-settings.json", {
            "locale": "zh", "model": "fixture-model",
            "sharedEnvironmentVariables": "PRIVATE_VARIABLE=source-private",
            "systemPrompt": "project-private", "mediaFolder": "project-assets",
            "providerConfigs": {"claude": {
                "enabled": True, "loadUserSettings": True,
                "environmentVariables": "PRIVATE_VARIABLE=provider-private",
                "cliPath": "machine-private", "safeMode": "bypassPermissions",
            }},
        })
        config.export_profile(self.source)

    def put(self, root, relative, value):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value))

    def apply(self, **kwargs):
        with patch.object(config, "assert_closed"):
            return config.apply_profile(self.source, self.target,
                                        self.root / "backups", **kwargs)

    def test_export_does_not_include_environment_paths_permissions_or_prompt(self):
        exported = (self.source / config.PROFILE).read_text()
        for private in ["source-private", "provider-private", "machine-private",
                        "project-private", "project-assets", "bypassPermissions"]:
            self.assertNotIn(private, exported)
        profile = json.loads(exported)
        self.assertEqual(profile["claudian"]["model"], "fixture-model")
        self.assertNotIn("attachmentFolderPath", profile["obsidian"]["app.json"])

    def test_apply_preserves_local_settings_sessions_plugins_and_backs_up(self):
        self.put(self.target, ".claudian/claudian-settings.json", {
            "locale": "en", "sharedEnvironmentVariables": "target-private",
            "providerConfigs": {"claude": {
                "cliPath": "target-cli", "environmentVariables": "target-env",
                "safeMode": "default"}},
        })
        self.put(self.target, ".obsidian/community-plugins.json", ["target-plugin"])
        self.put(self.target, ".obsidian/core-plugins.json", {"sync": True})
        self.put(self.target, ".claudian/sessions/existing.json", {"message": "keep"})
        self.put(self.target, ".obsidian/plugins/realclaudian/data.json", {"keep": True})
        self.put(self.target, ".obsidian/workspace.json", {"keep": True})
        path = self.target / ".claudian/claudian-settings.json"
        before = path.read_bytes()
        files, backup = self.apply()
        result = json.loads(path.read_text())
        self.assertEqual(result["locale"], "zh")
        self.assertEqual(result["sharedEnvironmentVariables"], "target-private")
        self.assertEqual(result["providerConfigs"]["claude"]["environmentVariables"], "target-env")
        self.assertEqual(result["providerConfigs"]["claude"]["cliPath"], "target-cli")
        self.assertEqual(result["providerConfigs"]["claude"]["safeMode"], "default")
        self.assertEqual((backup / "before/.claudian/claudian-settings.json").read_bytes(), before)
        self.assertEqual(config.read_json(self.target / ".obsidian/community-plugins.json"),
                         ["target-plugin", "realclaudian"])
        self.assertTrue(config.read_json(self.target / ".obsidian/core-plugins.json")["sync"])
        self.assertEqual((self.target / ".obsidian/plugins/realclaudian/main.js").read_text(), "fixture")
        self.assertNotIn(".claudian/sessions/existing.json", files)
        self.assertEqual(config.read_json(self.target / ".obsidian/plugins/realclaudian/data.json"),
                         {"keep": True})
        self.assertEqual(config.read_json(self.target / ".obsidian/workspace.json"), {"keep": True})
        self.assertEqual(self.apply(), ([], None))

    def test_preview_and_changed_source_do_not_write_target(self):
        files, backup = self.apply(dry_run=True)
        self.assertTrue(files)
        self.assertIsNone(backup)
        self.assertEqual(list(self.target.iterdir()), [])
        (self.source / ".obsidian/plugins/realclaudian/main.js").write_text("updated")
        with self.assertRaisesRegex(ValueError, "来源插件已变化"):
            self.apply()
        self.assertEqual(list(self.target.iterdir()), [])

    def test_rejects_nested_vaults_links_and_open_targets(self):
        nested = self.source / "nested"
        nested.mkdir()
        with self.assertRaisesRegex(ValueError, "相互嵌套"):
            config.apply_profile(self.source, nested, self.root / "backups")
        outside = self.root / "outside"
        outside.mkdir()
        (self.target / ".obsidian").symlink_to(outside)
        with self.assertRaisesRegex(ValueError, "库外"):
            self.apply()
        self.assertEqual(list(outside.iterdir()), [])
        (self.target / ".obsidian").unlink()
        with patch.object(config, "assert_closed", side_effect=ValueError("目标库正被打开")):
            with self.assertRaisesRegex(ValueError, "正被打开"):
                config.apply_profile(self.source, self.target, self.root / "backups")
        self.assertEqual(list(self.target.iterdir()), [])

    def test_failed_write_restores_previous_files(self):
        self.put(self.target, ".obsidian/app.json", {"promptDelete": False})
        existing = self.target / ".obsidian/app.json"
        before = existing.read_bytes()
        original_write = config.atomic_write

        def failing_write(path, data):
            if path == self.target / ".obsidian/core-plugins.json":
                raise OSError("模拟磁盘写入失败")
            original_write(path, data)

        with patch.object(config, "atomic_write", side_effect=failing_write):
            with self.assertRaisesRegex(OSError, "磁盘写入失败"):
                self.apply()
        self.assertEqual(existing.read_bytes(), before)
        self.assertFalse((self.target / ".obsidian/plugins").exists())


if __name__ == "__main__":
    unittest.main()
