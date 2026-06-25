"""Audio conversion and whisper.cpp invocation."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

# whisper.cpp ships the binary under different names depending on version/distro.
_WHISPER_BINARIES = ("whisper-cli", "whisper-cpp", "main")

# CLI output flag + produced file extension, per format.
_FORMAT_FLAGS = {
    "txt": ("-otxt", "txt"),
    "srt": ("-osrt", "srt"),
    "vtt": ("-ovtt", "vtt"),
    "json": ("-oj", "json"),
}


class DependencyError(RuntimeError):
    """A required external binary (ffmpeg / whisper.cpp) is missing."""


@dataclass
class TranscribeResult:
    text: str
    fmt: str


def find_ffmpeg() -> str:
    exe = shutil.which("ffmpeg")
    if not exe:
        raise DependencyError(
            "ffmpeg not found. Install it (macOS: `brew install ffmpeg`, "
            "Debian/Ubuntu: `sudo apt install ffmpeg`)."
        )
    return exe


def find_whisper() -> str:
    for name in _WHISPER_BINARIES:
        exe = shutil.which(name)
        if exe:
            return exe
    raise DependencyError(
        "whisper.cpp not found. Install it (macOS: `brew install whisper-cpp`) "
        "so that `whisper-cli` is on your PATH."
    )


def to_wav(src: Path, dst: Path, *, ffmpeg: str | None = None) -> None:
    """Convert any audio file to 16 kHz mono PCM WAV (what whisper.cpp expects)."""
    ffmpeg = ffmpeg or find_ffmpeg()
    cmd = [ffmpeg, "-y", "-i", str(src), "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", str(dst)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed to convert {src}:\n{proc.stderr.strip()}")


def transcribe(
    src: Path,
    model: Path,
    *,
    language: str = "auto",
    fmt: str = "txt",
    translate: bool = False,
    threads: int | None = None,
    quiet: bool = False,
) -> TranscribeResult:
    """Transcribe ``src`` and return the result text in the requested format."""
    if fmt not in _FORMAT_FLAGS:
        raise ValueError(f"unknown format {fmt!r}. Choose from: {', '.join(_FORMAT_FLAGS)}")

    ffmpeg = find_ffmpeg()
    whisper = find_whisper()
    out_flag, out_ext = _FORMAT_FLAGS[fmt]

    with tempfile.TemporaryDirectory(prefix="voxscribe-") as tmp:
        tmpdir = Path(tmp)
        wav = tmpdir / "audio.wav"
        to_wav(src, wav, ffmpeg=ffmpeg)

        out_prefix = tmpdir / "out"
        cmd = [
            whisper,
            "-m", str(model),
            "-f", str(wav),
            "-l", language,
            out_flag,
            "-of", str(out_prefix),
        ]
        if translate:
            cmd.append("-tr")
        if threads:
            cmd += ["-t", str(threads)]

        proc = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL if quiet else None,
            stderr=subprocess.DEVNULL if quiet else None,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"whisper.cpp exited with code {proc.returncode}")

        produced = out_prefix.with_suffix("." + out_ext)
        if not produced.exists():
            raise RuntimeError(f"expected output {produced} was not produced by whisper.cpp")
        text = produced.read_text(encoding="utf-8")

    if fmt == "txt":
        text = text.strip() + "\n"
    return TranscribeResult(text=text, fmt=fmt)
