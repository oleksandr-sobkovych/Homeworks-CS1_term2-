# -*- coding: utf-8 -*-

import threading
from time import sleep
from modules.helper_collections.llistqueue import Queue


class Processor(threading.Thread):
    """"""

    def __init__(self, queue: Queue):
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
                print(maze.array)
