class Graph:
    def __init__(self):
        self.airports = {}
        self.flights = {}

    def add_airport(self, code, name):
        self.airports[code] = name
        self.flights[code] = []

    def add_flight(self, a, b, price, minutes):
        if a not in self.airports or b not in self.airports:
            raise ValueError("Unknown airport: " + a + " or " + b)
        self.flights[a].append({"to": b, "price": price, "minutes": minutes})
        self.flights[b].append({"to": a, "price": price, "minutes": minutes})

    def neighbors(self, code):
        return self.flights[code]

    def name(self, code):
        return self.airports[code]

    def get_flight(self, a, b):
        for flight in self.flights[a]:
            if flight["to"] == b:
                return flight
        return None