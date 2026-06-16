from src.normalize.scores import normalize_score
from src.parsers.base import parse_feed_entry

class E(dict):
    __getattr__ = dict.get

def test_score_conversions():
    assert normalize_score("Guardian 4/5") == 8.0
    assert normalize_score("AllMusic 3.5/5") == 7.0
    assert normalize_score("Metacritic 84/100") == 8.4
    assert normalize_score("Pitchfork 7.8/10") == 7.8

def test_pitchfork_unavailable_score_preserved():
    item = parse_feed_entry(E(title="Artist - Album", link="https://p.test/a", summary="review text"), {"name":"Pitchfork","id":"pitchfork","score_scale":10})
    assert item.score_status == "no_score"
    assert item.reason_for_inclusion == "pitchfork_discovery_no_score"
