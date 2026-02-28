from wallgen.resolution import get_best_api_ratio

def test_best_ratio_32_9():
    # 32:9 is 3.55
    # Closest should be 4:1 (4.0) rather than 21:9 (2.33)
    ratio = get_best_api_ratio("gemini", 5120, 1440)
    assert ratio == "4:1"

def test_best_ratio_21_9():
    ratio = get_best_api_ratio("gemini", 3440, 1440)
    assert ratio == "21:9"

def test_best_ratio_16_9():
    ratio = get_best_api_ratio("gemini", 1920, 1080)
    assert ratio == "16:9"
