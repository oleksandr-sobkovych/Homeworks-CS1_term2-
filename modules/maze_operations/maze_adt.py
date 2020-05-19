"""Represent a maze."""
import requests
from modules.helper_collections.arrays import Array2D
import os
import json
import re
from pathlib import Path
from modules.maze_operations.a_star_search import AStarSearcher
from modules.maze_operations.q_learner import QLearner
from PIL import Image


class MazeConstructionError(Exception):
    """An exception for rare conflicting parameters."""
    def __init__(self, dimens: tuple, solution_len: int):
        super().__init__(f"unable to build a maze with solution length"
                         f" {solution_len} and of dimensions: {dimens}")


class MazeNameError(Exception):
    """Exception for invalid maze name."""
    pass


class MazeUnsolvableError(Exception):
    """Indicates that maze cannot be solved."""
    pass


class Maze:
    """Represent a maze."""

    def __init__(self, name: str = None, size: tuple = (0, 0),
                 array: list = None, **kwargs):
        if re.fullmatch(r"[\w_\d]+", name):
            self.name = name
        else:
            raise MazeNameError(f"name should be an allowed one")
        self.size = tuple(map(int, size))
        # self.array = self._list_to_array(array)
        self.array = array
        allowed_params = {"optimal_route": [],
                          "q_data": {},
                          "img": None,
                          "learning_rate": 0.1,
                          "discount": 0.95,
                          "algo": "User"}
        for param in allowed_params:
            self._init_param(param, kwargs, allowed_params[param])
        self.start = self.finish = None
        self._search_endpoints()

    def _init_param(self, param: str, source_collection, default):
        """"""
        if param in source_collection:
            self.__dict__[param] = source_collection[param]
        else:
            self.__dict__[param] = default

    def _list_to_array(self, lst: list) -> Array2D:
        """"""
        array = Array2D(*self.size)
        for i in range(self.size[0]):
            for ii in range(self.size[1]):
                array[i, ii] = lst[i][ii]
        return array

    def _search_endpoints(self):
        """"""
        array = self.array
        for i in range(self.size[0]):
            for ii in range(self.size[1]):
                if array[i][ii] == 2:
                    self.start = (i, ii)
                elif array[i][ii] == 3:
                    self.finish = (i, ii)
        if self.start is None or self.finish is None:
            raise MazeUnsolvableError("no endpoints")

    @staticmethod
    def _scale(*args: str, adder=0):
        """"""
        return tuple(2*(int(num)-1)+adder for num in args)

    @classmethod
    def _get_coords(cls, pos_node: dict):
        """"""
        return cls._scale(pos_node["y"], pos_node["x"])

    @classmethod
    def _get_node_neighbours(cls, node: dict):
        exits = node["exits"]
        for direction in exits:
            coords = cls._get_coords(exits[direction])
            if direction == "n":
                yield coords[0]-1, coords[1]
            elif direction == "s":
                yield coords[0]+1, coords[1]
            elif direction == "w":
                yield coords[0], coords[1]+1
            else:
                yield coords[0], coords[1]-1

    @classmethod
    def _graph_to_array(cls, graph, dimensions, start, finish):
        """"""
        size = cls._scale(*dimensions, adder=1)
        array = [[1 for i in range(size[0])] for ii in range(size[1])]
        for node in graph:
            coords = cls._get_coords(node["coordinates"])
            array[coords[0]][coords[1]] = 0
            for near in cls._get_node_neighbours(node):
                array[near[0]][near[1]] = 0
        start = cls._get_coords(start)
        finish = cls._get_coords(finish)
        array[start[0]][start[1]] = 2
        array[finish[0]][finish[1]] = 3
        return array, size

    @classmethod
    def from_api(cls, name: str, dimensions: tuple = (10, 10),
                 algo: str = "Recursive Backtracker",
                 solution_len: int = None, maze_id=None):
        """Get a single maze with the given parameters from the API.

        :param dimensions: dimensions of the graph
        :param algo: algorithm of the graph
        :param solution_len: length of the solution
        :param maze_id: an id of a specific generated maze
        :return:a Maze() instance from API
        :exception MazeConstructionError: change dimensions or solution length
        """
        if maze_id:
            maze_url = f"https://maze-api.herokuapp.com/api/mazes/{maze_id}"
            graph = requests.get(maze_url).json()
            dimensions = graph["dimensions"]
            dimensions = (int(dimensions["width"]),
                          int(dimensions["height"]))
        else:
            dimensions = tuple(map(int, dimensions))
            if not all(map(lambda x: isinstance(x, int) and x >= 5,
                           dimensions)):
                dimensions = (10, 10)
            params = {
                "number": 1,
                "width": dimensions[0],
                "height": dimensions[1],
                "algorithm": algo.replace(" ", "%20")
                if algo in ("Prims", "Woven", "Growing Tree") else
                "Recursive%20Backtracker",
                "cellShape": "Square",
                "solutionLength": solution_len if solution_len and
                algo in ("Prims", "Growing Tree") else None
            }
            # compose all parameters in a single GET request
            maze_pars = '&'.join(
                map(lambda x: f'{x}={params[x]}',
                    filter(lambda y: True if params[y] is not None else False,
                           params))
            )
            maze_url = (f"https://maze-api.herokuapp.com/api/mazes/?"
                        f"{maze_pars}")
            try:
                graph = requests.get(maze_url).json()[0]
            except IndexError:
                raise MazeConstructionError(dimensions, solution_len)

        array, size = cls._graph_to_array(graph["cellMap"], dimensions,
                                          graph["start"], graph["end"])

        return cls(name=name, size=size, array=array, algo=algo)

    def save_to_database(self):
        """"""
        if self.optimal_route is None:
            raise MazeUnsolvableError("maze cannot be solved")
        path = Path(f"database/{self.name}")
        try:
            os.mkdir(path)
        except OSError:
            None
        if self.img is not None:
            self.img.save(path / "img.jpg")
        json_data = {"name": self.name,
                     "q_data": self.q_data,
                     "size": self.size,
                     "array": self.array,
                     "optimal_route": tuple(self.optimal_route),
                     "start": self.start,
                     "finish": self.finish,
                     "algo": self.algo}
        with open(path / "data.json", encoding="utf-8", mode="w+") as f:
            json.dump(json_data, f, indent=4)
        json_data.pop("name")
        dict_repr = {"name": self.name,
                     "parameters": json_data,
                     "image": f"{path.name}/img.jpg"}
        return dict_repr

    def _find_optimal_route(self):
        """"""
        self.optimal_route = AStarSearcher(self).search_path()

    def find_q_data(self):
        """"""
        if not self.optimal_route:
            self._find_optimal_route()
        if self.optimal_route is None:
            raise MazeUnsolvableError("maze cannot be solved")
        qlearner = QLearner(self)
        self.q_data = qlearner.train_env(self.learning_rate, self.discount)
        self.img = QLearner(self).draw_maze(self.q_data["solution_path"])
        self.q_data["difference"] = len(self.q_data["solution_path"] &
                                        self.optimal_route)

        self.q_data["solution_path"] = tuple(self.q_data["solution_path"])

    @classmethod
    def read_from_database(cls, path: str):
        """"""
        path = Path(path)
        try:
            img = Image.open(path / "img.jpg")
        except FileNotFoundError:
            img = None
        with open(path / "data.json", encoding="utf-8") as f:
            json_data = json.load(f)
        return cls(img=img, **json_data)

    def __repr__(self) -> str:
        """"""
        result_str = ""
        for row in self.array:
            result_str += f"{'  '.join(map(str, row))}\n"
        return result_str
