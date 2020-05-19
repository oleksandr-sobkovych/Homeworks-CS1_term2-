""""""
import json
from threading import Lock


class MazesList:
    """"""

    def __init__(self, options_filename: str = "static/database/options.json",
                 list_filename: str = "static/database/mazes_list.json"):
        self.lock = Lock()
        with open(options_filename, encoding="utf-8") as opt_f:
            options_dct = json.load(opt_f)
        for key in options_dct:
            self.__dict__[key] = options_dct[key]
        with open(list_filename, encoding="utf-8") as list_f:
            self.mazes_list = json.load(list_f)
        self.list_filename = list_filename

    def get_context(self):
        """"""
        return self.__dict__

    @staticmethod
    def _filter_condition(elem: dict, filters):
        """"""
        for filt in filters:
            if filt in elem.keys() or filt in elem.values():
                return True
        return False

    def sort_by_key(self, key: str, filters: list):
        """"""
        filters.pop("sort_option")
        with self.lock:
            filtered = filter(lambda x: self._filter_condition(x["parameters"],
                                                                   filters),
                              self.mazes_list)
        return sorted(filtered, key=lambda x: x["parameters"][key])

    def save(self):
        """"""
        with self.lock:
            with open(self.list_filename,
                      mode="w+", encoding="utf-8") as list_f:
                json.dump(self.mazes_list, list_f)

    def get_current_mazes(self):
        """"""
        with self.lock:
            return self.mazes_list
