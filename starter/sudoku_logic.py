import copy
import random

SIZE = 9
EMPTY = 0

def deep_copy(board):
    return copy.deepcopy(board)

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True

def remove_cells(board, clues):
    if not 17 <= clues <= SIZE * SIZE:
        raise ValueError("clues must be between 17 and 81")
    if sum(value != EMPTY for row in board for value in row) != SIZE * SIZE:
        raise ValueError("board must be a complete solution")
    if count_solutions(board) != 1:
        raise ValueError("board must be a valid solution")

    cells = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(cells)
    removed = 0
    for row, col in cells:
        if SIZE * SIZE - removed <= clues:
            break
        value = board[row][col]
        board[row][col] = EMPTY
        if count_solutions(board) == 1:
            removed += 1
        else:
            board[row][col] = value


def _has_consistent_clues(board):
    if (
        not isinstance(board, list)
        or len(board) != SIZE
        or any(not isinstance(row, list) or len(row) != SIZE for row in board)
    ):
        return False

    rows = [set() for _ in range(SIZE)]
    columns = [set() for _ in range(SIZE)]
    boxes = [set() for _ in range(SIZE)]
    for row in range(SIZE):
        for col in range(SIZE):
            value = board[row][col]
            if (
                not isinstance(value, int)
                or isinstance(value, bool)
                or not 0 <= value <= SIZE
            ):
                return False
            if value == EMPTY:
                continue
            box = (row // 3) * 3 + col // 3
            if value in rows[row] or value in columns[col] or value in boxes[box]:
                return False
            rows[row].add(value)
            columns[col].add(value)
            boxes[box].add(value)
    return True


def _count_solutions(board, limit):
    """Count solutions up to limit, using the most constrained empty cell."""
    best_cell = None
    best_candidates = None

    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] != EMPTY:
                continue
            candidates = [
                value for value in range(1, SIZE + 1)
                if is_safe(board, row, col, value)
            ]
            if not candidates:
                return 0
            if best_candidates is None or len(candidates) < len(best_candidates):
                best_cell = (row, col)
                best_candidates = candidates
                if len(candidates) == 1:
                    break
        if best_candidates is not None and len(best_candidates) == 1:
            break

    if best_cell is None:
        return 1

    row, col = best_cell
    solutions = 0
    for candidate in best_candidates:
        board[row][col] = candidate
        solutions += _count_solutions(board, limit - solutions)
        board[row][col] = EMPTY
        if solutions >= limit:
            break
    return solutions


def count_solutions(board, limit=2):
    """Count valid solutions up to limit; contradictory clues have no solutions."""
    if limit < 1 or not _has_consistent_clues(board):
        return 0
    return _count_solutions(board, limit)


def generate_puzzle(clues=35):
    if not 17 <= clues <= SIZE * SIZE:
        raise ValueError("clues must be between 17 and 81")

    board = create_empty_board()
    if not fill_board(board):
        raise RuntimeError("Could not generate a complete Sudoku solution.")
    solution = deep_copy(board)

    remove_cells(board, clues)

    puzzle = deep_copy(board)
    return puzzle, solution
