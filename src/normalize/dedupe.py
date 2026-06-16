from __future__ import annotations
from difflib import SequenceMatcher
from .text import normalize_name, canonical_album_title, normalize_url


def album_key(artist: str, album: str, year: int | str | None) -> str:
    return f"{normalize_name(artist)}::{canonical_album_title(album)}::{year or ''}"


def is_fuzzy_duplicate(a_artist: str, a_album: str, b_artist: str, b_album: str, threshold: float = 0.88) -> bool:
    a = f"{normalize_name(a_artist)} {canonical_album_title(a_album)}"
    b = f"{normalize_name(b_artist)} {canonical_album_title(b_album)}"
    return SequenceMatcher(None, a, b).ratio() >= threshold


def review_key(source: str, url: str | None, title: str, review_date: str | None = None) -> str:
    if url:
        return normalize_url(url)
    return f"{source.lower()}::{normalize_name(title)}::{review_date or ''}"
