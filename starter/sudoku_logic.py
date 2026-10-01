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
    attempts = SIZE * SIZE - clues
    while attempts > 0:
        row = random.randrange(SIZE)
        col = random.randrange(SIZE)
        if board[row][col] != EMPTY:
            board[row][col] = EMPTY
            attempts -= 1


def count_solutions(board, limit=2):
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
        solutions += count_solutions(board, limit - solutions)
        board[row][col] = EMPTY
        if solutions >= limit:
            break
    return solutions


def generate_puzzle(clues=35):
    if not 17 <= clues <= SIZE * SIZE:
        raise ValueError("clues must be between 17 and 81")

    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)

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

    puzzle = deep_copy(board)
    return puzzle, solution
