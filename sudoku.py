from main import GameRules, GameEngine, GridState, Move
import dataclasses


class SudokuState(GridState):
    def __init__(self, starting_grid) -> None:
        super().__init__(size=9, box_size=3)
        self.grid = starting_grid


@dataclasses.dataclass
class SudokuMovePlace:
    row: int
    col: int
    value: int

    def play(self, state: SudokuState) -> None:
        state.grid[self.row][self.col] = self.value

    def undo(self, state: SudokuState) -> None:
        state.grid[self.row][self.col] = None


class SudokuRules(GameRules):
    def generate_moves(self, data: SudokuState) -> list[list[Move]]:
        moves = []
        for row in range(9):
            for col in range(9):
                if data.grid[row][col] is None:
                    move_options = []
                    for value in range(1, 10):
                        move_options.append(SudokuMovePlace(row, col, value))
                    moves.append(move_options)

        return moves

    def is_legal(self, data: SudokuState) -> bool:
        def has_duplicates(lst):
            seen = set()
            for item in lst:
                if item is not None:
                    if item in seen:
                        return True
                    seen.add(item)
            return False

        for row in data.grid:
            if has_duplicates(row):
                return False

        for col in range(9):
            if has_duplicates(data.grid[row][col] for row in range(9)):
                return False

        for box_row in range(3):
            for box_col in range(3):
                box = []
                for i in range(3):
                    for j in range(3):
                        box.append(data.grid[box_row * 3 + i][box_col * 3 + j])
                if has_duplicates(box):
                    return False

        return True

    def is_solved(self, data: SudokuState) -> bool:
        for row in data.grid:
            if any(cell is None for cell in row):
                return False
        return True


if __name__ == "__main__":
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
    sudoku_rules = SudokuRules()
    game_engine = GameEngine(sudoku_state, sudoku_rules)
    game_engine.solve()
    game_engine.state.print()
