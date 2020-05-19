# -*- coding: utf-8 -*-

import threading
from time import sleep
from modules.maze_operations.maze_adt import MazeUnsolvableError


class BackgroundProcessor(threading.Thread):
    """"""

    def __init__(self, queue, maze_list,
                 l_rates=(0.1, 0.3), discounts=(0.95, 0.75)):
        threading.Thread.__init__(self)
        self.queue = queue
        self.setDaemon(True)
        self.l_rates = l_rates
        self.discounts = discounts
        self.maze_list = maze_list

    def run(self):
        """"""
        while True:
            if self.queue.isEmpty():
                sleep(10)
            else:
                maze = self.queue.pop()
                self.process_maze(maze)

    def process_maze(self, maze):
        """"""
        base_name = maze.name
        try:
            for l_rate in self.l_rates:
                for discount in self.discounts:
                    maze.find_q_data()
                    maze.name = f"{base_name}-{l_rate}-{discount}"
                    self.maze_list.mazes_list.append(maze.save_to_database())
            self.maze_list.save()
        except MazeUnsolvableError:
            print("Impossible to solve.")
        else:
            print(f"Thread has finished processing {base_name} maze.")
