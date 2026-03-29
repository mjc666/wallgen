from unittest.mock import MagicMock, patch
from pathlib import Path
from wallgen.generate import _generate_gemini, generate_theme


@patch("google.genai.Client")
def test_generate_theme(mock_client_class):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client

    mock_response = MagicMock()
    mock_response.text = "A futuristic cyberpunk city with neon lights and wet pavement."
    mock_client.models.generate_content.return_value = mock_response

    cfg = {"api_key": "test_key"}
    topic = "cyberpunk"

    result = generate_theme(cfg, topic)

    assert result == ["A futuristic cyberpunk city with neon lights and wet pavement."]
    args, kwargs = mock_client.models.generate_content.call_args
    assert kwargs["model"] == "gemini-3-flash-preview"

    assert topic in kwargs["contents"][0]

@patch("google.genai.Client")
def test_generate_multiple_themes(mock_client_class):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.text = "Theme 1\nTheme 2\nTheme 3"
    mock_client.models.generate_content.return_value = mock_response
    
    cfg = {"api_key": "test_key"}
    topic = "space"
    
    results = generate_theme(cfg, topic, count=3)
    
    assert len(results) == 3
    assert results[0] == "Theme 1"
    assert results[1] == "Theme 2"
    assert results[2] == "Theme 3"
    args, kwargs = mock_client.models.generate_content.call_args
    assert "3" in kwargs["contents"][0]


@patch("google.genai.Client")
def test_generate_gemini_4k_support(mock_client_class):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    cfg = {
        "api_key": "test_key",
        "model": "gemini-3.1-flash-image-preview",
    }
    prompt = "test prompt"
    aspect_ratio = "16:9"
    output_path = Path("test.png")
    
    # We need to mock the types module too
    with patch("google.genai.types") as mock_types:
        # Mock the behavior of generate_content
        mock_response = MagicMock()
        mock_response.parts = []
        mock_client.models.generate_content.return_value = mock_response
        
        try:
            _generate_gemini(cfg, prompt, aspect_ratio, output_path)
        except RuntimeError:
            # Expected because we didn't mock the response parts correctly for a full run
            pass
        
        # Check if generate_content was called with the right config
        args, kwargs = mock_client.models.generate_content.call_args
        config = kwargs.get("config")
        
        # Check if image_size was set to 4K
        # Since we mocked types.ImageConfig, we need to check how it was constructed
        mock_types.ImageConfig.assert_called_with(aspect_ratio=aspect_ratio)
        # Note: image_size is set after construction in generate.py
        # image_config.image_size = "4K"
        
        # We can check the instance that was passed to GenerateContentConfig
        image_config = mock_types.ImageConfig.return_value
        assert image_config.image_size == "4K"

@patch("google.genai.Client")
def test_generate_gemini_no_4k_for_old_models(mock_client_class):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    cfg = {
        "api_key": "test_key",
        "model": "gemini-2.5-flash-image",
    }
    
    with patch("google.genai.types") as mock_types:
        mock_response = MagicMock()
        mock_response.parts = []
        mock_client.models.generate_content.return_value = mock_response
        
        try:
            _generate_gemini(cfg, "prompt", "16:9", Path("test.png"))
        except RuntimeError:
            pass
        
        image_config = mock_types.ImageConfig.return_value
        # Should not have image_size set (or at least not to 4K)
        assert not hasattr(image_config, "image_size") or image_config.image_size != "4K"
