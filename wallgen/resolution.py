import subprocess
import re

# Gemini-supported aspect ratios mapped to common resolutions
ASPECT_RATIOS = {
    (16, 9): "16:9",
    (16, 10): "16:9",   # closest supported
    (21, 9): "16:9",    # ultrawide → closest supported
    (4, 3): "4:3",
    (3, 2): "3:2",
    (1, 1): "1:1",
}

FALLBACK_WIDTH = 1920
FALLBACK_HEIGHT = 1080


def detect_resolution() -> tuple[int, int]:
    for func in [_try_xrandr, _try_kscreen_doctor]:
        result = func()
        if result:
            return result
    return FALLBACK_WIDTH, FALLBACK_HEIGHT


def detect_aspect_ratio() -> str:
    w, h = detect_resolution()
    return _closest_aspect_ratio(w, h)


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


def _closest_aspect_ratio(w: int, h: int) -> str:
    from math import gcd
    g = gcd(w, h)
    rw, rh = w // g, h // g

    if (rw, rh) in ASPECT_RATIOS:
        return ASPECT_RATIOS[(rw, rh)]

    # Find closest by ratio distance
    target = w / h
    best = "16:9"
    best_dist = float("inf")
    for (aw, ah), label in ASPECT_RATIOS.items():
        dist = abs(aw / ah - target)
        if dist < best_dist:
            best_dist = dist
            best = label
    return best
