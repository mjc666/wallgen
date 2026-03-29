# wallgen

AI wallpaper generator for KDE Plasma using Google Gemini (including Nano Banana 2) or xAI Grok. Generates unique wallpapers from themed prompts, applies them to your desktop, and can run on a schedule via systemd.

## Requirements

- Python >= 3.10
- KDE Plasma
- API key for [Google Gemini](https://aistudio.google.com/apikey) or [xAI Grok](https://console.x.ai/)

## Installation

```bash
pipx install .
```

## Setup

1. Create the config file:

   ```bash
   wallgen config
   ```

2. Edit `~/.config/wallgen/config.yaml`:
   - Set `provider` to `gemini` or `grok`
   - Add your API key (`api_key` for Gemini, `xai_api_key` for Grok)
   - Or use environment variables: `GOOGLE_API_KEY` / `XAI_API_KEY`

3. Test it:

   ```bash
   wallgen generate
   ```

## Usage

```bash
# Generate a wallpaper (randomly selects from themes in config)
wallgen generate

# Use a custom theme prompt
wallgen generate --theme "sunset over mountains"

# Generate without applying to desktop
wallgen generate --no-apply

# Generate new theme prompts using Gemini AI
wallgen theme-gen "cyberpunk"

# Generate multiple theme prompts at once
wallgen theme-gen "space" --count 5

# Add a specific theme prompt to the rotation
wallgen add-theme "abstract geometric art, bold colors"

# Ultrawide mode: crop, stitch, or stretch (for super-ultrawide displays)
wallgen generate --mode crop
wallgen generate --mode stitch
wallgen generate --mode stretch

# Set an existing image as wallpaper
wallgen set /path/to/image.png

# Show or create config file
wallgen config
```

## Configuration

Located at `~/.config/wallgen/config.yaml`. See [config.example.yaml](config.example.yaml) for all options.

| Setting | Default | Description |
|---|---|---|
| `provider` | `gemini` | Image generation provider (`gemini` or `grok`) |
| `api_key` | `""` | Gemini API key (or `GOOGLE_API_KEY` env var) |
| `xai_api_key` | `""` | Grok API key (or `XAI_API_KEY` env var) |
| `model` | *(auto)* | Model name (defaults to provider's recommended model) |
| `output_dir` | `~/.local/share/wallgen` | Where wallpapers are saved |
| `max_stored` | `20` | Number of recent wallpapers to keep |
| `mode` | `crop` | Ultrawide mode: `crop`, `stitch`, or `stretch` |
| `themes` | *(8 built-in)* | List of prompts to rotate through |

Themes are randomly selected from the `themes` list in your config.

## Ultrawide support

Displays wider than what the AI provider supports (e.g. 5120x1440 / 32:9) are automatically detected. Choose a strategy with `--mode` or set a default in config:

| Mode | Description |
|---|---|
| `crop` | Generate at the widest API ratio, center-crop to fit your display |
| `stitch` | Generate two 16:9 images and place them side-by-side |
| `stretch` | Generate at the widest API ratio and stretch to fit |

For standard displays these modes are ignored and the image is generated at the native aspect ratio.

## Automatic scheduling

Copy the systemd units and enable the timer to generate a new wallpaper 1 minute after boot and every 4 hours:

```bash
cp systemd/wallgen.service systemd/wallgen.timer ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now wallgen.timer
```

Check status:

```bash
systemctl --user status wallgen.timer
journalctl --user -u wallgen.service -f
```
