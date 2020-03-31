"""Example of Maze API printing the mazes."""


import requests


class MazeConstructionError(Exception):
    """An exception for rare conflicting parameters."""
    def __init__(self, dimens: tuple, solution_len: int):
        super().__init__(f"unable to build a maze with solution length"
                         f" {solution_len} and of dimensions: {dimens}")


class GraphMaze:
    """A class for representing the maze as a graph."""

    def __init__(self, graph: dict):
        self.graph = graph
        self._id = self.graph["_id"]

    @classmethod
    def from_api(cls, dimensions: tuple = (10, 10),
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
            maze = requests.get(maze_url).json()
        else:
            if not all(map(lambda x: isinstance(x, int) and x >= 5,
                           dimensions)):
                dimensions = (None, None)
            pars = {
                "number": 1,
                "width": dimensions[0],
                "height": dimensions[1],
                "algorithm": algo.replace(" ", "%20")
                if algo in ("Prims", "Woven", "Growing Tree") else
                "Recursive%20Backtracker",
                "cellShape": "Square",
                "solutionLength": solution_len
                if algo in ("Prims", "Growing Tree") else None
            }
            # compose all parameters in a single GET request
            maze_pars = '&'.join(
                map(lambda x: f'{x}={pars[x]}',
                    filter(lambda y: True if pars[y] is not None else False,
                           pars))
            )
            maze_url = (f"https://maze-api.herokuapp.com/api/mazes/?"
                        f"{maze_pars}")
            try:
                maze = requests.get(maze_url).json()[0]
            except IndexError:
                raise MazeConstructionError(dimensions, solution_len)
        return cls(maze)

    def get_id(self):
        """Get the graph's id."""
        return self._id

    def __str__(self):
        """Return the representable string provided by the API."""
        return self.graph["displayString"].replace("▁▁▁", "___")

    def solved(self):
        """Return a sting with the correct path in it."""
        return (self.graph["displayStringWithSolutionPath"].replace("▁▁▁",
                                                                    "___"))


if __name__ == '__main__':
    maze1 = GraphMaze.from_api(maze_id="5da9fc2f461a8c001710e70c")
    # structure test
    assert "e" in maze1.graph["cellMap"][0]["exits"]
    assert maze1.graph["start"]["x"] == 1
    # preprocessed string test
    print(maze1)
    print(maze1.solved())
    maze2 = GraphMaze.from_api(dimensions=(10, 10),
                               algo="Prims")
    print(maze2)
    maze3 = GraphMaze.from_api(algo="ygefukwg")
    print(maze3)
    maze4 = GraphMaze.from_api(algo="Growing Tree", dimensions=(10, 10),
                               solution_len=20)
    print(maze4)
    print(maze4.solved())
    assert (GraphMaze.from_api(maze_id=maze4.get_id()).__str__() ==
            maze4.__str__())
