import json
from pathlib import Path

from platformdirs import user_cache_dir, user_config_dir, user_music_dir

APP_NAME = "dlmusic"
APP_AUTHOR = "dlmusic"

DEFAULT_CONFIG = {
    "music_dir": str(Path(user_music_dir()) / "Dilan"),
    "format": "m4a",
    "bitrate": "auto",
    "jobs": 4,
    "threads": 4,
    "engine": "auto",
    "retries": 5,
    "lyrics": True,
    "cookies_browser": "",
    "cookie_file": "",
    "use_archive": True,
    "language": "es",
    "theme": "system",
    "structure": "artist_title" # artist_title, flat, artist_album
}

def get_config_dir() -> Path:
    d = Path(user_config_dir(APP_NAME, APP_AUTHOR))
    d.mkdir(parents=True, exist_ok=True)
    return d

def get_cache_dir() -> Path:
    d = Path(user_cache_dir(APP_NAME, APP_AUTHOR))
    d.mkdir(parents=True, exist_ok=True)
    return d

def get_config_path() -> Path:
    return get_config_dir() / "config.json"

def load_config() -> dict:
    path = get_config_path()
    cfg = DEFAULT_CONFIG.copy()
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                cfg.update(data)
        except Exception as e:
            print(f"Error loading config: {e}")
    return cfg

def save_config(cfg: dict) -> None:
    path = get_config_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving config: {e}")
