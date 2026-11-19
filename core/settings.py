"""Configurações persistentes do NEXUS."""

import json
import os
from pathlib import Path

APP_VERSION = "1.0.0"
APP_NAME = "NEXUS"

CONFIG_DIR = Path(os.getenv("APPDATA", Path.home())) / "NEXUS"
CONFIG_FILE = CONFIG_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "theme": "cyan",
    "language": "pt-BR",
    "start_with_windows": False,
    "automatic_updates": False,
}


def load_settings():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    if not CONFIG_FILE.exists():
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()

    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        settings = DEFAULT_SETTINGS.copy()
        settings.update(data)

        if settings["theme"] not in ("cyan", "violet"):
            settings["theme"] = "cyan"

        return settings

    except (OSError, json.JSONDecodeError):
        return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    safe_settings = DEFAULT_SETTINGS.copy()
    safe_settings.update(settings)

    if safe_settings["theme"] not in ("cyan", "violet"):
        raise ValueError("Tema inválido.")

    temporary_file = CONFIG_FILE.with_suffix(".tmp")

    with temporary_file.open("w", encoding="utf-8") as file:
        json.dump(safe_settings, file, indent=4, ensure_ascii=False)

    temporary_file.replace(CONFIG_FILE)

    return safe_settings
