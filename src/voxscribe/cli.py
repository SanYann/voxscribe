"""Command-line interface for voxscribe."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .core import DependencyError, transcribe
from .models import MODELS, resolve_model

_EXT_FOR_FORMAT = {"txt": ".txt", "srt": ".srt", "vtt": ".vtt", "json": ".json"}


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="voxscribe",
        description="Transcribe voice notes (WhatsApp .opus, .mp3, .m4a, ...) locally with whisper.cpp.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  voxscribe note.opus\n"
            "  voxscribe note.opus -l fr -m medium\n"
            "  voxscribe note.opus -f srt -o note.srt\n"
            "  voxscribe *.m4a -l en --translate\n"
            "\nAvailable models:\n"
            + "\n".join(f"  {name:<16} {desc}" for name, desc in MODELS.items())
        ),
    )
    p.add_argument("audio", nargs="+", type=Path, help="audio file(s) to transcribe")
    p.add_argument("-l", "--language", default="auto",
                   help="language code (e.g. fr, en) or 'auto' to detect (default: auto)")
    p.add_argument("-m", "--model", default="base",
                   help="model name or path to a .bin file (default: base)")
    p.add_argument("-f", "--format", default="txt", choices=list(_EXT_FOR_FORMAT),
                   help="output format (default: txt)")
    p.add_argument("-o", "--output", type=Path,
                   help="write to this file instead of stdout (single input only)")
    p.add_argument("--translate", action="store_true",
                   help="translate the speech to English")
    p.add_argument("-t", "--threads", type=int, default=None, help="number of threads")
    p.add_argument("-q", "--quiet", action="store_true", help="suppress whisper.cpp logs")
    p.add_argument("-V", "--version", action="version", version=f"voxscribe {__version__}")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.output and len(args.audio) > 1:
        print("voxscribe: --output cannot be used with multiple input files", file=sys.stderr)
        return 2

    try:
        model = resolve_model(args.model)
    except (ValueError, FileNotFoundError) as exc:
        print(f"voxscribe: {exc}", file=sys.stderr)
        return 2

    rc = 0
    for audio in args.audio:
        if not audio.exists():
            print(f"voxscribe: no such file: {audio}", file=sys.stderr)
            rc = 1
            continue
        try:
            result = transcribe(
                audio,
                model,
                language=args.language,
                fmt=args.format,
                translate=args.translate,
                threads=args.threads,
                quiet=args.quiet,
            )
        except DependencyError as exc:
            print(f"voxscribe: {exc}", file=sys.stderr)
            return 3
        except RuntimeError as exc:
            print(f"voxscribe: failed on {audio}: {exc}", file=sys.stderr)
            rc = 1
            continue

        if args.output:
            args.output.write_text(result.text, encoding="utf-8")
            print(f"voxscribe: wrote {args.output}", file=sys.stderr)
        elif len(args.audio) > 1:
            dest = audio.with_suffix(_EXT_FOR_FORMAT[args.format])
            dest.write_text(result.text, encoding="utf-8")
            print(f"voxscribe: wrote {dest}", file=sys.stderr)
        else:
            sys.stdout.write(result.text)

    return rc


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
