import yaml
from wallgen.config import DEFAULT_MODELS, add_theme, CONFIG_PATH, DEFAULT_CONFIG


def test_default_gemini_model():
    assert DEFAULT_MODELS["gemini"] == "gemini-3.1-flash-image-preview"


def test_grok_model():
    assert DEFAULT_MODELS["grok"] == "grok-imagine-image"


def test_add_theme_avoids_duplicates(tmp_path):
    # Use a temporary config path for testing
    import wallgen.config
    original_path = wallgen.config.CONFIG_PATH
    test_cfg_path = tmp_path / "config.yaml"
    wallgen.config.CONFIG_PATH = test_cfg_path
    
    try:
        # Create initial config
        initial_themes = ["theme1", "theme2"]
        test_cfg_path.write_text(yaml.dump({"themes": initial_themes}))
        
        # Add a new theme
        add_theme("theme3")
        with open(test_cfg_path) as f:
            cfg = yaml.safe_load(f)
            assert "theme3" in cfg["themes"]
            assert len(cfg["themes"]) == 3
            
        # Add a duplicate theme
        add_theme("theme1")
        with open(test_cfg_path) as f:
            cfg = yaml.safe_load(f)
            assert len(cfg["themes"]) == 3
            
    finally:
        wallgen.config.CONFIG_PATH = original_path
