"""Represent a node."""
from __future__ import annotations
from typing import Any


class Node:
    """Nodes for singly linked structures."""

    def __init__(self, data: Any, next_n: Node = None):
        """Create a node instance.

        :param data: data to store
        :param next_n: link to the next node
        """
        self.data = data
        self.next = next_n
