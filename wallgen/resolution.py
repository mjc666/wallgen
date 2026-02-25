import subprocess
import re

# Supported aspect ratios per provider (landscape only, widest first)
GEMINI_RATIOS = ["21:9", "16:9", "3:2", "4:3", "5:4", "1:1"]
GROK_RATIOS = ["20:9", "2:1", "16:9", "3:2", "4:3", "1:1"]

FALLBACK_WIDTH = 1920
FALLBACK_HEIGHT = 1080


def _ratio_value(label: str) -> float:
    w, h = label.split(":")
    return float(w) / float(h)


def detect_resolution() -> tuple[int, int]:
    for func in [_try_xrandr, _try_kscreen_doctor]:
        result = func()
        if result:
            return result
    return FALLBACK_WIDTH, FALLBACK_HEIGHT


def detect_aspect_ratio(provider: str) -> str:
    w, h = detect_resolution()
    return get_best_api_ratio(provider, w, h)


def get_best_api_ratio(provider: str, w: int, h: int) -> str:
    """Return the closest supported API aspect ratio for the given resolution."""
    ratios = GEMINI_RATIOS if provider == "gemini" else GROK_RATIOS
    target = w / h

    best = ratios[0]
    best_dist = float("inf")
    for label in ratios:
        dist = abs(_ratio_value(label) - target)
        if dist < best_dist:
            best_dist = dist
            best = label
    return best


def needs_ultrawide_processing(provider: str, w: int, h: int) -> bool:
    """Return True if the display is wider than the widest ratio the API supports."""
    ratios = GEMINI_RATIOS if provider == "gemini" else GROK_RATIOS
    widest = _ratio_value(ratios[0])
    return (w / h) > widest


def _try_xrandr() -> tuple[int, int] | None:
    try:
        out = subprocess.run(
            ["xrandr", "--current"],
            capture_output=True, text=True, timeout=5,
        ).stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None

    for line in out.splitlines():
        match = re.search(r"(\d+)x(\d+).*\*", line)
        if match:
            return int(match.group(1)), int(match.group(2))
    return None


def _try_kscreen_doctor() -> tuple[int, int] | None:
    try:
        out = subprocess.run(
            ["kscreen-doctor", "--outputs"],
            capture_output=True, text=True, timeout=5,
        ).stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None

    for line in out.splitlines():
        match = re.search(r"(\d+)x(\d+)@", line)
        if match:
            return int(match.group(1)), int(match.group(2))
    return None
