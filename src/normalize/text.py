from __future__ import annotations
import re
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

STOPWORDS = {"the", "a", "an"}
TRACKING_PREFIXES = ("utm_",)
TRACKING_KEYS = {"fbclid", "gclid", "mc_cid", "mc_eid"}


def normalize_name(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"\b(the|a|an)\b", " ", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def canonical_album_title(title: str) -> str:
    title = title.strip()
    if title.lower().endswith(", the"):
        title = "The " + title[:-5]
    return normalize_name(title)


def normalize_url(url: str) -> str:
    parts = urlsplit(url)
    query = [(k, v) for k, v in parse_qsl(parts.query) if k not in TRACKING_KEYS and not k.startswith(TRACKING_PREFIXES)]
    return urlunsplit((parts.scheme, parts.netloc, parts.path.rstrip("/"), urlencode(query), ""))
