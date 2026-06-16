from src.normalize.genres import classify_genre

def test_genre_bucket_mapping():
    assert classify_genre("Art Pop")[0] == "Pop"
    assert classify_genre("Techno")[0] == "Electronic"
    assert classify_genre("Cantopop")[0] == "Global / C-Pop"

def test_exclusion_rules_primary_only():
    assert classify_genre("Hip-Hop")[3] == "primary_genre_rap_hip_hop"
    bucket, _, _, excluded = classify_genre("Art Pop", ["rap"])
    assert bucket == "Pop"
    assert excluded is None
