from datetime import datetime
from pathlib import Path

from PIL import Image

from .resolution import (
    detect_aspect_ratio,
    detect_resolution,
    needs_ultrawide_processing,
)


def generate_theme(cfg: dict, topic: str, count: int = 1) -> list[str]:
    from google import genai

    client = genai.Client(api_key=cfg["api_key"])
    
    # Use a standard text model for prompt generation
    model_id = "gemini-3-flash-preview" 
    
    if count > 1:
        prompt = (
            f"Generate {count} unique, single-sentence descriptive prompts for high-quality desktop wallpapers "
            f"based on the theme '{topic}'. Each description should be evocative, detailed, "
            f"and focus on visual elements, lighting, and mood. "
            f"Return them as a simple list with one description per line. "
            f"Do not include any numbering, introductory text, or quotes."
        )
    else:
        prompt = (
            f"Generate a single-sentence descriptive prompt for a high-quality desktop wallpaper "
            f"based on the theme '{topic}'. The description should be evocative, detailed, "
            f"and focus on visual elements, lighting, and mood. "
            f"Do not include any introductory text or quotes, just the description itself."
        )

    response = client.models.generate_content(
        model=model_id,
        contents=[prompt],
    )
    
    lines = [line.strip().strip('"').strip("'").strip("- ") for line in response.text.split("\n") if line.strip()]
    return lines[:count]


def generate_wallpaper(cfg: dict, theme: str) -> Path:
    output_dir = Path(cfg["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    provider = cfg["provider"]
    target_w, target_h = detect_resolution()
    api_ratio = detect_aspect_ratio(provider)
    mode = cfg.get("mode", "crop")
    ultrawide = needs_ultrawide_processing(provider, target_w, target_h)

    print(f"Provider: {provider}")
    print(f"Theme: {theme}")
    print(f"Display: {target_w}x{target_h}")
    print(f"API aspect ratio: {api_ratio}")
    if ultrawide:
        print(f"Ultrawide mode: {mode}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"wallgen_{timestamp}.png"

    if ultrawide and mode == "stitch":
        _generate_stitched(cfg, provider, theme, target_w, target_h, output_path)
    else:
        prompt = _build_prompt(theme, api_ratio)
        _generate_single(cfg, provider, prompt, api_ratio, output_path)
        if ultrawide:
            _postprocess(output_path, mode, target_w, target_h)

    print(f"Saved: {output_path}")
    _cleanup_old(output_dir, cfg["max_stored"])
    return output_path


def _build_prompt(theme: str, aspect_ratio: str = "16:9") -> str:
    # Enhance prompt for ultra-wide panoramic shots
    wide_suffix = ""
    w, h = map(float, aspect_ratio.split(":"))
    if w / h > 2.5:  # Wider than 21:9
        wide_suffix = "panoramic, wide-angle cinematic view, "

    return (
        f"Generate a high-resolution desktop wallpaper: {wide_suffix}{theme}. "
        "The image should be vivid, detailed, and suitable as a desktop background "
        "with no text, watermarks, or UI elements."
    )


def _generate_single(cfg: dict, provider: str, prompt: str, aspect_ratio: str, output_path: Path):
    if provider == "grok":
        _generate_grok(cfg, prompt, aspect_ratio, output_path)
    else:
        _generate_gemini(cfg, prompt, aspect_ratio, output_path)


def _generate_stitched(cfg: dict, provider: str, theme: str, target_w: int, target_h: int, output_path: Path):
    """Generate two 16:9 images and stitch them side-by-side."""
    panel_w = target_w // 2
    prompt_left = _build_prompt(theme + ", left half of a panoramic scene", "16:9")
    prompt_right = _build_prompt(theme + ", right half of a panoramic scene", "16:9")

    left_path = output_path.with_suffix(".left.png")
    right_path = output_path.with_suffix(".right.png")

    try:
        _generate_single(cfg, provider, prompt_left, "16:9", left_path)
        _generate_single(cfg, provider, prompt_right, "16:9", right_path)

        left = Image.open(left_path).resize((panel_w, target_h), Image.LANCZOS)
        right = Image.open(right_path).resize((panel_w, target_h), Image.LANCZOS)

        canvas = Image.new("RGB", (target_w, target_h))
        canvas.paste(left, (0, 0))
        canvas.paste(right, (panel_w, 0))
        canvas.save(output_path)
    finally:
        left_path.unlink(missing_ok=True)
        right_path.unlink(missing_ok=True)


def _postprocess(output_path: Path, mode: str, target_w: int, target_h: int):
    """Crop or stretch generated image to target resolution."""
    img = Image.open(output_path)

    if mode == "crop":
        # Scale to match target width, then center-crop height
        scale = target_w / img.width
        scaled_h = round(img.height * scale)
        img = img.resize((target_w, scaled_h), Image.LANCZOS)
        if scaled_h > target_h:
            top = (scaled_h - target_h) // 2
            img = img.crop((0, top, target_w, top + target_h))
        elif scaled_h < target_h:
            # Rare: image is already wider than target ratio, pad vertically
            canvas = Image.new("RGB", (target_w, target_h))
            offset = (target_h - scaled_h) // 2
            canvas.paste(img, (0, offset))
            img = canvas
    elif mode == "stretch":
        img = img.resize((target_w, target_h), Image.LANCZOS)

    img.save(output_path)


def _generate_gemini(cfg: dict, prompt: str, aspect_ratio: str, output_path: Path):
    from google import genai
    from google.genai import types

    image_config = types.ImageConfig(aspect_ratio=aspect_ratio)
    # Enable 4K resolution for Nano Banana 2 / Gemini 3.1 models
    if "3.1" in cfg["model"] or "nano-banana" in cfg["model"]:
        image_config.image_size = "4K"

    client = genai.Client(api_key=cfg["api_key"])
    response = client.models.generate_content(
        model=cfg["model"],
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=image_config,
        ),
    )

    if response.usage_metadata:
        usage = response.usage_metadata
        print(f"Tokens: {usage.prompt_token_count} (prompt) + {usage.candidates_token_count} (candidates) = {usage.total_token_count} total")

    for part in response.parts:
        if part.inline_data is not None:
            image = part.as_image()
            image.save(output_path)
            return

    raise RuntimeError("Gemini returned no image data. Check your API tier and model.")


def _generate_grok(cfg: dict, prompt: str, aspect_ratio: str, output_path: Path):
    import xai_sdk

    client = xai_sdk.Client(api_key=cfg["xai_api_key"])
    response = client.image.sample(
        prompt=prompt,
        model=cfg["model"],
        aspect_ratio=aspect_ratio,
        resolution="2k",
    )

    with open(output_path, "wb") as f:
        f.write(response.image)


def _cleanup_old(output_dir: Path, max_stored: int):
    images = sorted(output_dir.glob("wallgen_*.png"), key=lambda p: p.stat().st_mtime)
    while len(images) > max_stored:
        old = images.pop(0)
        old.unlink()
        print(f"Cleaned up: {old.name}")
