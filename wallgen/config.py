import json
import os
import random
from pathlib import Path

import yaml

CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "wallgen"
CONFIG_PATH = CONFIG_DIR / "config.yaml"
STATE_PATH = CONFIG_DIR / "state.json"

DEFAULT_MODELS = {
    "gemini": "gemini-3.1-flash-image-preview",  # Also known as Nano Banana 2
    "grok": "grok-imagine-image",
}

DEFAULT_CONFIG = {
    "provider": "gemini",
    "api_key": "",
    "xai_api_key": "",
    "model": "",
    "output_dir": str(
        Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
        / "wallgen"
    ),
    "max_stored": 20,
    "mode": "crop",
    "themes": [
        "vast alien landscape with bioluminescent flora, cinematic lighting",
        "cyberpunk cityscape at night, neon reflections on wet streets",
        "serene Japanese garden in autumn, soft morning light",
        "abstract geometric art, bold colors, minimalist composition",
        "underwater coral reef teeming with life, sunlight filtering through water",
        "snow-capped mountain range at golden hour, dramatic clouds",
        "futuristic space station orbiting a gas giant, stars in background",
        "misty enchanted forest with ancient trees and glowing mushrooms",
    ],
}


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Config not found at {CONFIG_PATH}\n"
            f"Run 'wallgen config' to create a default config."
        )
    with open(CONFIG_PATH) as f:
        user = yaml.safe_load(f) or {}

    cfg = {**DEFAULT_CONFIG, **user}
    cfg["output_dir"] = str(Path(cfg["output_dir"]).expanduser())

    provider = cfg["provider"]
    if provider not in DEFAULT_MODELS:
        raise ValueError(f"Unknown provider '{provider}'. Use 'gemini' or 'grok'.")

    if not cfg["model"]:
        cfg["model"] = DEFAULT_MODELS[provider]

    if provider == "gemini":
        api_key = cfg["api_key"] or os.environ.get("GOOGLE_API_KEY", "")
        if not api_key:
            raise ValueError(
                "No Gemini API key configured. Set 'api_key' in config.yaml "
                "or export GOOGLE_API_KEY."
            )
        cfg["api_key"] = api_key
    elif provider == "grok":
        xai_key = cfg["xai_api_key"] or os.environ.get("XAI_API_KEY", "")
        if not xai_key:
            raise ValueError(
                "No xAI API key configured. Set 'xai_api_key' in config.yaml "
                "or export XAI_API_KEY."
            )
        cfg["xai_api_key"] = xai_key

    return cfg


def create_default_config():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if CONFIG_PATH.exists():
        print(f"Config already exists: {CONFIG_PATH}")
        return
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False, sort_keys=False)
    print(f"Created default config: {CONFIG_PATH}")
    print("Edit it to add your API key.")


def load_state() -> dict:
    if STATE_PATH.exists():
        with open(STATE_PATH) as f:
            return json.load(f)
    return {"theme_index": 0}


def save_state(state: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f)


def add_themes(themes: list[str]):
    """Add multiple themes to the config file at once."""
    if not themes:
        return

    user_cfg = {}
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            user_cfg = yaml.safe_load(f) or {}
    
    if "themes" not in user_cfg:
        user_cfg["themes"] = list(DEFAULT_CONFIG["themes"])
    
    added_count = 0
    for theme in themes:
        if theme in user_cfg["themes"]:
            print(f" - Already exists: {theme}")
            continue
        
        user_cfg["themes"].append(theme)
        print(f" + Added: {theme}")
        added_count += 1
    
    if added_count > 0:
        with open(CONFIG_PATH, "w") as f:
            yaml.dump(user_cfg, f, default_flow_style=False, sort_keys=False)


def add_theme(theme: str):
    add_themes([theme])


def next_theme(cfg: dict) -> str:
    themes = cfg["themes"]
    if not themes:
        return ""
    return random.choice(themes)
