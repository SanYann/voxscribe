"""Offline text translation via Argos Translate (optional `translate` extra)."""

from __future__ import annotations


def translate_text(text: str, source: str, target: str) -> str:
    """Translate ``text`` from ``source`` to ``target`` language code, fully offline.

    Downloads the language pack on first use. Argos pivots through English
    automatically when no direct pair exists.
    """
    if source == target:
        return text
    try:
        import argostranslate.package as pkg
        import argostranslate.translate as tr
    except ImportError as exc:
        raise RuntimeError(
            "translation needs the 'translate' extra. Install it with:\n"
            '    pip install "voxscribe[translate]"'
        ) from exc

    installed = {(p.from_code, p.to_code) for p in pkg.get_installed_packages()}
    if (source, target) not in installed:
        pkg.update_package_index()
        available = pkg.get_available_packages()
        match = next((p for p in available if p.from_code == source and p.to_code == target), None)
        if match is None:
            raise RuntimeError(f"no offline translation package available for {source} -> {target}")
        pkg.install_from_path(match.download())

    return tr.translate(text, source, target)
