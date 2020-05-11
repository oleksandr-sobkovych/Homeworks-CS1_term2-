""""""
from flask import request, jsonify, make_response, Flask, render_template
from modules.maze_operations.maze_adt import Maze
from modules.maze_operations.process_maze import Processor
from modules.helper_collections.llistqueue import Queue


MAZE_CONTEXT_DATA = {
    'construct_types': [
        ['construct_maze_api', 'Maze API',
         'Set API parameters and hit Create button'],
        ['construct_editor', 'Editor',
         'Build your own maze and hit Create button'],
    ],
    'api_options': [
        {'api_maze_size': {'title': 'Maze Size',
                           'data': [
                               ['10x10', '10 x 10'],
                               ['20x20', '20 x 20'],
                               ['30x30', '30 x 30'],
                           ]
                           }
        },
        {
            'api_algorithm': {
                'title': 'API Algorithm',
                'data': [
                    ['api_alg_qsort', 'Quick Sort'],
                    ['api_alg_bubble_sort', 'Bubble Sort'],
                ]
            }
        },
        {
            'api_length': {
                'title': 'Solution length',
            }
        },
        {
            'api_maze_id': {
                'title': 'Maze ID',
            }
        },
    ],
    'sort_keys': [
        ['time', 'Time'],
        ['optimality', 'Optimality'],
    ],
    'filters_set': [
        [['filter_id_1', 'Filter-1'], ['filter_id_2', 'Filter-2']],
        [['filter_id_3', 'Filter-3'], ['filter_id_4', 'Filter-4']],
        [['filter_id_5', 'Filter-5'], ['filter_id_6', 'Filter-6']],
        [['filter_id_7', 'Filter-7'], ['filter_id_8', 'Filter-8']],
    ],
    'mazes_list': [
        {
            'name': 'My Super Pupper maze 1',
            'parameters': [
                ['Param Name 1', 'Value 1'],
                ['Param Name 2', 'Value 2'],
                ['Param Name 3', 'Value 3'],
                ['Param Name 4', 'Value 4'],
                ['Param Name 5', 'Value 5'],
                ['Param Name 6', 'Value 6'],
                ['Param Name 7', 'Value 7'],
                ['Param Name 8', 'Value 8'],
            ],
            'performance': 'img/graph-1.png',
            'image': 'img/maze-1.png'
        },
        {
            'name': 'My Super Pupper maze 2',
            'parameters': [
                ['Param Name 1', 'Value 1'],
                ['Param Name 2', 'Value 2'],
                ['Param Name 3', 'Value 3'],
                ['Param Name 4', 'Value 4'],
                ['Param Name 5', 'Value 5'],
                ['Param Name 6', 'Value 6'],
                ['Param Name 7', 'Value 7'],
                ['Param Name 8', 'Value 8'],
            ],
            'performance': 'img/graph-1.png',
            'image': 'img/maze-1.png'
        },
        {
            'name': 'My Super Pupper maze 3',
            'parameters': [
                ['Param Name 1', 'Value 1'],
                ['Param Name 2', 'Value 2'],
                ['Param Name 3', 'Value 3'],
                ['Param Name 4', 'Value 4'],
                ['Param Name 5', 'Value 5'],
                ['Param Name 6', 'Value 6'],
                ['Param Name 7', 'Value 7'],
                ['Param Name 8', 'Value 8'],
            ],
            'performance': 'static/img/graph-1.png',
            'image': 'static/img/maze-1.png'
        },
    ]
}
app = Flask(__name__)


@app.route("/", methods=["GET"])
def render_main_page():
    """"""
    return render_template("index.html", **MAZE_CONTEXT_DATA)


@app.route("/stats.html", methods=["GET"])
def render_stats_page():
    """"""
    return render_template("stats.html", **MAZE_CONTEXT_DATA)


@app.route("/filter/", methods=["POST"])
def get_stats():
    """"""
    req = request.get_json()
    print(req)
    return "res"


@app.route("/api/", methods=["POST"])
def handle_api_request():
    """"""
    req = request.get_json()
    print(req)
    # print(Maze.from_api(**req).array)

    res = make_response(jsonify({"message": "OK"}), 200)

    return res


@app.route("/editor/", methods=["POST"])
def handle_editor_request():
    """"""
    global queue
    req = request.get_json()
    print(req)
    queue.push(Maze(**req))
    res = make_response(jsonify({"message": "OK"}), 200)

    return res


if __name__ == '__main__':
    queue = Queue()
    Processor(queue).start()
    print("ready")
    app.run(debug=False)
