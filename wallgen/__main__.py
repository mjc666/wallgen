import argparse
import sys

from .config import (
    create_default_config,
    load_config,
    next_theme,
    CONFIG_PATH,
    add_theme,
    add_themes,
)
from .generate import generate_wallpaper, generate_theme
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


def cmd_add_theme(args):
    add_theme(args.theme)


def cmd_theme_gen(args):
    cfg = load_config()
    count = args.count or 1
    print(f"Generating {count} theme(s) for '{args.topic}'...")
    themes = generate_theme(cfg, args.topic, count)
    add_themes(themes)


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

    add = sub.add_parser("add-theme", help="Add a new theme prompt to config")
    add.add_argument("theme", help="Theme prompt to add")

    tgen = sub.add_parser("theme-gen", help="Generate a new theme prompt using Gemini AI")
    tgen.add_argument("topic", help="General topic for the theme (e.g. space, nature)")
    tgen.add_argument("--count", "-c", type=int, default=1, help="Number of themes to generate")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    try:
        commands = {
            "generate": cmd_generate,
            "set": cmd_set,
            "config": cmd_config,
            "add-theme": cmd_add_theme,
            "theme-gen": cmd_theme_gen,
        }
        commands[args.command](args)
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
