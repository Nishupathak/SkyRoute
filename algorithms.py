import heapq
from collections import deque


def fewest_stops(graph, start, end):
    if start not in graph.airports or end not in graph.airports:
        raise ValueError("Unknown airport code")
    if start == end:
        return [start]

    visited = {start}
    came_from = {}
    queue = deque([start])

    while queue:
        current = queue.popleft()
        for flight in graph.neighbors(current):
            nxt = flight["to"]
            if nxt in visited:
                continue
            visited.add(nxt)
            came_from[nxt] = current
            if nxt == end:
                return rebuild_path(came_from, start, end)
            queue.append(nxt)

    return None


def best_route(graph, start, end, key="price"):
    if key not in ("price", "minutes"):
        raise ValueError("key must be 'price' or 'minutes'")
    if start not in graph.airports or end not in graph.airports:
        raise ValueError("Unknown airport code")
    if start == end:
        return [start]

    best = {start: 0}
    came_from = {}
    heap = [(0, start)]

    while heap:
        cost, current = heapq.heappop(heap)
        if cost > best.get(current, float("inf")):
            continue
        if current == end:
            return rebuild_path(came_from, start, end)
        for flight in graph.neighbors(current):
            nxt = flight["to"]
            new_cost = cost + flight[key]
            if new_cost < best.get(nxt, float("inf")):
                best[nxt] = new_cost
                came_from[nxt] = current
                heapq.heappush(heap, (new_cost, nxt))

    return None


def rebuild_path(came_from, start, end):
    path = [end]
    while path[-1] != start:
        path.append(came_from[path[-1]])
    path.reverse()
    return path