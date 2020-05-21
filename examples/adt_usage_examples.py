"""Test main ADT features."""
from modules.maze_operations.maze_adt import Maze
from modules.maze_operations.process_maze import BackgroundProcessor
from modules.maze_operations.q_learner import QLearner
from modules.helper_collections.llistqueue import Queue
from modules.maze_operations.maze_list import MazesList


class VerboseBGProcessor(BackgroundProcessor):
    """For demonstration."""

    @staticmethod
    def process_maze(maze):
        """Print the maze."""
        print(maze) # waits for ten seconds if queue is empty


if __name__ == '__main__':
    m_list = MazesList("database/options.json", "database/mazes_list.json")
    # maze2 = Maze.read_from_database("database/my_maze")
    queue = Queue()
    maze2 = Maze("small_maze", array=[[2, 0], [0, 3]], size=(2, 2))
    queue.push(maze2)
    VerboseBGProcessor(queue, m_list).start()
    maze1 = Maze.from_api("my_maze")
    maze1._find_optimal_route()  #uses AStarSearcher and _CellNode
    queue.push(maze1)
    new_queue = Queue()
    try:
        BackgroundProcessor(new_queue, m_list).start()
    except FileNotFoundError:
        print("Done processing.")
    new_queue.push(maze1)
    new_queue.push(maze2)
    print(QLearner(maze1).train_env(verbose=True))  #uses QAgent
    maze3 = Maze.from_api("new_maze", maze_id="5da9f969461a8c0017016912")
    QLearner(maze3).train_env(verbose=True)
