# -*- coding: utf-8 -*-

import threading
from time import sleep


class BackgroundProcessor(threading.Thread):
    """"""

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.setDaemon(True)

    def run(self):
        """"""
        while True:
            if self.queue.isEmpty():
                sleep(10)
            else:
                maze = self.queue.pop()
                self.process_maze(maze)

    @staticmethod
    def process_maze(maze):
        """"""
        maze.save_to_database()
