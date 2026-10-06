from flask import Flask, jsonify, request

import db
from algorithms import best_route, fewest_stops
from cache import LRUCache
from trie import Trie

app = Flask(__name__)

db.init_db()
graph = db.load_graph()
cache = LRUCache(100)
MISSING = object()

trie = Trie()
for code, name in graph.airports.items():
    trie.insert(name, code)
    trie.insert(code, code)

MODES = {"fewest": "fewest stops", "cheapest": "cheapest", "fastest": "fastest"}


def find(mode, start, end):
    if mode == "fewest":
        return fewest_stops(graph, start, end)
    if mode == "cheapest":
        return best_route(graph, start, end, "price")
    return best_route(graph, start, end, "minutes")


def summarize(path):
    legs = []
    total_price = 0
    total_minutes = 0
    for a, b in zip(path, path[1:]):
        flight = graph.get_flight(a, b)
        legs.append({
            "from": a,
            "to": b,
            "price": flight["price"],
            "minutes": flight["minutes"],
        })
        total_price += flight["price"]
        total_minutes += flight["minutes"]
    return {
        "path": path,
        "names": [graph.name(code) for code in path],
        "legs": legs,
        "layovers": max(0, len(path) - 2),
        "total_price": total_price,
        "total_minutes": total_minutes,
    }


@app.route("/")
def home():
    return app.send_static_file("index.html")


@app.route("/api/airports")
def airports():
    items = sorted(graph.airports.items())
    return jsonify([{"code": code, "name": name} for code, name in items])


@app.route("/api/suggest")
def suggest():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])
    codes = trie.suggest(q, limit=5)
    return jsonify([{"code": c, "name": graph.name(c)} for c in codes])


@app.route("/api/routes")
def routes():
    start = request.args.get("from", "").strip().upper()
    end = request.args.get("to", "").strip().upper()
    mode = request.args.get("mode", "cheapest").strip().lower()

    if not start or not end:
        return jsonify(error="Please give both 'from' and 'to'."), 400
    if mode not in MODES:
        return jsonify(error="mode must be fewest, cheapest or fastest."), 400
    if start not in graph.airports or end not in graph.airports:
        return jsonify(error="Unknown airport code."), 404

    key = (mode, start, end)
    result = cache.get(key, MISSING)
    from_cache = result is not MISSING
    if not from_cache:
        path = find(mode, start, end)
        result = summarize(path) if path else None
        cache.put(key, result)

    db.log_search(start, end, MODES[mode], result is not None)
    if result is None:
        return jsonify(found=False, mode=mode, cached=from_cache)
    response = dict(result)
    response.update(found=True, mode=mode, cached=from_cache)
    return jsonify(response)


@app.route("/api/cache")
def cache_stats():
    return jsonify(cache.stats())


@app.route("/api/searches")
def searches():
    try:
        limit = int(request.args.get("limit", 5))
    except ValueError:
        return jsonify(error="limit must be a number."), 400
    limit = max(1, min(limit, 50))
    return jsonify(db.recent_searches(limit))


if __name__ == "__main__":
    app.run(debug=True, port=5001)