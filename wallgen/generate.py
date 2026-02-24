import os
from datetime import datetime
from pathlib import Path

from google import genai
from google.genai import types

from .resolution import detect_aspect_ratio


def generate_wallpaper(cfg: dict, theme: str) -> Path:
    output_dir = Path(cfg["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    aspect_ratio = detect_aspect_ratio()
    print(f"Theme: {theme}")
    print(f"Aspect ratio: {aspect_ratio}")

    prompt = (
        f"Generate a high-resolution desktop wallpaper: {theme}. "
        "The image should be vivid, detailed, and suitable as a desktop background "
        "with no text, watermarks, or UI elements."
    )

    client = genai.Client(api_key=cfg["api_key"])
    response = client.models.generate_content(
        model=cfg["model"],
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(aspect_ratio=aspect_ratio),
        ),
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"wallgen_{timestamp}.png"

    for part in response.parts:
        if part.inline_data is not None:
            image = part.as_image()
            image.save(output_path)
            print(f"Saved: {output_path}")
            _cleanup_old(output_dir, cfg["max_stored"])
            return output_path

    raise RuntimeError("Gemini returned no image data. Check your API tier and model.")


def _cleanup_old(output_dir: Path, max_stored: int):
    images = sorted(output_dir.glob("wallgen_*.png"), key=lambda p: p.stat().st_mtime)
    while len(images) > max_stored:
        old = images.pop(0)
        old.unlink()
        print(f"Cleaned up: {old.name}")
