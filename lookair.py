# Rules for Lookair: https://puzz.link/rules.html?lookair

from typing import Iterable, Optional, Self
from main import Move, ShadedGridState, GameEngine, GridMove
from util import concat_str_horizontally, grid_data_to_str


class LookairState(ShadedGridState):
    def __init__(
        self, size: int, numbers_and_pos: dict[tuple[int, int], int], data=None
    ) -> None:
        super().__init__(size=size, starting_state=data)
        self.numbers_and_pos = numbers_and_pos

    def __str__(self) -> str:
        shaded_grid = super().__str__()
        number_grid = [
            [str(self.numbers_and_pos.get((row, col), " ")) for col in range(self.size)]
            for row in range(self.size)
        ]
        return concat_str_horizontally(
            grid_data_to_str(number_grid), shaded_grid, f"(move {self.moves_played})"
        )

    def copy(self):
        copy_state = LookairState(
            size=self.size,
            numbers_and_pos=self.numbers_and_pos,
            data=[row[:] for row in self.data],
        )
        copy_state.moves_played = self.moves_played
        return copy_state

    def generate_legal_moves(self) -> list[list[Move[Self]]]:
        moves = self._generate_moves()
        if moves == []:
            return []
        if self.moves_played != self.size * self.size - 1:
            return moves

        # Otherwise, it's the last move, we must ensure legality
        assert len(moves) == 1, "There should only be one cell left to fill."
        for move in moves[0]:
            potential_end_state = self.copy()
            move.play(potential_end_state)
            if potential_end_state.is_legal_solution():
                return [[move]]
        return []

    def is_legal_solution(self) -> bool:
        # Check numbers rule
        for (row, col), number in self.numbers_and_pos.items():
            neighbors = self.neighbors(row, col) + [self.data[row][col]]
            shaded_count = sum(v == self.SHADED for v in neighbors)
            if shaded_count != number:
                return False

        # Check all squares
        checked = set()
        for row, col, value in self.iter_cells():
            if value != self.SHADED or (row, col) in checked:
                continue
            max_row, max_col = self._get_rect_extent(row, col)
            height = max_row - row + 1
            width = max_col - col + 1
            if height != width:
                return False
            for r, c, v in self._iter_rect(row, col, max_row, max_col):
                if v != self.SHADED:
                    return False
                checked.add((r, c))

        # Check line of sight rule
        squares = self._find_rect()
        squares_by_size = {s: [] for s in range(1, self.size + 1)}

        for top, left, bottom, right in squares:
            size = bottom - top + 1
            squares_by_size[size].append((top, left, bottom, right))

        for size, squares_of_size in squares_by_size.items():
            squares_by_row = {r: [] for r in range(self.size)}
            squares_by_col = {c: [] for c in range(self.size)}
            for top, left, bottom, right in squares_of_size:
                squares_by_row[top].append((top, left, bottom, right))
                squares_by_col[left].append((top, left, bottom, right))

            for row, squares_in_row in squares_by_row.items():
                if len(squares_in_row) <= 1:
                    continue
                squares_by_row = sorted(squares_in_row, key=lambda s: s[1])
                for i in range(len(squares_by_row) - 1):
                    first = squares_by_row[i]
                    second = squares_by_row[i + 1]

                    for _, _, val in self._iter_rect(
                        first[0], first[3] + 1, first[2], second[1] - 1
                    ):
                        if val == self.SHADED:
                            break
                    else:
                        return False
            for col, squares_in_col in squares_by_col.items():
                if len(squares_in_col) <= 1:
                    continue
                squares_by_col = sorted(squares_in_col, key=lambda s: s[0])
                for i in range(len(squares_by_col) - 1):
                    first = squares_by_col[i]
                    second = squares_by_col[i + 1]

                    for _, _, val in self._iter_rect(
                        first[2] + 1, first[1], second[0] - 1, first[3]
                    ):
                        if val == self.SHADED:
                            break
                    else:
                        return False
        return True

    def _generate_moves(self) -> list[list[GridMove[Self]]]:
        forced_moves = self.find_forced_fill_rect_moves()
        if forced_moves is not None:
            return forced_moves
        forced_moves = self.find_forced_rect_to_square_moves()
        if forced_moves is not None:
            return forced_moves
        forced_moves = self.find_forced_numbers()
        if forced_moves is not None:
            return forced_moves

        return [
            [GridMove(row, col, value) for value in (self.SHADED, self.UNSHADED)]
            for row, col, cell_value in self.iter_cells()
            if cell_value is None
        ]

    def find_forced_fill_rect_moves(self) -> list[list[GridMove]] | None:
        cells_checked = set()
        for row, col, value in self.iter_cells():
            if (row, col) in cells_checked or value != self.SHADED:
                continue

            max_row, max_col = self._get_rect_extent(row, col)
            for r, c, val in self._iter_rect(row, col, max_row, max_col):
                if val == self.UNSHADED:
                    return []  # illegal state
                elif val is None:
                    return [[GridMove(r, c, self.SHADED)]]  # forced move
                elif val == self.SHADED:
                    cells_checked.add((r, c))
                else:
                    raise ValueError("Unexpected cell value")

    def find_forced_rect_to_square_moves(self) -> list[list[GridMove]] | None:
        rectangles = self._find_rect()

        for row, col, end_row, end_col in rectangles:
            height = end_row - row + 1
            width = end_col - col + 1
            if height == width:
                continue  # already a square
            if height < width:
                can_fill_top_row = row > 0 and all(
                    self.data[row - 1][c] is None for c in range(col, end_col + 1)
                )
                can_fill_bottom_row = end_row + 1 < self.size and all(
                    self.data[end_row + 1][c] is None for c in range(col, end_col + 1)
                )

                if not can_fill_top_row and not can_fill_bottom_row:
                    return []  # illegal state
                if can_fill_top_row and not can_fill_bottom_row:
                    return [[GridMove(row - 1, col, self.SHADED)]]
                if not can_fill_top_row and can_fill_bottom_row:
                    return [[GridMove(end_row + 1, col, self.SHADED)]]
            if width < height:
                can_fill_left_col = col > 0 and all(
                    self.data[r][col - 1] is None for r in range(row, end_row + 1)
                )
                can_fill_right_col = end_col + 1 < self.size and all(
                    self.data[r][end_col + 1] is None for r in range(row, end_row + 1)
                )

                if not can_fill_left_col and not can_fill_right_col:
                    return []  # illegal state
                if can_fill_left_col and not can_fill_right_col:
                    return [[GridMove(row, col - 1, self.SHADED)]]
                if not can_fill_left_col and can_fill_right_col:
                    return [[GridMove(row, end_col + 1, self.SHADED)]]

    def find_forced_numbers(self) -> list[list[GridMove]] | None:
        for (row, col), number in self.numbers_and_pos.items():
            neighbors = self.neighbors(row, col, with_pos=True) + [
                (row, col, self.data[row][col])
            ]
            min_shaded = sum(v == self.SHADED for _, _, v in neighbors)
            max_shaded = min_shaded + sum(v is None for _, _, v in neighbors)
            if not (min_shaded <= number <= max_shaded):
                return []  # illegal state

            if min_shaded == number and max_shaded > number:
                must_not_shade = [n for n in neighbors if n[2] is None][0]
                return [[GridMove(must_not_shade[0], must_not_shade[1], self.UNSHADED)]]
            if max_shaded == number and min_shaded < number:
                must_shade = [n for n in neighbors if n[2] is None][0]
                return [[GridMove(must_shade[0], must_shade[1], self.SHADED)]]

        return None

    def _find_rect(self) -> list[tuple[int, int, int, int]]:
        rect = []

        for row, col, value in self.iter_cells():
            if value != self.SHADED:
                continue
            if row > 0 and self.data[row - 1][col] == self.SHADED:
                continue
            if col > 0 and self.data[row][col - 1] == self.SHADED:
                continue
            right_edge = col
            bottom_edge = row
            while (
                right_edge + 1 < self.size
                and self.data[row][right_edge + 1] == self.SHADED
            ):
                right_edge += 1
            while (
                bottom_edge + 1 < self.size
                and self.data[bottom_edge + 1][col] == self.SHADED
            ):
                bottom_edge += 1

            rect.append((row, col, bottom_edge, right_edge))

        return rect

    def _follow_dir(
        self, start_row, start_col, direction
    ) -> Iterable[tuple[int, int, Optional[int]]]:
        dr, dc = direction
        while True:
            start_row += dr
            start_col += dc
            if not (0 <= start_row < self.size and 0 <= start_col < self.size):
                break
            yield (start_row, start_col, self.data[start_row][start_col])

    def _near_square(
        self, row: int, col: int, square: tuple[int, int, int, int]
    ) -> bool:
        top, left, bottom, right = square
        return (top - 1 <= row <= bottom + 1 and left <= col <= right) or (
            left - 1 <= col <= right + 1 and top <= row <= bottom
        )

    def _get_rect_extent(self, start_row, start_col) -> tuple[int, int]:
        explored = set()
        unexplored = [(start_row, start_col)]

        while unexplored:
            to_explore = unexplored.pop()
            explored.add(to_explore)
            for r, c, val in self.neighbors(
                to_explore[0],
                to_explore[1],
                with_pos=True,
                directions=(self.DOWN, self.RIGHT),
            ):
                if (r, c) not in explored and val == self.SHADED:
                    unexplored.append((r, c))

        max_row = max(explored, key=lambda x: x[0])[0]
        max_col = max(explored, key=lambda x: x[1])[1]
        return max_row, max_col


if __name__ == "__main__":
    test_problem = LookairState(
        size=6,
        numbers_and_pos={
            (0, 0): 3,
            (1, 0): 3,
            (1, 3): 3,
            (2, 5): 1,
            (3, 1): 2,
            (4, 1): 0,
            (4, 3): 2,
            (5, 1): 1,
        },
    )

    print(GameEngine(test_problem).solve())
