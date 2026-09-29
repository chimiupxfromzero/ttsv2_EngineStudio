import os
import json
from pathlib import Path


CONFIG_FILE = "config.json"

DEFAULTS = {
    "theme": "System",
    "output_dir": str(Path.cwd() / "output"),
    "language": "es",
    "accent": "es-MX",
    "mode": "preset",
    "speaker": "Luis Moray",
    "reference_audio": "",
    "window_geometry": "800x700",
}


def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                user_config = json.load(f)
                return {**DEFAULTS, **user_config}
        except (json.JSONDecodeError, OSError):
            pass
    return DEFAULTS.copy()


def save_config(config: dict) -> None:
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except OSError:
        pass


def get_output_dir(config: dict) -> str:
    output_dir = config.get("output_dir", DEFAULTS["output_dir"])
    os.makedirs(output_dir, exist_ok=True)
    return output_dir