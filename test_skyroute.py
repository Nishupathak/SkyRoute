import pytest

from algorithms import best_route, fewest_stops
from cache import LRUCache
from data import AIRPORTS, FLIGHTS
from graph import Graph
from trie import Trie


def make_graph():
    g = Graph()
    for code, name in AIRPORTS.items():
        g.add_airport(code, name)
    for a, b, price, minutes in FLIGHTS:
        g.add_flight(a, b, price, minutes)
    return g


def route_cost(g, path, key):
    return sum(g.get_flight(a, b)[key] for a, b in zip(path, path[1:]))


def brute_force_min(g, start, end, key):
    best = [float("inf")]

    def walk(node, seen, cost):
        if cost >= best[0]:
            return
        if node == end:
            best[0] = cost
            return
        for flight in g.neighbors(node):
            nxt = flight["to"]
            if nxt not in seen:
                walk(nxt, seen | {nxt}, cost + flight[key])

    walk(start, {start}, 0)
    return best[0]


def test_fewest_stops_to_goa_uses_one_layover():
    g = make_graph()
    path = fewest_stops(g, "DEL", "GOI")
    assert path[0] == "DEL" and path[-1] == "GOI"
    assert len(path) == 3


def test_same_airport_returns_itself():
    g = make_graph()
    assert fewest_stops(g, "DEL", "DEL") == ["DEL"]
    assert best_route(g, "DEL", "DEL") == ["DEL"]


def test_unknown_airport_raises():
    g = make_graph()
    with pytest.raises(ValueError):
        fewest_stops(g, "XYZ", "DEL")
    with pytest.raises(ValueError):
        best_route(g, "DEL", "XYZ")


def test_cheapest_delhi_to_chennai():
    g = make_graph()
    path = best_route(g, "DEL", "MAA", "price")
    assert path == ["DEL", "HYD", "MAA"]
    assert route_cost(g, path, "price") == 7500


def test_fastest_delhi_to_chennai():
    g = make_graph()
    path = best_route(g, "DEL", "MAA", "minutes")
    assert route_cost(g, path, "minutes") == 230


def test_no_route_returns_none():
    g = make_graph()
    g.add_airport("PNQ", "Pune")
    assert fewest_stops(g, "DEL", "PNQ") is None
    assert best_route(g, "DEL", "PNQ") is None


@pytest.mark.parametrize("key", ["price", "minutes"])
def test_dijkstra_matches_brute_force_for_every_pair(key):
    g = make_graph()
    for a in AIRPORTS:
        for b in AIRPORTS:
            if a != b:
                path = best_route(g, a, b, key)
                assert route_cost(g, path, key) == brute_force_min(g, a, b, key)


def test_graph_rejects_unknown_airport():
    g = Graph()
    g.add_airport("DEL", "Delhi")
    with pytest.raises(ValueError):
        g.add_flight("DEL", "XYZ", 100, 60)


def test_lru_evicts_least_recently_used():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    c.get("a")
    c.put("c", 3)
    assert c.get("b") is None
    assert c.get("a") == 1
    assert c.get("c") == 3


def test_lru_counts_hits_and_misses():
    c = LRUCache(2)
    c.put("a", 1)
    c.get("a")
    c.get("zzz")
    assert c.stats()["hits"] == 1
    assert c.stats()["misses"] == 1


def test_trie_suggestions():
    t = Trie()
    t.insert("Delhi", "DEL")
    t.insert("DEL", "DEL")
    t.insert("Dehradun", "DED")
    assert t.suggest("del") == ["DEL"]
    assert t.suggest("de") == ["DED", "DEL"]
    assert t.suggest("zzz") == []