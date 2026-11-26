"""Custom data structures used by the queue consolidation algorithm."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Job:
    job_id: str
    timestamp: float
    department: str
    original_index: int

    def as_dict(self):
        return {
            "job_id": self.job_id,
            "timestamp": self.timestamp,
            "department": self.department,
            "original_index": self.original_index,
        }


class Node:
    def __init__(self, value):
        self.value = value
        self.next: Optional["Node"] = None


class LinkedQueue:
    """Singly linked queue; append is O(1), removal from head is O(1)."""
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def append(self, value):
        node = Node(value)
        if self.tail is None:
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self.size += 1

    def peek(self):
        return self.head.value if self.head else None

    def pop(self):
        if self.head is None:
            return None
        node = self.head
        self.head = node.next
        if self.head is None:
            self.tail = None
        self.size -= 1
        return node.value

    def __len__(self):
        return self.size

    def to_list(self):
        result, node = [], self.head
        while node:
            result.append(node.value)
            node = node.next
        return result


class MinHeap:
    """Custom binary min heap. No heapq or built-in sorting is used."""
    def __init__(self):
        self.items = []

    @staticmethod
    def key(job):
        # Tie rule: timestamp, then department code, then original position.
        return (job.timestamp, job.department.casefold(), job.original_index)

    def __len__(self):
        return len(self.items)

    def push(self, item):
        self.items.append(item)
        self._sift_up(len(self.items) - 1)

    def pop(self):
        if not self.items:
            raise IndexError("pop from empty heap")
        minimum = self.items[0]
        last = self.items.pop()
        if self.items:
            self.items[0] = last
            self._sift_down(0)
        return minimum

    def _sift_up(self, index):
        while index > 0:
            parent = (index - 1) // 2
            if self.key(self.items[parent]) <= self.key(self.items[index]):
                break
            self.items[parent], self.items[index] = self.items[index], self.items[parent]
            index = parent

    def _sift_down(self, index):
        size = len(self.items)
        while True:
            left, right = 2 * index + 1, 2 * index + 2
            smallest = index
            if left < size and self.key(self.items[left]) < self.key(self.items[smallest]):
                smallest = left
            if right < size and self.key(self.items[right]) < self.key(self.items[smallest]):
                smallest = right
            if smallest == index:
                return
            self.items[index], self.items[smallest] = self.items[smallest], self.items[index]
            index = smallest
