import random


class Reservoir(object):
    def __init__(self, size):
        self.size = size
        self.reservoir = []
        self.counter = 0.0
        self.current = 0

    def process_element(self, element):
        self.counter += 1
        if len(self.reservoir) < self.size:
            self.reservoir.append(element)
        elif random.random() < self.size / self.counter:
            self.reservoir.remove(random.choice(self.reservoir))
            self.reservoir.append(element)

    def __iter__(self):
        return self

    def __next__(self):
        if self.current == self.size:
            raise StopIteration
        else:
            self.current += 1
            return self.reservoir[self.current - 1]
