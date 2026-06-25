"""Unit tests that don't require ffmpeg / whisper.cpp to be installed."""

import pytest

from voxscribe.cli import _build_parser
from voxscribe.mcp_server import transcribe_file
from voxscribe.models import MODELS, cache_dir, resolve_model


def test_parser_defaults():
    args = _build_parser().parse_args(["note.opus"])
    assert [str(a) for a in args.audio] == ["note.opus"]
    assert args.model == "base"
    assert args.language == "auto"
    assert args.format == "txt"


def test_parser_rejects_unknown_format():
    with pytest.raises(SystemExit):
        _build_parser().parse_args(["note.opus", "-f", "doc"])


def test_resolve_model_rejects_unknown():
    with pytest.raises(ValueError):
        resolve_model("not-a-real-model", allow_download=False)


def test_resolve_model_missing_without_download(tmp_path, monkeypatch):
    monkeypatch.setenv("VOXSCRIBE_HOME", str(tmp_path))
    with pytest.raises(FileNotFoundError):
        resolve_model("base", allow_download=False)


def test_cache_dir_respects_home(tmp_path, monkeypatch):
    monkeypatch.setenv("VOXSCRIBE_HOME", str(tmp_path))
    assert cache_dir() == tmp_path / "models"


def test_local_bin_path_resolves(tmp_path):
    fake = tmp_path / "ggml-custom.bin"
    fake.write_bytes(b"")
    assert resolve_model(str(fake)) == fake


def test_catalog_not_empty():
    assert "base" in MODELS


def test_mcp_transcribe_missing_file():
    with pytest.raises(ValueError, match="no such file"):
        transcribe_file("/no/such/audio.opus")


def test_mcp_transcribe_bad_format(tmp_path):
    audio = tmp_path / "a.wav"
    audio.write_bytes(b"")
    with pytest.raises(ValueError, match="unknown format"):
        transcribe_file(str(audio), fmt="doc")
