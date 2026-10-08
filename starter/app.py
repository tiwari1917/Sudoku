import os
import secrets
import uuid

from flask import Flask, jsonify, render_template, request, session
import sudoku_logic

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(32))

DIFFICULTIES = {"easy": 40, "medium": 34, "hard": 28}
GAMES = {}


def _read_board(value):
    if not isinstance(value, list) or len(value) != sudoku_logic.SIZE:
        return None
    if any(not isinstance(row, list) or len(row) != sudoku_logic.SIZE for row in value):
        return None
    if any(
        not isinstance(cell, int) or isinstance(cell, bool) or not 0 <= cell <= sudoku_logic.SIZE
        for row in value
        for cell in row
    ):
        return None
    return value


def _current_game():
    game_id = session.get("game_id")
    return GAMES.get(game_id)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    difficulty = request.args.get("difficulty", "medium").lower()
    clues = DIFFICULTIES.get(difficulty)
    if clues is None:
        return jsonify({"error": "Difficulty must be easy, medium, or hard."}), 400

    puzzle, solution = sudoku_logic.generate_puzzle(clues)
    game_id = str(uuid.uuid4())
    GAMES[game_id] = {
        "puzzle": puzzle,
        "solution": solution,
        "difficulty": difficulty,
        "hints": 0,
        "revealed": set(),
    }
    session["game_id"] = game_id
    return jsonify({"puzzle": puzzle, "difficulty": difficulty})


@app.route("/hint", methods=["POST"])
def give_hint():
    game = _current_game()
    if game is None:
        return jsonify({"error": "No game in progress."}), 400

    data = request.get_json(silent=True)
    board = _read_board(data.get("board") if isinstance(data, dict) else None)
    if board is None:
        return jsonify({"error": "Board must be a 9 by 9 grid of values from 0 to 9."}), 400

    puzzle = game["puzzle"]
    solution = game["solution"]
    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            if puzzle[row][col] and board[row][col] != puzzle[row][col]:
                return jsonify({"error": "Prefilled cells cannot be changed."}), 400
            if (row, col) in game["revealed"] and board[row][col] != solution[row][col]:
                return jsonify({"error": "Hinted cells cannot be changed."}), 400

    empty_cells = [
        (row, col)
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
        if board[row][col] == sudoku_logic.EMPTY and (row, col) not in game["revealed"]
    ]
    if not empty_cells:
        return jsonify({"error": "There are no empty cells to hint."}), 400

    row, col = secrets.choice(empty_cells)
    game["revealed"].add((row, col))
    game["hints"] += 1
    return jsonify({
        "row": row,
        "col": col,
        "value": solution[row][col],
        "hints": game["hints"],
    })


@app.route('/check', methods=['POST'])
def check_solution():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "A JSON board is required."}), 400
    board = _read_board(data.get("board"))
    if board is None:
        return jsonify({"error": "Board must be a 9 by 9 grid of values from 0 to 9."}), 400

    game = _current_game()
    if game is None:
        return jsonify({"error": "No game in progress."}), 400

    puzzle = game["puzzle"]
    solution = game["solution"]
    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            if puzzle[row][col] and board[row][col] != puzzle[row][col]:
                return jsonify({"error": "Prefilled cells cannot be changed."}), 400
            if (row, col) in game["revealed"] and board[row][col] != solution[row][col]:
                return jsonify({"error": "Hinted cells cannot be changed."}), 400

    incorrect = []
    complete = True
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] == sudoku_logic.EMPTY:
                complete = False
            elif board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    return jsonify({"incorrect": incorrect, "solved": complete and not incorrect})

if __name__ == '__main__':
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")