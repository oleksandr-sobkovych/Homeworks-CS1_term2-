"""Examples of working with data using libraries."""

import json
import numpy as np

from examples.maze_api_example import GraphMaze


def float_parser(float_str: str) -> float:
    """Round a string of float to 2."""
    return round(float(float_str), 2)


def int_parser(int_str: str) -> str:
    """Convert a numeric string to hex."""
    return hex(int(int_str))


def json_example():
    """Working with json example."""
    print("JSON usage example:", end="\n\n\n")
    print("Loading maze from API...")
    maze1 = GraphMaze.from_api(maze_id="5da9f9d6461a8c001703a1fc")
    print(maze1)
    with open("maze1.json", mode="w+", encoding="utf-8") as f:
        json.dump(maze1.graph, f, indent=4, sort_keys=True)

    with open("weird_maze.txt", "w+", encoding="utf-8") as f:
        json.dump(maze1.graph, f, indent=4, separators=(";;", "::"))

    print("Weird separators:")
    with open("weird_maze.txt", encoding="utf-8") as f:
        for _ in range(4):
            print(f.readline())

    with open("maze1.json", encoding="utf-8") as f:
        maze1_graph = json.load(f)
    print(f"Loaded and initial mazes are equal: {maze1_graph == maze1.graph}")

    custom_graph = {1: [128, 2, 36], "bar": {(1, 2): "fooх",
                                             "fooх": (1.2342, 2.4567)}}

    with open("custom.json", "w+", encoding="utf-8") as f:
        json.dump(custom_graph, f, skipkeys=True, indent=4)

    print("Hex integers and rounded floats:")
    with open("custom.json", encoding="utf-8") as f:
        print(json.load(f, parse_float=float_parser, parse_int=int_parser),
              end="\n\n")


def numpy_example():
    """Working with numpy example."""
    print("numpy usage example:", end="\n\n\n")
    matrix1 = np.zeros((4, 5))
    print(f"Initialized matrix:\n{matrix1}", end="\n\n")
    matrix1 = matrix1.reshape((2, 10))
    print(f"Reshaped matrix:\n{matrix1}", end="\n\n")
    matrix2 = np.random.random((4, 4))
    print(f"Random matrix:\n{matrix2}", end="\n\n")
    matrix3 = matrix2 * 100
    print(f"Random matrix expanded to the range [0, 100]:\n{matrix3}",
          end="\n\n")
    print(f"Expanded random matrix elements larger than 50\n"
          f"{matrix3[matrix3 > 50]}")
    print(f"Positions of expanded random matrix elements larger than 30:\n")
    indexes = np.nonzero(matrix3 > 30)
    for i, j in zip(indexes[0], indexes[1]):
        print(f"{matrix3[i,j]} at ({i}, {j})")
    print(matrix3, end="\n\n")
    print(f"Min values from exp. rnd. matrix for every row:\n"
          f"{np.min(matrix3, axis=1)}")
    print(f"Mean for every column in the matrix:\n{np.mean(matrix3, axis=0)}")
    print("Performing a formula: (sum with i from 1 to 100 of "
          "the array of int(random*range)"
          "(a range starting from 1 and a random both with 100 elements))"
          " mod 123:\n")
    vect_range = np.arange(1, 101, 1)
    print(f"The range: {vect_range}\n")
    vect_random = np.random.random(100)
    print(f"The random vector: {vect_random}\n")
    res = vect_range*vect_random
    print(f"The broadcast: {res}\n")
    res = res.astype(int)
    print(f"After int conversion: {res}\n")
    print(f"The resulting sum: {np.sum(res) % 123}\n")
    np.savez("three_vectors.npz", rnd=vect_random, rng=vect_range, res=res)
    with np.load("three_vectors.npz") as data:
        print(f"Loaded objects are equal to saved ones:\n")
        print(f"For random:{vect_random == data['rnd']}")
        print(f"For range:{vect_range == data['rng']}")
        print(f"For result:{res == data['res']}")


if __name__ == '__main__':
    json_example()
    numpy_example()
