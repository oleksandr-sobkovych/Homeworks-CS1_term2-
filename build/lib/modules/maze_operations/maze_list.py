"""Work with a maze list for representing all sortable mazes."""
import json
from threading import Lock
from typing import Collection


class MazesList:
    """Represent a collection of all sortable mazes."""
    keys_to_reversed = {
        "max_reward": True,
        "solution episode": False,
        "difference": False,
        "route_len": False
    }

    def __init__(self, options_filename: str = "static/database/options.json",
                 list_filename: str = "static/database/mazes_list.json"):
        """Load a new sequence from the database.

        :param options_filename: path for web options
        :param list_filename: path for already stored maze representations
        """
        self.lock = Lock()
        with open(options_filename, encoding="utf-8") as opt_f:
            options_dct = json.load(opt_f)
        for key in options_dct:
            self.__dict__[key] = options_dct[key]
        with open(list_filename, encoding="utf-8") as list_f:
            self.mazes_list = json.load(list_f)
        self.list_filename = list_filename
        self._names = None

    def get_context(self) -> dict:
        """Get context for web page."""
        return self.__dict__

    @staticmethod
    def _filter_condition(elem: dict, filters: Collection) -> bool:
        """Filter through conditions.

        :param elem: current maze
        :param filters: a collection of all filters
        :return: True if at least one filter works, False otherwise
        """
        for filt in filters:
            if filt in elem.keys() or filt in elem.values():
                return True
        return False

    def sort_by_key(self, filters: dict) -> Collection:
        """Sort filtered mazes by key.

        :param filters: key and filters
        :return: a sorted collection
        """
        # pop the key
        key = filters.pop("sort_option")
        with self.lock:
            if not filters:
                return sorted(self.mazes_list,
                              key=lambda x: x["parameters"][key],
                              reverse=self.keys_to_reversed[key])
            filtered = filter(lambda x: self._filter_condition(x["parameters"],
                                                               filters),
                              self.mazes_list)
        return sorted(filtered, key=lambda x: x["parameters"][key],
                      reverse=self.keys_to_reversed[key])

    def save(self):
        """Save mazes to database."""
        with self.lock:
            with open(self.list_filename,
                      mode="w+", encoding="utf-8") as list_f:
                json.dump(self.mazes_list, list_f)

    @property
    def names(self) -> set:
        """Get all mazes' names."""
        if self._names:
            return self._names
        self._names = set(map(lambda x: x["name"].split("-")[0],
                              self.mazes_list))
        return self._names

    @names.setter
    def names(self, value: str):
        """Add a new name to names."""
        if self._names is None:
            pass
        self._names.add(value)
