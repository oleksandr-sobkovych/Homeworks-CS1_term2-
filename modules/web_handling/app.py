""""""
from flask import request, jsonify, make_response, Flask, render_template,\
    session
from flask_session import Session
from modules.maze_operations.maze_adt import Maze, MazeUnsolvableError, \
    MazeNameError, MazeConstructionError
from modules.maze_operations.process_maze import BackgroundProcessor
from modules.helper_collections.llistqueue import Queue
from modules.maze_operations.maze_list import MazesList


app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/", methods=["GET"])
def render_main_page():
    """Render the main page on GET request."""
    global maze_list
    return render_template("index.html",
                           **maze_list.get_context())


@app.route("/stats.html", methods=["GET"])
def render_stats_page():
    """"""
    global maze_list
    if session.get("mazes") is None:
        session["mazes"] = maze_list.get_current_mazes()
    if request.args:
        session["mazes"] = maze_list.sort_by_key(request.args["sort_option"],
                                dict(request.args))
    return render_template("stats.html",
                           **maze_list.get_context(), mazes=session["mazes"])


@app.route("/api/", methods=["POST"])
def handle_api_request():
    """"""
    global queue
    req = request.get_json()
    print(req)
    try:
        maze = Maze.from_api(**req)
    except MazeConstructionError:
        res = make_response(jsonify({"message":
                                     "API does not support this data "
                                     "combination"}), 422)
    except MazeNameError:
        res = make_response(jsonify({"message": "Name should contain only "
                                                "A-Z, a-z and _"}), 422)
    except MazeUnsolvableError:
        res = make_response(jsonify({"message": "Should be solvable"}), 422)
    else:
        res = make_response(jsonify({"message": "OK"}), 200)
        queue.push(maze)
    return res


@app.route("/editor/", methods=["POST"])
def handle_editor_request():
    """"""
    global queue
    req = request.get_json()
    print(req)
    try:
        maze = Maze(**req)
    except MazeNameError:
        res = make_response(jsonify({"message": "Name should contain only "
                                                "A-Z, a-z and _"}), 422)
    except MazeUnsolvableError:
        res = make_response(jsonify({"message": "Should be solvable"}), 422)
    else:
        res = make_response(jsonify({"message": "OK"}), 200)
        queue.push(maze)
    return res


if __name__ == '__main__':
    maze_list = MazesList()
    queue = Queue()
    BackgroundProcessor(queue, maze_list).start()
    print(maze_list.mazes_list)
    app.run()
