from wallgen.config import DEFAULT_MODELS

def test_default_gemini_model():
    assert DEFAULT_MODELS["gemini"] == "gemini-3.1-flash-image-preview"

def test_grok_model():
    assert DEFAULT_MODELS["grok"] == "grok-imagine-image"
