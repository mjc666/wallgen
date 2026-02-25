import argparse
import sys

from .config import create_default_config, load_config, next_theme, CONFIG_PATH
from .generate import generate_wallpaper
from .wallpaper import set_wallpaper


def cmd_generate(args):
    cfg = load_config()
    if args.mode:
        cfg["mode"] = args.mode
    theme = args.theme or next_theme(cfg)
    path = generate_wallpaper(cfg, theme)
    if not args.no_apply:
        set_wallpaper(path)


def cmd_set(args):
    set_wallpaper(args.path)


def cmd_config(args):
    if CONFIG_PATH.exists():
        print(f"Config location: {CONFIG_PATH}")
        with open(CONFIG_PATH) as f:
            print(f.read())
    else:
        create_default_config()


def main():
    parser = argparse.ArgumentParser(
        prog="wallgen",
        description="AI wallpaper generator for KDE Plasma",
    )
    sub = parser.add_subparsers(dest="command")

    gen = sub.add_parser("generate", help="Generate and apply a new wallpaper")
    gen.add_argument("--theme", help="Override theme prompt")
    gen.add_argument(
        "--no-apply", action="store_true",
        help="Generate only, don't set as wallpaper",
    )
    gen.add_argument(
        "--mode", choices=["crop", "stitch", "stretch"],
        help="Ultrawide mode: crop (center-crop to fit), "
             "stitch (two images side-by-side), stretch (stretch to fit)",
    )

    setp = sub.add_parser("set", help="Set an existing image as wallpaper")
    setp.add_argument("path", help="Path to image file")

    sub.add_parser("config", help="Show or create config file")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    try:
        {"generate": cmd_generate, "set": cmd_set, "config": cmd_config}[
            args.command
        ](args)
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
