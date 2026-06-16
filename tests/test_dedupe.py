from src.normalize.dedupe import album_key, is_fuzzy_duplicate

def test_album_key():
    assert album_key("The Artist", "Album, The", 2026) == album_key("Artist", "The Album", 2026)

def test_fuzzy_duplicate():
    assert is_fuzzy_duplicate("Artist", "The Album", "Artist", "Album")
