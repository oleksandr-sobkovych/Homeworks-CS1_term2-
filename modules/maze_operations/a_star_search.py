"""Use A* to find the optimal route through a maze."""
from __future__ import annotations
from modules.helper_collections.node import Node
from math import inf


class _CellNode(Node):
    """A node class for A* Pathfinding"""

    def __init__(self, data: tuple, parent: _CellNode = None):
        super().__init__(data, parent)
        self.g = inf
        self.h = inf
        self.f = inf

    def __eq__(self, other: _CellNode) -> bool:
        return self.data == other.data

    def __repr__(self) -> str:
        """"""
        return f"{self.data}"


class AStarSearcher:
    """"""
    allowed_moves = ((0, -1), (0, 1), (-1, 0), (1, 0))

    def __init__(self, maze):
        self.array = maze.array
        self.start = _CellNode(maze.start)
        self.start.f = self.start.g = self.start.h = 0
        self.finish = _CellNode(maze.finish)
        self.col_len = len(maze.array)
        self.row_len = len(maze.array[0])

    def _calc_heuristic(self, cell: _CellNode):
        """"""
        return (abs(cell.data[0] - self.start.data[0]) +
                abs(cell.data[1] - self.start.data[1]))

    def _is_valid_pos(self, pos_i: int, pos_ii: int):
        """"""
        return (self.col_len > pos_i >= 0 and
                self.row_len > pos_ii >= 0 and
                self.array[pos_i][pos_ii] != 1)

    def _is_final(self, cell: _CellNode):
        return cell == self.finish

    def _generate_children(self, cell: _CellNode):
        for i, ii in self.allowed_moves:
            new_pos = (cell.data[0] + i, cell.data[1] + ii)
            if self._is_valid_pos(*new_pos):
                yield _CellNode(new_pos, cell)

    @staticmethod
    def _build_path(cell: _CellNode):
        """"""
        # path = Linked_list()
        path = []
        while cell is not None:
            path.append(cell.data)
            cell = cell.next
        return path[::-1]

    def search_path(self):
        """"""
        if not (self._is_valid_pos(*self.start.data) and
                self._is_valid_pos(*self.finish.data)):
            return None

        if self.start == self.finish:
            return self._build_path(self.start)

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
