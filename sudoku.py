from main import GameEngine, GridState, GridMove


class SudokuState(GridState):
    def __init__(self, starting_grid) -> None:
        super().__init__(size=9, max_value=9, box_size=3, starting_state=starting_grid)

    def copy(self):
        return SudokuState([row[:] for row in self.data])

    def _generate_plausible_moves_for_cell(self, row: int, col: int) -> list[GridMove]:
        options = [True] * 9
        for cell in self.row(row):
            if cell is not None:
                options[cell - 1] = False
        for cell in self.column(col):
            if cell is not None:
                options[cell - 1] = False
        for cell in self.box(row // 3, col // 3):
            if cell is not None:
                options[cell - 1] = False
        return [
            GridMove(row, col, value)
            for value, can_place in enumerate(options, start=1)
            if can_place
        ]


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
    game_engine = GameEngine(sudoku_state)
    print(sudoku_state)
    solution = game_engine.solve()
    print(solution)
