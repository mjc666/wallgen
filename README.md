# wallgen

AI wallpaper generator for KDE Plasma using Google Gemini. Generates unique wallpapers from themed prompts, applies them to your desktop, and can run on a schedule via systemd.

## Requirements

- Python >= 3.10
- KDE Plasma
- Google Gemini API key

## Installation

```bash
pipx install .
```

## Setup

1. Create the config file:

   ```bash
   wallgen config
   ```

2. Add your Gemini API key to `~/.config/wallgen/config.yaml`, or set the `GOOGLE_API_KEY` environment variable.

3. Test it:

   ```bash
   wallgen generate
   ```

## Usage

```bash
# Generate a wallpaper (rotates through themes automatically)
wallgen generate

# Use a custom theme prompt
wallgen generate --theme "sunset over mountains"

# Generate without applying to desktop
wallgen generate --no-apply

# Set an existing image as wallpaper
wallgen set /path/to/image.png

# Show or create config file
wallgen config
```

## Configuration

Located at `~/.config/wallgen/config.yaml`. See [config.example.yaml](config.example.yaml) for all options.

| Setting | Default | Description |
|---|---|---|
| `api_key` | `""` | Gemini API key (or use `GOOGLE_API_KEY` env var) |
| `model` | `gemini-2.0-flash-exp` | Gemini model for image generation |
| `output_dir` | `~/.local/share/wallgen` | Where wallpapers are saved |
| `max_stored` | `20` | Number of recent wallpapers to keep |
| `themes` | *(8 built-in)* | List of prompts to rotate through |

Themes are cycled sequentially, with rotation state tracked in `~/.config/wallgen/state.json`.

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
