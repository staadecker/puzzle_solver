from sudoku import SudokuState
from main import GameEngine


def test_easy():
    sudoku_state = SudokuState(
        [
            [None, None, 9, 2, 1, 8, None, None, None],
            [1, 7, None, None, 9, 6, 8, None, None],
            [None, 4, None, None, 5, None, None, None, 6],
            [4, 5, 1, None, 6, None, 3, 7, None],
            [None, None, None, None, None, 5, None, None, 9],
            [9, None, 2, 3, 7, None, 5, None, None],
            [6, None, None, 5, None, 1, None, None, None],
            [None, None, None, None, 4, 9, 2, 5, 7],
            [None, 9, 4, 8, None, None, None, 1, 3],
        ]
    )
    game_engine = GameEngine(sudoku_state)
    result = game_engine.solve()

    assert result.data == [
        [3, 6, 9, 2, 1, 8, 7, 4, 5],
        [1, 7, 5, 4, 9, 6, 8, 3, 2],
        [2, 4, 8, 7, 5, 3, 1, 9, 6],
        [4, 5, 1, 9, 6, 2, 3, 7, 8],
        [7, 3, 6, 1, 8, 5, 4, 2, 9],
        [9, 8, 2, 3, 7, 4, 5, 6, 1],
        [6, 2, 7, 5, 3, 1, 9, 8, 4],
        [8, 1, 3, 6, 4, 9, 2, 5, 7],
        [5, 9, 4, 8, 2, 7, 6, 1, 3],
    ]


def test_medium():
    sudoku_state = SudokuState(
        [
            [6, 3, 4, 2, None, 7, 8, None, 5],
            [None, None, None, 8, None, 4, None, 3, None],
            [5, 2, None, 9, None, 6, 1, 4, 7],
            [None, None, None, None, None, 5, None, 1, None],
            [8, 5, None, None, 7, 3, None, None, None],
            [4, None, 9, None, 2, None, 7, None, None],
            [None, None, None, None, None, 2, 5, None, 9],
            [None, 9, None, None, 4, None, None, None, None],
            [3, None, 5, None, None, None, None, 2, 1],
        ]
    )
    game_engine = GameEngine(sudoku_state)
    result = game_engine.solve()
    result.print()
    assert result.data == [
        [6, 3, 4, 2, 1, 7, 8, 9, 5],
        [9, 7, 1, 8, 5, 4, 6, 3, 2],
        [5, 2, 8, 9, 3, 6, 1, 4, 7],
        [7, 6, 3, 4, 9, 5, 2, 1, 8],
        [8, 5, 2, 1, 7, 3, 9, 6, 4],
        [4, 1, 9, 6, 2, 8, 7, 5, 3],
        [1, 4, 6, 3, 8, 2, 5, 7, 9],
        [2, 9, 7, 5, 4, 1, 3, 8, 6],
        [3, 8, 5, 7, 6, 9, 4, 2, 1],
    ]


def test_extreme():
    sudoku_state = SudokuState(
        [
            [3, None, None, None, None, 8, None, None, 9],
            [7, None, None, 5, None, None, None, 2, None],
            [None, None, None, None, None, None, None, None, None],
            [None, 4, 6, None, None, None, None, None, None],
            [2, None, None, 1, None, None, None, 3, None],
            [None, None, 3, 8, None, None, 4, None, None],
            [8, None, None, None, None, 7, None, 5, None],
            [None, None, None, None, None, 6, None, 4, None],
            [6, 7, None, None, None, 9, 2, None, None],
        ]
    )
    game_engine = GameEngine(sudoku_state)
    result = game_engine.solve()
    result.print()
    assert result.data == [
        [3, 2, 5, 6, 4, 8, 7, 1, 9],
        [7, 6, 9, 5, 3, 1, 8, 2, 4],
        [4, 1, 8, 9, 7, 2, 5, 6, 3],
        [5, 4, 6, 7, 2, 3, 1, 9, 8],
        [2, 8, 7, 1, 9, 4, 6, 3, 5],
        [1, 9, 3, 8, 6, 5, 4, 7, 2],
        [8, 3, 2, 4, 1, 7, 9, 5, 6],
        [9, 5, 1, 2, 8, 6, 3, 4, 7],
        [6, 7, 4, 3, 5, 9, 2, 8, 1],
    ]
