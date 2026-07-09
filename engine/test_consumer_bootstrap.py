"""Tests for consumer bootstrap (Janice edition paths)."""

import os
import tempfile
from pathlib import Path
from unittest import mock

import yaml


def test_runtime_config_paths():
    with tempfile.TemporaryDirectory() as tmp:
        data_dir = Path(tmp)
        template = Path(__file__).parent / "assistant_config.consumer.yml"
        assert template.exists()

        with mock.patch("modules.consumer_bootstrap._template_path", return_value=template):
            with mock.patch("modules.consumer_bootstrap.consumer_data_dir", return_value=data_dir):
                from modules.consumer_bootstrap import _write_runtime_config

                dest = data_dir / "assistant_config.runtime.yml"
                from modules.consumer_bootstrap import save_user_secrets

                save_user_secrets(
                    name="TestUser",
                    groq_key=None,
                    assistant_name="Alex",
                )
                dest = data_dir / "assistant_config.runtime.yml"
                cfg = yaml.safe_load(dest.read_text(encoding="utf-8"))
                assert cfg["memory"]["backend"] == "sqlite"
                assert cfg["memory"]["embedding"]["backend"] == "hash"
                assert cfg["base_assistant"]["assistant_name"] == "Alex"
                assert cfg["base_assistant"]["human_companion_name"] == "TestUser"
                assert str(data_dir) in cfg["memory"]["sqlite_path"]
                assert str(data_dir / "chroma") in cfg["memory"]["chroma"]["persist_directory"]


if __name__ == "__main__":
    test_runtime_config_paths()
    print("[SUCCESS] Consumer bootstrap tests passed")
