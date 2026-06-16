from __future__ import annotations

BUCKETS = ["Pop", "Rock", "Electronic", "R&B / Soul", "Folk / Country", "Global / C-Pop"]
EXCLUDED_PRIMARY = {"jazz": "primary_genre_jazz", "classical": "primary_genre_classical", "instrumental": "primary_genre_instrumental", "rap": "primary_genre_rap_hip_hop", "hip-hop": "primary_genre_rap_hip_hop", "hip hop": "primary_genre_rap_hip_hop"}
MAP = {
    "synth-pop": "Pop", "art pop": "Pop", "indie pop": "Pop", "pop": "Pop",
    "indie rock": "Rock", "alternative rock": "Rock", "post-punk": "Rock", "rock": "Rock",
    "techno": "Electronic", "house": "Electronic", "ambient": "Electronic", "idm": "Electronic", "electronic": "Electronic",
    "r&b": "R&B / Soul", "soul": "R&B / Soul", "neo-soul": "R&B / Soul",
    "folk": "Folk / Country", "americana": "Folk / Country", "country": "Folk / Country",
    "mandopop": "Global / C-Pop", "cantopop": "Global / C-Pop", "c-pop": "Global / C-Pop", "hk pop": "Global / C-Pop", "taiwan pop": "Global / C-Pop", "k-pop": "Global / C-Pop", "j-pop": "Global / C-Pop", "global pop": "Global / C-Pop",
}


def classify_genre(primary_genre: str | None, secondary: list[str] | None = None) -> tuple[str, str | None, str, str | None]:
    primary = (primary_genre or "").strip().lower()
    if primary in EXCLUDED_PRIMARY:
        return "Excluded", primary_genre, "high", EXCLUDED_PRIMARY[primary]
    if primary in MAP:
        return MAP[primary], primary_genre, "high", None
    for genre in secondary or []:
        bucket = MAP.get(genre.lower())
        if bucket:
            return bucket, primary_genre or genre, "medium", None
    return "Unknown", primary_genre, "low", None
