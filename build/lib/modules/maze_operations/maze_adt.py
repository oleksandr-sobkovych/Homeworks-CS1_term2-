"""Represent a maze."""
from __future__ import annotations
import requests
from modules.helper_collections.arrays import Array2D
import os
import json
import re
from pathlib import Path
from modules.maze_operations.a_star_search import AStarSearcher
from modules.maze_operations.q_learner import QLearner
from PIL import Image
from typing import Any, Collection, Union


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
    START = 2  # indicates start position in the array
    END = 3  # indicates end position in the array

    def __init__(self, name: str = None, size: tuple = (0, 0),
                 array: list = None, **kwargs):
        """Create a new maze.

        :param name: name of the maze
        :param size: size of the maze (two-dimensional tuple)
        :param array: list representation o the maze
        :param kwargs: other possible arguments
        """
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
                          "algo": "User",
                          "size_str": "x".join(map(str, size))}
        for param in allowed_params:
            self._init_param(param, kwargs, allowed_params[param])
        self.start = self.finish = None
        self._search_endpoints()

    def _init_param(self, param: str, source_collection: Collection,
                    default: Any):
        """Initialize additional parameters.

        :param param: name of parameter
        :param source_collection: source collection from where to take it
        :param default: default value (if not found)
        """
        if param in source_collection:
            self.__dict__[param] = source_collection[param]
        else:
            self.__dict__[param] = default

    def _list_to_array(self, lst: list) -> Array2D:
        """Convert a Python list to 2D array."""
        array = Array2D(*self.size)
        for i in range(self.size[0]):
            for ii in range(self.size[1]):
                array[i, ii] = lst[i][ii]
        return array

    def _search_endpoints(self):
        """Search the array for the start and end position."""
        array = self.array
        for i in range(self.size[0]):
            for ii in range(self.size[1]):
                if array[i][ii] == self.START:
                    self.start = (i, ii)
                elif array[i][ii] == self.END:
                    self.finish = (i, ii)
        if self.start is None or self.finish is None:
            raise MazeUnsolvableError("no endpoints")

    @staticmethod
    def _scale(*args: Union[str, int], adder: int = 0) -> tuple:
        """Scale the arguments (stretch by 2 and slide by 1 (and adder)).

        Used for converting API graph maze dimensions into array dimensions.
        :param args: arbitrary integers or numeric strings
        :param adder: additional sliding factor
        :return: tuple of scaled integers
        """
        return tuple(2*(int(num)-1)+adder for num in args)

    @classmethod
    def _get_coords(cls, pos_node: dict) -> tuple:
        """Get coordinates of a node in true array.

        :param pos_node: current node's position as a dictionary
        :return: a tuple of coordinates
        """
        return cls._scale(pos_node["y"], pos_node["x"])

    @classmethod
    def _get_node_neighbours(cls, node: dict):
        """Get all node neighbours from API graph."""
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
    def _graph_to_array(cls, graph: dict, dimensions: tuple,
                        start: dict, finish: dict) -> (list, tuple):
        """Convert the API graph to an array.

        :param graph: API graph (displays connections between neighbour nodes)
        :param dimensions: dimensions of the API maze
        :param start: API start coordinates
        :param finish: API finish coordinates
        :return: a tuple of array itself and its scaled size
        """
        size = cls._scale(*dimensions, adder=1)
        array = [[1 for i in range(size[0])] for ii in range(size[1])]
        for node in graph:
            coords = cls._get_coords(node["coordinates"])
            array[coords[0]][coords[1]] = 0
            for near in cls._get_node_neighbours(node):
                array[near[0]][near[1]] = 0
        start = cls._get_coords(start)
        finish = cls._get_coords(finish)
        array[start[0]][start[1]] = cls.START
        array[finish[0]][finish[1]] = cls.END
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
        size_str = "x".join(map(lambda x: str(x+1), size))

        return cls(name=name, size=size, array=array, algo=algo,
                   size_str=size_str)

    def save_to_database(self) -> dict:
        """Save the maze to the database.

        :return: a representative dictionary for sorting database
        """
        if self.optimal_route is None:
            raise MazeUnsolvableError("maze cannot be solved")
        path = Path(f"static/database/{self.name}")
        try:
            os.mkdir(path)
        except OSError:
            "already exists"
        if self.img is not None:
            self.img.save(path / "img.jpg")
        json_data = {"name": self.name,
                     "q_data": self.q_data,
                     "size": self.size,
                     "array": self.array,
                     "optimal_route": tuple(self.optimal_route),
                     "start": self.start,
                     "finish": self.finish,
                     "algo": self.algo,
                     "size_str": self.size_str}
        with open(path / "data.json", encoding="utf-8", mode="w+") as f:
            json.dump(json_data, f, indent=4)
        json_data.pop("name")
        final_q = json_data.pop("q_data")
        dict_repr = {"name": self.name,
                     "parameters": json_data,
                     "image": f"../static/database/{path.name}/img.jpg"}
        dict_repr["parameters"].update(final_q)
        for key in ("size", "array", "optimal_route", "solution_path"):
            dict_repr["parameters"].pop(key)

        dict_repr["parameters"]["route_len"] = len(
            self.q_data["solution_path"]
        )

        return dict_repr

    def _find_optimal_route(self):
        """Use A* to find optimal route as a set."""
        self.optimal_route = AStarSearcher(self).search_path()

    def find_q_data(self):
        """Train a QAgent to solve the maze and gather desired information."""
        if not self.optimal_route:
            self._find_optimal_route()
        if self.optimal_route is None:
            raise MazeUnsolvableError("maze cannot be solved")
        qlearner = QLearner(self)
        self.q_data = qlearner.train_env(self.learning_rate, self.discount)
        self.img = QLearner(self).draw_maze(self.q_data["solution_path"])
        # number of all different coordinates in two paths
        self.q_data["difference"] = len(
            (self.q_data["solution_path"] | self.optimal_route) -
            (self.q_data["solution_path"] & self.optimal_route)
        )
        self.q_data["solution_path"] = tuple(self.q_data["solution_path"])

    @classmethod
    def read_from_database(cls, path: str) -> Maze:
        """Get a maze from the database.

        :param path: path to the maze directory
        :return: a maze object with appropriate parameters
        """
        path = Path(path)
        try:
            img = Image.open(path / "img.jpg")
        except FileNotFoundError:
            img = None
        with open(path / "data.json", encoding="utf-8") as f:
            json_data = json.load(f)
        return cls(img=img, **json_data)

    def __repr__(self) -> str:
        result_str = ""
        for row in self.array:
            result_str += f"{'  '.join(map(str, row))}\n"
        return result_str
