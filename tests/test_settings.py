"""Tests for jarvis.settings."""

import pytest

from jarvis import settings


def test_default_target_is_claude(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "_SETTINGS_FILE", tmp_path / "settings.json")

    assert settings.get_target() == "claude"
    assert settings.get_target_label() == "Claude Code"
    assert settings.get_target_command() == "/jarvis"


def test_set_codex_target(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "_SETTINGS_FILE", tmp_path / "settings.json")

    assert settings.set_target("codex") == "codex"
    assert settings.get_target() == "codex"
    assert settings.get_target_label() == "Codex"
    assert settings.get_target_command() == "$jarvis"


def test_target_aliases(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "_SETTINGS_FILE", tmp_path / "settings.json")

    assert settings.set_target("Claude Code") == "claude"
    assert settings.set_target("cloud") == "claude"


def test_invalid_target_raises():
    with pytest.raises(ValueError):
        settings.normalize_target("vim")
