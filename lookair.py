# Rules for Lookair: https://puzz.link/rules.html?lookair

from typing import Iterable, Iterator, Optional, Self
from main import Move, ShadedGridState, GameEngine, GridMove


class LookairState(ShadedGridState):
    def __init__(
        self,
        size: int,
        numbers_and_pos: dict[tuple[int, int], int],
        data=None,
    ) -> None:
        super().__init__(size=size, starting_state=data)
        self.numbers_and_pos = numbers_and_pos

    def copy(self):
        return LookairState(
            size=self.size,
            numbers_and_pos=self.numbers_and_pos,
            data=[row[:] for row in self.data],
        )

    def generate_legal_moves(self) -> list[list[Move[Self]]]:
        # Search for forced moves to fill in rectangles
        # cells_checked = set()
        # row, column = 0, 0
        # while row < self.size:
        #     if self.data[row][column] == 1 and (row, column) not in cells_checked:
        #         min_width, min_height = self._get_min_square_size(row, column)
        #         for dr in range(min_height):
        #             for dc in range(min_width):
        #                 r, c = row + dr, column + dc
        #                 if self.data[r][c] != 1:
        #                     assert self.data[r][c] is None, "Grid is already illegal!"
        #                     return [[GridMove(r, c, 1)]]
        #                 cells_checked.add((r, c))
        #         column += min_width
        #     else:
        #         column += 1
        #     if column >= self.size:
        #         row += 1
        #         column = 0

        # Then proceed cell-by-cell as normal
        return super().generate_legal_moves()

    def _calculate_squares(self) -> list[tuple[int, int, int, int]]:
        squares = []

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

            squares.append((row, col, bottom_edge, right_edge))

        return squares

    def _generate_square_starter_moves(
        self, squares: list[tuple[int, int, int, int]]
    ) -> Iterable[list[GridMove]]:
        is_valid = [[True] * self.size for _ in range(self.size)]

        # exclude cells that are already filled or near existing squares
        for row, col, value in self.iter_cells():
            if value is not None:
                is_valid[row][col] = False
            for square in squares:
                if self._near_square(row, col, square):
                    is_valid[row][col] = False

        # exclude cells that would violate line of sight rules
        for square in squares:
            size = square[2] - square[0] + 1
            if size != 1:
                continue
            for dir in self.DIRECTIONS:
                for r, c, val in self._follow_dir(square[0], square[1], dir):
                    is_valid[r][c] = False
                    if val == self.SHADED:
                        break

        # exclude cells that would make it impossible to satisfy number constraints
        for (row, col), number in self.numbers_and_pos.items():
            neighbor_values = self.neighbors(row, col) + [self.data[row][col]]
            max_shaded = sum(
                v in (None, self.SHADED) for v in neighbor_values
            )
            if max_shaded == number:
                for r, c, _ in self._get_neighbor_numbers(row, col):
                    is_valid[r][c] = False

        return [
            [GridMove(r, c, self.SHADED)]
            for r in range(self.size)
            for c in range(self.size)
            if is_valid[r][c]
        ]

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

    def _generate_legal_moves_for_cell(self, row: int, col: int) -> list[GridMove]:
        moves = []
        if self._can_shade(row, col):
            moves.append(GridMove(row, col, 1))
        if self._can_not_shade(row, col):
            moves.append(GridMove(row, col, 2))
        return moves

    def _can_shade(self, row: int, col: int) -> bool:
        # check it will still be possible to satisfy number constraints
        for ng_row, ng_col, number in self._get_neighbor_numbers(row, col):
            neighbor_values = self.neighbors(ng_row, ng_col) + [
                self.data[ng_row][ng_col]
            ]
            num_shaded = sum(v == self.SHADED for v in neighbor_values)
            if num_shaded == number:
                return False

        # check it will still be possible to make squares
        # notice we know the grid must have only filled in rectangles so far
        start_row, start_col = row, col
        end_row, end_col = row, col
        for off_row, off_col in self.DIRECTIONS:
            if self.data[row + off_row][col + off_col] != self.SHADED:
                continue

            directions_to_follow = [(off_row, off_col)]
            directions_to_follow.extend(
                [self.UP, self.DOWN] if off_row == 0 else [self.LEFT, self.RIGHT]
            )

            shaded_cell = (row + off_row, col + off_col)

            for ddr, ddc in directions_to_follow:
                while True:
                    next_cell = (shaded_cell[0] + ddr, shaded_cell[1] + ddc)

                    if (
                        (0 <= next_cell[0] < self.size)
                        and (0 <= next_cell[1] < self.size)
                        and self.data[next_cell[0]][next_cell[1]] == self.SHADED
                    ):
                        shaded_cell = next_cell
                    else:
                        break

                start_row, start_col = (
                    min(start_row, shaded_cell[0]),
                    min(start_col, shaded_cell[1]),
                )
                end_row, end_col = (
                    max(end_row, shaded_cell[0]),
                    max(end_col, shaded_cell[1]),
                )

        if any(
            self.data[row][c] == self.UNSHADED for c in range(start_col, end_col + 1)
        ):
            return False
        if any(
            self.data[r][col] == self.UNSHADED for r in range(start_row, end_row + 1)
        ):
            return False

        if not self._square_could_exist(start_row, start_col, min_width, min_height):
            return False

    def _can_not_shade(self, row: int, col: int) -> bool:
        # check it will still be possible to satisfy number constraints
        for ng_row, ng_col, number in self._get_neighbor_numbers(row, col):
            neighbor_values = self.neighbors(ng_row, ng_col) + [
                self.data[ng_row][ng_col]
            ]

            max_shaded = sum(v in (None, 1) for v in neighbor_values)
            if max_shaded == number:
                return False
        return True

    def _get_neighbor_numbers(
        self, row: int, col: int
    ) -> Iterator[tuple[int, int, int]]:
        for ng_row, ng_col in self.neighbors_pos(row, col):
            if (ng_row, ng_col) in self.numbers_and_pos:
                yield (ng_row, ng_col, self.numbers_and_pos[(ng_row, ng_col)])

    def _can_make_squares(self) -> bool:
        squares_needed: list[list[tuple[int, int, int]]] = []
        size = self.size

        for row, col, value in self.iter_cells():
            if value != 1:
                continue

            min_width, min_height = self._get_min_square_size(row, col)

            if self._val_in_rect(row, col, min_width, min_height, val=2):
                return False

            expansion_needed = abs(min_width - min_height)
            if min_width != min_height:
                transpose = min_width > min_height
                # expand left first
                num_prior = 0
                root_index = col if not transpose else row
                while num_prior < expansion_needed:
                    check_index = root_index - 1 - num_prior
                    if check_index < 0 or self._val_in_rect(
                        row, check_index, 1, min_height, val=2
                    ):
                        break
                    num_prior += 1
                if num_prior < expansion_needed:
                    expansion_needed -= num_prior
                    num_after = 0
                    while num_after < expansion_needed:
                        check_index = root_index + 1 + num_after
                        if check_index >= size or self._val_in_rect(
                            row, check_index, 1, min_height, val=2
                        ):
                            return False
                        num_after += 1

        raise NotImplementedError()

    def _get_min_square_size(self, start_row, start_col) -> tuple[int, int]:
        explored = set()
        to_explore = [(0, 0)]

        while to_explore:
            offset_row, offset_col = to_explore.pop()
            explored.add((offset_row, offset_col))
            for potentials in [
                (offset_row + 1, offset_col),
                (offset_row, offset_col + 1),
            ]:
                if (
                    potentials[0] + start_row < self.size
                    and potentials[1] + start_col < self.size
                    and potentials not in explored
                    and self.data[start_row + potentials[0]][start_col + potentials[1]]
                    == 1
                ):
                    to_explore.append(potentials)

        min_height = max(explored, key=lambda x: x[0])[0] + 1
        min_width = max(explored, key=lambda x: x[1])[1] + 1
        return min_width, min_height

    def _val_in_rect(self, row, col, width, height, val) -> bool:
        for r in range(row, row + height + 1):
            for c in range(col, col + width + 1):
                if self.data[r][c] == val:
                    return True
        return False


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
