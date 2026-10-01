import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import app as sudoku_app
import sudoku_logic


@pytest.fixture

def client():
    sudoku_app.app.config.update(TESTING=True, SECRET_KEY="test-secret")
    sudoku_app.GAMES.clear()
    with sudoku_app.app.test_client() as test_client:
        yield test_client
    sudoku_app.GAMES.clear()


def test_home_page_renders_sudoku_controls(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"sudoku-board" in response.data
    assert b"difficulty" in response.data
    assert b"check-solution" in response.data


def test_new_game_returns_difficulty_and_valid_unique_puzzle(client):
    response = client.get("/new?difficulty=easy")
    payload = response.get_json()
    puzzle = payload["puzzle"]

    assert response.status_code == 200
    assert payload["difficulty"] == "easy"
    assert sum(value != sudoku_logic.EMPTY for row in puzzle for value in row) >= 40
    assert sudoku_logic.count_solutions(sudoku_logic.deep_copy(puzzle)) == 1


def test_new_game_rejects_unknown_difficulty(client):
    response = client.get("/new?difficulty=expert")

    assert response.status_code == 400
    assert "error" in response.get_json()


@pytest.mark.parametrize(("difficulty", "clue_count"), [("easy", 40), ("medium", 34), ("hard", 28)])
def test_difficulty_sets_exact_clue_count(client, difficulty, clue_count):
    payload = client.get(f"/new?difficulty={difficulty}").get_json()

    assert sum(value != sudoku_logic.EMPTY for row in payload["puzzle"] for value in row) == clue_count


def test_check_accepts_the_generated_solution(client):
    client.get("/new?difficulty=medium")
    with client.session_transaction() as browser_session:
        game = sudoku_app.GAMES[browser_session["game_id"]]

    response = client.post("/check", json={"board": game["solution"]})

    assert response.status_code == 200
    assert response.get_json() == {"incorrect": [], "solved": True}


def test_check_treats_empty_cells_as_incomplete_not_incorrect(client):
    client.get("/new?difficulty=easy")
    with client.session_transaction() as browser_session:
        game = sudoku_app.GAMES[browser_session["game_id"]]

    response = client.post("/check", json={"board": game["puzzle"]})

    assert response.status_code == 200
    assert response.get_json() == {"incorrect": [], "solved": False}


def test_hint_returns_correct_value_for_empty_cell(client):
    client.get("/new?difficulty=easy")
    with client.session_transaction() as browser_session:
        game = sudoku_app.GAMES[browser_session["game_id"]]
    puzzle = game["puzzle"]

    response = client.post("/hint", json={"board": puzzle})
    hint = response.get_json()

    assert response.status_code == 200
    assert puzzle[hint["row"]][hint["col"]] == sudoku_logic.EMPTY
    assert hint["value"] == game["solution"][hint["row"]][hint["col"]]
    assert hint["hints"] == 1


def test_hint_locks_revealed_cell(client):
    client.get("/new?difficulty=easy")
    with client.session_transaction() as browser_session:
        game = sudoku_app.GAMES[browser_session["game_id"]]
    puzzle = sudoku_logic.deep_copy(game["puzzle"])
    hint = client.post("/hint", json={"board": puzzle}).get_json()
    puzzle[hint["row"]][hint["col"]] = hint["value"] % sudoku_logic.SIZE + 1

    response = client.post("/check", json={"board": puzzle})

    assert response.status_code == 400
    assert "Hinted cells" in response.get_json()["error"]


def test_check_rejects_malformed_board(client):
    client.get("/new?difficulty=easy")

    response = client.post("/check", json={"board": [[0]]})

    assert response.status_code == 400


def test_home_page_has_controls_for_required_features(client):
    response = client.get("/")

    assert b'id="hint-button"' in response.data
    assert b'id="timer"' in response.data
    assert b'id="theme-toggle"' in response.data
    assert b'id="score-list"' in response.data
