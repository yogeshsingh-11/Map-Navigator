import heapq


class PriorityQueue:
    def __init__(self):
        self.heap = []
        self.counter = 0

    def insert(self, key, value):
        entry = [key, self.counter, value]
        self.counter += 1
        heapq.heappush(self.heap, entry)

    def extract_min(self):
        while self.heap:
            priority, _, value = heapq.heappop(self.heap)
            if value is not None:
                return priority, value
        raise KeyError('Pop from an empty priority queue')

    def decrease_key(self, key, value):
        index = -1
        for i, entry in enumerate(self.heap):
            if entry[2] == value:
                index = i
                break
        if index != -1:
            self.heap.pop(index)
            # self.counter -= 1
        self.insert(key, value)

    def is_empty(self):
        return len(self.heap) == 0
