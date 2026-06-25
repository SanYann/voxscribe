"""MCP server exposing voxscribe as a tool for Claude (Desktop, Code, …).

Run with ``voxscribe-mcp`` (stdio transport). Requires the ``mcp`` extra:

    pip install "voxscribe[mcp]"
"""

from __future__ import annotations

from pathlib import Path

from .core import DependencyError, transcribe as _transcribe
from .models import MODELS, resolve_model

_FORMATS = ("txt", "srt", "vtt", "json")


def transcribe_file(
    path: str,
    language: str = "auto",
    model: str = "base",
    fmt: str = "txt",
    translate: bool = False,
) -> str:
    """Core logic, independent of MCP — kept importable for tests."""
    audio = Path(path).expanduser()
    if not audio.exists():
        raise ValueError(f"no such file: {audio}")
    if fmt not in _FORMATS:
        raise ValueError(f"unknown format {fmt!r}; choose from {', '.join(_FORMATS)}")
    resolved = resolve_model(model)
    result = _transcribe(audio, resolved, language=language, fmt=fmt, translate=translate, quiet=True)
    return result.text


def build_server():
    """Construct the FastMCP server, importing ``mcp`` lazily."""
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:  # pragma: no cover - depends on optional extra
        raise SystemExit(
            "voxscribe-mcp requires the 'mcp' package. Install it with:\n"
            '    pip install "voxscribe[mcp]"'
        ) from exc

    mcp = FastMCP("voxscribe")

    @mcp.tool()
    def transcribe(
        path: str,
        language: str = "auto",
        model: str = "base",
        format: str = "txt",
        translate: bool = False,
    ) -> str:
        """Transcribe a local audio file (WhatsApp .opus, .mp3, .m4a, .ogg, .wav, …).

        Runs entirely offline via whisper.cpp — the audio never leaves the machine.

        Args:
            path: Absolute path to the audio file on this machine.
            language: Language code such as 'fr' or 'en', or 'auto' to detect.
            model: Whisper model — one of tiny, base, small, medium, large-v3,
                large-v3-turbo (downloaded on first use). Bigger = more accurate, slower.
            format: Output format — 'txt' (default), 'srt', 'vtt', or 'json'.
            translate: If true, translate the speech into English.

        Returns:
            The transcription in the requested format.
        """
        try:
            return transcribe_file(path, language=language, model=model, fmt=format, translate=translate)
        except DependencyError as exc:
            raise RuntimeError(str(exc)) from exc

    @mcp.tool()
    def list_models() -> dict:
        """List the available whisper models and their size / quality trade-offs."""
        return dict(MODELS)

    return mcp


def main() -> None:
    build_server().run()


if __name__ == "__main__":  # pragma: no cover
    main()
