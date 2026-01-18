"""Allows the creation of a puzzle where each grid cell can be one of two puzzles."""

from main import GridState, Move, GridMove, ShadedGridState
from typing import TypeVar, Generic, Iterable

A = TypeVar("A", bound=GridState)
B = TypeVar("B", bound=GridState)


class HybridPuzzleState(Generic[A, B], ShadedGridState):
    def __init__(self, state_a: A, state_b: B) -> None:
        super().__init__(size=state_a.size, max_value=2, box_size=None)
        self.state_a = state_a
        self.state_b = state_b

    def generate_moves(self) -> Iterable[list[Move]]:
        for move_option in self._smart_generate_moves():
            yield move_option

        for move_option in self.state_a.generate_moves():
            if self.data[move_option[0].row][move_option[0].col] == 1:
                yield [HybridMoveWrapper(move, True) for move in move_option]
        for move_option in self.state_b.generate_moves():
            if self.data[move_option[0].row][move_option[0].col] == 2:
                yield [HybridMoveWrapper(move, False) for move in move_option]

    def _smart_generate_moves(self) -> Iterable[list[Move]]:
        has_a = any(
            self.data[row][col] == 1
            for row in range(self.size)
            for col in range(self.size)
        )
        has_b = any(
            self.data[row][col] == 2
            for row in range(self.size)
            for col in range(self.size)
        )

        for row in range(self.size):
            for col in range(self.size):
                moves = []
                if self.data[row][col] is not None:
                    continue
                neighbors = list(self.neighbors(row, col))
                if not has_a or 1 in neighbors:
                    moves.append(GridMove(row, col, 1))
                if not has_b or 2 in neighbors:
                    moves.append(GridMove(row, col, 2))
                yield moves

    def is_solved(self) -> bool:        
        for row, col, value in self.iter_cells():
            if value is None:
                return False
            elif value == 1 and self.state_a.data[row][col] is None:
                return False
            elif value == 2 and self.state_b.data[row][col] is None:
                return False
        return True
                        
class HybridMoveWrapper(Move[HybridPuzzleState]):
    def __init__(self, move: Move, puzzle_a: bool):
        self.move = move
        self.puzzle_a = puzzle_a

    def _play(self, state: HybridPuzzleState) -> None:
        self.move.play(state.state_a if self.puzzle_a else state.state_b)
