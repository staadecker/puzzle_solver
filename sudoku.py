from main import GameRules, GameEngine, GridState, Move, ConstraintNoDuplicates
from typing import Iterable


class SudokuState(GridState):
    def __init__(self, starting_grid) -> None:
        super().__init__(size=9, box_size=3)
        self.data = starting_grid


class SudokuMovePlace(Move):
    def __init__(self, row: int, col: int, value: int):
        super().__init__()
        self.row = row
        self.col = col
        self.value = value

    def _play(self, state: SudokuState) -> None:
        state.data[self.row][self.col] = self.value

    def _undo(self, state: SudokuState) -> None:
        state.data[self.row][self.col] = None


class SudokuRules(GameRules):
    def __init__(self) -> None:
        constraints = (
            [
                ConstraintNoDuplicates(
                    state_to_values=lambda state, r=row: state.row(r), name=f"Row {row}"
                )
                for row in range(9)
            ]
            + [
                ConstraintNoDuplicates(
                    state_to_values=lambda state, col=col: state.column(col),
                    name=f"Column {col}",
                )
                for col in range(9)
            ]
            + [
                ConstraintNoDuplicates(
                    state_to_values=lambda state,
                    box_row=box_row,
                    box_col=box_col: state.box(box_row, box_col),
                    name=f"Box {box_row}, {box_col}",
                )
                for box_row in range(3)
                for box_col in range(3)
            ]
        )
        super().__init__(constraints)

    def _generate_moves(self, state: SudokuState) -> Iterable[list[Move]]:
        for row in range(9):
            for col in range(9):
                if state.data[row][col] is None:
                    move_options = []
                    for value in range(1, 10):
                        move_options.append(SudokuMovePlace(row, col, value))
                    yield move_options

    def is_solved(self, state: SudokuState) -> bool:
        return all(cell is not None for row in state.data for cell in row)


if __name__ == "__main__":
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
    sudoku_rules = SudokuRules()
    game_engine = GameEngine(sudoku_state, sudoku_rules)
    solution = game_engine.solve()
    solution.print()
