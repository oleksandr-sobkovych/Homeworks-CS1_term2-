# -*- coding: utf-8 -*-
"""Work with a background processor thread."""
import threading
from time import sleep
from modules.maze_operations.maze_adt import MazeUnsolvableError
from modules.maze_operations.maze_adt import Maze
from modules.maze_operations.maze_list import MazesList
from modules.helper_collections.llistqueue import Queue


class MazeNameExists(Exception):
    """Indicates that maze with this name already exists."""
    pass


class BackgroundProcessor(threading.Thread):
    """A thread for handling maze processing."""

    def __init__(self, queue: Queue, maze_list: MazesList,
                 l_rates: tuple = (0.1, 0.3), discounts: tuple = (0.95, 0.75)):
        """Create a new thread.

        :param queue: maze queue
        :param maze_list: list of all processed mazes
        :param l_rates: learning rates to process for
        :param discounts: discount rates to process for
        """
        threading.Thread.__init__(self)
        self.queue = queue
        self.setDaemon(True)
        self.l_rates = l_rates
        self.discounts = discounts
        self.maze_list = maze_list

    def run(self):
        """Run the thread while the main program runs."""
        while True:
            if self.queue.isEmpty():
                sleep(10)
            else:
                maze = self.queue.pop()
                self.process_maze(maze)

    def process_maze(self, maze: Maze):
        """Process a maze: use A* and Q Learning techniques."""
        base_name = maze.name
        try:
            if base_name not in self.maze_list.names:
                self.maze_list.names = base_name
            else:
                raise MazeNameExists("maze with this name already exists")
            for l_rate in self.l_rates:
                for discount in self.discounts:
                    maze.find_q_data()
                    maze.name = f"{base_name}-{l_rate}-{discount}"
                    self.maze_list.mazes_list.append(maze.save_to_database())
            self.maze_list.save()
        except MazeUnsolvableError:
            print("Impossible to solve.")
        except MazeNameExists:
            print("Skipped maze because name exists.")
        else:
            print(f"Thread has finished processing {base_name} maze.")
