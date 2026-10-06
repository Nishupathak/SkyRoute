import db
from algorithms import best_route, fewest_stops

MODES = {"1": "fewest stops", "2": "cheapest", "3": "fastest"}


def show_route(g, path):
    if path is None:
        print("Sorry, no route found.")
        return
    names = [g.name(code) for code in path]
    print("Route:", " -> ".join(names))
    total_price = 0
    total_minutes = 0
    for a, b in zip(path, path[1:]):
        flight = g.get_flight(a, b)
        total_price += flight["price"]
        total_minutes += flight["minutes"]
    print("Layovers:", max(0, len(path) - 2))
    print("Total price:", total_price, "rupees")
    print("Total flying time:", total_minutes, "minutes")


def find(g, mode, start, end):
    if mode == "1":
        return fewest_stops(g, start, end)
    if mode == "2":
        return best_route(g, start, end, "price")
    return best_route(g, start, end, "minutes")


def search(g):
    print("Airports:", ", ".join(sorted(g.airports)))
    start = input("From (code): ").strip().upper()
    end = input("To (code): ").strip().upper()
    print("1 = fewest stops, 2 = cheapest, 3 = fastest")
    mode = input("Pick: ").strip()
    if mode not in MODES:
        print("Please pick 1, 2 or 3.")
        return
    try:
        path = find(g, mode, start, end)
    except ValueError as error:
        print("Error:", error)
        return
    show_route(g, path)
    db.log_search(start, end, MODES[mode], path is not None)


def show_history():
    rows = db.recent_searches()
    if not rows:
        print("No searches yet.")
        return
    for r in rows:
        result = "found" if r["found"] else "no route"
        print(r["created_at"], "|", r["origin"], "->", r["destination"],
              "|", r["mode"], "|", result)


if __name__ == "__main__":
    db.init_db()
    g = db.load_graph()
    while True:
        print()
        print("1 = search a route, 2 = recent searches, 3 = quit")
        choice = input("Pick: ").strip()
        if choice == "1":
            search(g)
        elif choice == "2":
            show_history()
        elif choice == "3":
            print("Bye!")
            break
        else:
            print("Please pick 1 to 3.")