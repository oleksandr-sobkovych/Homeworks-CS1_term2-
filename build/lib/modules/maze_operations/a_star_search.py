"""Use A* to find the optimal route through a maze."""
from __future__ import annotations
from modules.helper_collections.node import Node
from math import inf
from typing import Optional, Iterable


class _CellNode(Node):
    """A node class for A* Pathfinding"""

    def __init__(self, data: (int, int), parent: _CellNode = None):
        """Create a new node.

        :param data: location stored in node
        :param parent: reference to the previous node
        """
        super().__init__(data, parent)
        # initialize the undiscovered node
        self.g = inf
        self.h = inf
        self.f = inf

    def __eq__(self, other: _CellNode) -> bool:
        return self.data == other.data

    def __repr__(self) -> str:
        return f"{self.data}"


class AStarSearcher:
    """Detect an optimal path in a maze."""
    allowed_moves = ((0, -1), (0, 1), (-1, 0), (1, 0))

    def __init__(self, maze):
        """Create a new A* searcher based on a maze.

        :param maze: maze to base upon
        :type maze: Maze
        """
        self.array = maze.array
        self.start = _CellNode(maze.start)
        self.start.f = self.start.g = self.start.h = 0
        self.finish = _CellNode(maze.finish)
        self.col_len = len(maze.array)
        self.row_len = len(maze.array[0])

    def _calc_heuristic(self, cell: _CellNode) -> int:
        """Calculate the heuristic (Manhattan Distance) for the cell."""
        return (abs(cell.data[0] - self.start.data[0]) +
                abs(cell.data[1] - self.start.data[1]))

    def _is_valid_pos(self, pos_i: int, pos_ii: int) -> bool:
        """Check if position belongs to the maze

        :param pos_i: row of the cell
        :param pos_ii: column of the cell
        :return: True if it does, False otherwise
        """
        return (self.col_len > pos_i >= 0 and
                self.row_len > pos_ii >= 0 and
                self.array[pos_i][pos_ii] != 1)

    def _is_final(self, cell: _CellNode) -> bool:
        """Check if the cell if the end goal."""
        return cell == self.finish

    def _generate_children(self, cell: _CellNode) -> Iterable[_CellNode]:
        """Generate all valid neighbours for the cell."""
        for i, ii in self.allowed_moves:
            new_pos = (cell.data[0] + i, cell.data[1] + ii)
            if self._is_valid_pos(*new_pos):
                yield _CellNode(new_pos, cell)

    @staticmethod
    def _build_path(cell: _CellNode) -> set:
        """Build the final path as a set of coordinates."""
        path = set()
        while cell is not None:
            path.add(cell.data)
            cell = cell.next
        # set of tuples of integers
        return path

    def search_path(self) -> Optional[set]:
        """Search for the path using A*."""
        if not (self._is_valid_pos(*self.start.data) and
                self._is_valid_pos(*self.finish.data)):
            return None

        if self.start == self.finish:
            return self._build_path(self.start)

        # visited and unvisited but detected cells
        closed_list = []
        open_list = []

        open_list.append(self.start)

        while len(open_list) > 0:
            curr_i = min(range(len(open_list)),
                         key=lambda i: open_list[i].f)
            curr_node = open_list.pop(curr_i)
            closed_list.append(curr_node)
            for child in self._generate_children(curr_node):
                if self._is_final(child):
                    return self._build_path(child)
                if child in closed_list:
                    continue
                child.g = curr_node.g + 1
                child.h = self._calc_heuristic(child)
                child.f = child.g + child.h
                for cell in open_list:
                    if child == cell and cell.f <= child.f:
                        break
                else:
                    open_list.append(child)
        return None
