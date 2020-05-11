"""Implementation of the MyStack ADT using a singly linked list."""
from __future__ import annotations
from typing import Any


class Queue:
    """Represent a queue using a singly linked list."""

    def __init__(self):
        """Create an empty instance of queue."""
        self._front = self._rear = None
        self._size = 0

    def isEmpty(self) -> bool:
        """Return True if the queue is empty and False otherwise."""
        return self._front is None

    def __len__(self) -> int:
        """Return the number of items in the queue."""
        return self._size

    def peek(self) -> Any:
        """Return the first item in the queue."""
        assert not self.isEmpty(), "Cannot peek at an empty queue"
        return self._front.item

    def pop(self) -> Any:
        """Remove and return the first item."""
        assert not self.isEmpty(), "Cannot pop from an empty queue"
        node = self._front
        self._front = self._front.next
        if self._front is None:
            self._rear = None
        self._size -= 1
        return node.item

    def push(self, item: Any):
        """Push the item in the rear of the queue.

        :param item: item to push
        """
        if self.isEmpty():
            self._rear = self._front = _QueueNode(item)
        else:
            self._rear.next = _QueueNode(item)
            self._rear = self._rear.next
        self._size += 1


class _QueueNode:
    """Private class for storing queue nodes."""

    def __init__(self, item: Any, link: _QueueNode = None):
        self.item = item
        self.next = link
