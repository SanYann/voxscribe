"""Whisper.cpp GGML model catalog and download helpers."""

from __future__ import annotations

import os
import shutil
import sys
import urllib.request
from pathlib import Path

_HF_BASE = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main"

# name -> short description (approx. download size)
MODELS: dict[str, str] = {
    "tiny": "~75 MB · fastest, lowest quality",
    "base": "~142 MB · fast, decent quality (good default)",
    "small": "~466 MB · slower, better quality",
    "medium": "~1.5 GB · slow, high quality",
    "large-v3": "~3.1 GB · slowest, best quality",
    "large-v3-turbo": "~1.6 GB · fast + near-best quality (great for long notes)",
}


def cache_dir() -> Path:
    """Directory where downloaded models live (override with VOXSCRIBE_HOME)."""
    base = os.environ.get("VOXSCRIBE_HOME")
    if base:
        root = Path(base).expanduser()
    else:
        root = Path(os.environ.get("XDG_CACHE_HOME", "~/.cache")).expanduser() / "voxscribe"
    models = root / "models"
    models.mkdir(parents=True, exist_ok=True)
    return models


def resolve_model(model: str, *, allow_download: bool = True) -> Path:
    """Resolve a model name (e.g. ``base``) or path to a local ``.bin`` file.

    Downloads the GGML weights into the cache on first use unless they already
    exist locally.
    """
    # An explicit path to an existing file wins.
    p = Path(model).expanduser()
    if p.suffix == ".bin" and p.exists():
        return p

    if model not in MODELS:
        known = ", ".join(MODELS)
        raise ValueError(f"unknown model {model!r}. Known models: {known} (or pass a path to a .bin file)")

    target = cache_dir() / f"ggml-{model}.bin"
    if target.exists():
        return target
    if not allow_download:
        raise FileNotFoundError(f"model {model!r} not found at {target} and downloads are disabled")

    _download(f"{_HF_BASE}/ggml-{model}.bin", target)
    return target


def _download(url: str, target: Path) -> None:
    print(f"voxscribe: downloading model -> {target}", file=sys.stderr)
    tmp = target.with_suffix(target.suffix + ".part")
    try:
        with urllib.request.urlopen(url) as resp:  # noqa: S310 (trusted host)
            total = int(resp.headers.get("Content-Length", 0))
            done = 0
            chunk = 1 << 20  # 1 MiB
            with open(tmp, "wb") as fh:
                while True:
                    buf = resp.read(chunk)
                    if not buf:
                        break
                    fh.write(buf)
                    done += len(buf)
                    if total:
                        pct = done * 100 // total
                        mb = done / (1 << 20)
                        tmb = total / (1 << 20)
                        print(f"\r  {pct:3d}%  {mb:7.1f} / {tmb:.1f} MiB", end="", file=sys.stderr)
        print("", file=sys.stderr)
        shutil.move(str(tmp), str(target))
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise
