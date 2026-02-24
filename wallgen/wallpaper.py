import subprocess
import sys
from pathlib import Path


def set_wallpaper(image_path: str | Path):
    image_path = Path(image_path).resolve()
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    file_uri = f"file://{image_path}"

    script = (
        "desktops().forEach(d => {"
        "  d.wallpaperPlugin = 'org.kde.image';"
        "  d.currentConfigGroup = Array('Wallpaper', 'org.kde.image', 'General');"
        f"  d.writeConfig('Image', '{file_uri}');"
        "  d.reloadConfig();"
        "});"
    )

    for cmd in ["qdbus6", "qdbus"]:
        try:
            result = subprocess.run(
                [
                    cmd, "org.kde.plasmashell", "/PlasmaShell",
                    "org.kde.PlasmaShell.evaluateScript", script,
                ],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0:
                print(f"Wallpaper applied via {cmd}")
                return
            print(f"{cmd} failed: {result.stderr.strip()}", file=sys.stderr)
        except FileNotFoundError:
            continue
        except subprocess.TimeoutExpired:
            print(f"{cmd} timed out", file=sys.stderr)
            continue

    # Last resort fallback
    try:
        subprocess.run(
            ["plasma-apply-wallpaperimage", str(image_path)],
            check=True, timeout=10,
        )
        print("Wallpaper applied via plasma-apply-wallpaperimage")
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        raise RuntimeError(
            "Could not set wallpaper. No working method found "
            "(tried qdbus6, qdbus, plasma-apply-wallpaperimage)."
        ) from e
