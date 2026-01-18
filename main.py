from abc import ABC, abstractmethod
from typing import Self, Callable, Generic, TypeVar, Iterable, Sequence, Optional


class State(ABC):
    def __init__(self, data, moves_played=0):
        self.data = data
        self.moves_played = moves_played

    @abstractmethod
    def print(self): ...

    def copy(self) -> Self:  # not abstract method so we can run test
        raise NotImplementedError()

    @abstractmethod
    def generate_legal_moves(self) -> list[list["Move"]]:
        """Generate all legal moves from the current state.

        Can also generate a single move if it is forced.
        """

    @abstractmethod
    def is_solved(self) -> bool: ...


S = TypeVar("S", bound=State)


class Move(ABC, Generic[S]):
    def __init__(self):
        self.is_legal = True

    @abstractmethod
    def _play(self, state: S) -> None: ...

    def play(self, state: S) -> None:
        self._play(state)
        state.moves_played += 1


class ComboMove(Move[S]):
    def __init__(self, moves: list[Move[S]]):
        super().__init__()
        self.moves = moves

    def _play(self, state: S) -> None:
        for move in self.moves:
            move.play(state)

class GridState(State, Generic[S]):
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)
    DIRECTIONS = [UP, DOWN, LEFT, RIGHT]

    def __init__(
        self, size: int, max_value, box_size=None, moves_played=0, starting_state=None
    ) -> None:
        assert size > 0
        assert box_size is None or (size % box_size == 0 and size // box_size > 1)
        self.size = size
        self._box_size = box_size
        self.max_value = max_value
        if starting_state is None:
            starting_state = [[None for _ in range(size)] for _ in range(size)]
        super().__init__(data=starting_state, moves_played=moves_played)

    def is_solved(self) -> bool:
        return not any(None in row for row in self.data)

    def iter_cells(self) -> Iterable[tuple[int, int, Optional[int]]]:
        for row in range(self.size):
            for col in range(self.size):
                yield row, col, self.data[row][col]

    def column(self, col_idx: int) -> Sequence:
        return [self.data[row_idx][col_idx] for row_idx in range(self.size)]

    def row(self, row_idx: int) -> Sequence:
        return self.data[row_idx]

    def box(self, box_row: int, box_col: int) -> Sequence:
        assert self._box_size is not None, "Grid has no boxes defined."
        return tuple(
            self.data[box_row * self._box_size + i][box_col * self._box_size + j]
            for i in range(self._box_size)
            for j in range(self._box_size)
        )

    def neighbors(
        self, row: int, col: int, diagonal: bool = False
    ) -> list[Optional[int]]:
        assert not diagonal, "Diagonal neighbors not implemented."
        return [self.data[r][c] for r, c in self.neighbors_pos(row, col)]

    def neighbors_pos(self, row: int, col: int) -> Iterable[tuple[int, int]]:
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            if 0 <= row + dr < self.size and 0 <= col + dc < self.size:
                yield (row + dr, col + dc)

    def generate_legal_moves(self) -> list[list[Move[S]]]:
        all_legal_moves = []
        for row, col, value in self.iter_cells():
            if value is not None:
                continue
            legal_moves = self._generate_legal_moves_for_cell(row, col)
            if len(legal_moves) == 1:
                return [legal_moves]
            all_legal_moves.append(legal_moves)
        return all_legal_moves

    def _generate_legal_moves_for_cell(self, row: int, col: int) -> list[Move[S]]:
        raise NotImplementedError()

    def print(self):
        if self._box_size:
            num_boxes = self.size // self._box_size
            box_edge = "═" * (self._box_size * 2 + 1)
            print("╔" + (box_edge + "╦") * (num_boxes - 1) + box_edge + "╗")

            for i, row in enumerate(self.data):
                print("║", end=" ")
                for j, cell in enumerate(row):
                    if cell is None:
                        cell = " "
                    print(cell, end=" ")
                    if (
                        (j + 1) % self._box_size == 0
                        and self._box_size
                        and j + 1 < self.size
                    ):
                        print("║", end=" ")
                print("║")
                if (
                    (i + 1) % self._box_size == 0
                    and self._box_size
                    and i + 1 < self.size
                ):
                    print("╠" + (box_edge + "╬") * (num_boxes - 1) + box_edge + "╣")
            print("╚" + (box_edge + "╩") * (num_boxes - 1) + box_edge + "╝")
        else:
            print("╔" + "═" * (self.size * 2 + 1) + "╗")
            for i, row in enumerate(self.data):
                print(
                    "║ "
                    + " ".join(" " if cell is None else str(cell) for cell in row)
                    + " ║"
                )
            print("╚" + "═" * (self.size * 2 + 1) + "╝")


class ShadedGridState(GridState):
    SHADED = 1
    UNSHADED = 2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, max_value=2, box_size=None)

    def __str__(self) -> str:
        result = "╔" + "═" * (self.size * 2 + 1) + "╗\n"
        for row in self.data:
            result += (
                "║ "
                + " ".join(
                    " " if cell is None else ("█" if cell == 2 else "▒") for cell in row
                )
                + " ║\n"
            )
        result += "╚" + "═" * (self.size * 2 + 1) + "╝\n"
        return result


class GridMove(Move[GridState[S]]):
    def __init__(self, row: int, col: int, value: int):
        super().__init__()
        self.row = row
        self.col = col
        self.value = value

    def _play(self, state: GridState[S]) -> None:
        state.data[self.row][self.col] = self.value

class SolutionFound(Exception, Generic[S]):
    def __init__(self, state: S):
        self.state = state


def play_necessary_moves(state: S) -> tuple[S, list[list[Move]], int]:
    while True:
        least_options = float("inf")
        legal_moves = state.generate_legal_moves()
        for move_options in legal_moves:
            num_move_options = len(move_options)
            if num_move_options == 1:
                move_options[0].play(state)
                break
            if num_move_options == 0:
                return state, [], 0
            least_options = min(num_move_options, least_options)
        else:
            break

    assert legal_moves is not None
    if not legal_moves and state.is_solved():
        raise SolutionFound(state)

    assert least_options != 1, "Should have played all necessary moves."

    return state, legal_moves, least_options  # type: ignore


class GameTreeNode(Generic[S]):
    def __init__(
        self,
        state: S,
        parent: "GameTreeNode[S]",
        parent_move: Move[S],
    ):
        self.parent = parent
        self.parent_move = parent_move
        self.explored_moves: dict[Move, Optional["GameTreeNode[S]"]] = {}
        self.state = state

    def initialize(self):
        self.state, self.legal_moves, self.least_options = play_necessary_moves(
            self.state
        )
        if not self.legal_moves:
            self.parent.mark_child_as_illegal(self)
        return self

    def mark_child_as_illegal(self, child: "GameTreeNode[S]"):
        for move, explored_node in self.explored_moves.items():
            if explored_node is child:
                move.is_legal = False
                self.explored_moves[move] = None
                was_forced = self.check_for_forced_move()
                if not was_forced:
                    self.recalc_least_options()
                break

    def recalc_least_options(self):
        self.least_options = float("inf")
        for move_options in self.legal_moves:
            num_move_options = len([m for m in move_options if m.is_legal])
            self.least_options = min(self.least_options, num_move_options)
        assert self.least_options != 1, "Should have played all necessary moves."

    def replace_child_with(self, move: Move[S], new_child: "GameTreeNode[S]"):
        assert move in self.explored_moves, "Move not found among explored moves."
        self.explored_moves[move] = new_child

    def check_for_forced_move(self):
        for move_options in self.legal_moves:
            move_options = [m for m in move_options if m.is_legal]
            assert len(move_options) > 0, "Should have already played the forced move."
            if len(move_options) == 1:
                self.play_forced_move(move_options[0])
                return True
        return False

    def play_forced_move(self, forced_move: Move):
        if forced_move in self.explored_moves:
            new_node = self.explored_moves[forced_move]
            new_node.parent = self.parent
            new_node.parent_move = self.parent_move
            assert new_node is not None, "Forced move was marked illegal."
            self.parent.replace_child_with(self.parent_move, new_node)
        else:
            forced_move.play(self.state)
            new_node = GameTreeNode(self.state, self.parent, self.parent_move)
            self.parent.replace_child_with(self.parent_move, new_node)
            new_node.initialize()

    def explore_move(self, move: Move):
        new_state = self.state.copy()
        move.play(new_state)

        child_node = GameTreeNode(new_state, self, move)
        self.explored_moves[move] = child_node
        child_node.initialize()


class GameTreeRoot(GameTreeNode[S]):
    def __init__(self, starting_state: S):
        self.starting_node = GameTreeNode(starting_state, self, None).initialize()

    def replace_child_with(self, move: Move[S] | None, new_child: "GameTreeNode[S]"):
        self.starting_node = new_child
        print(f"Root node on move {self.starting_node.state.moves_played}")

    def mark_child_as_illegal(self, child: "GameTreeNode[S]"):
        raise Exception("No solution exists.")


class GameEngine(Generic[S]):
    def __init__(self, start_state: S) -> None:
        self.start_state = start_state

    def choose_next_explore(
        self, root: GameTreeRoot[S]
    ) -> tuple[GameTreeNode[S], Move]:
        stack = [(root.starting_node, 0)]

        best_node = None
        best_num = float("inf")
        best_move = None

        while stack:
            node, depth = stack.pop(len(stack) - 1)

            for move_options in node.legal_moves:
                move_options = [m for m in move_options if m.is_legal]
                if len(move_options) < best_num:
                    unexplored_moves = [
                        m for m in move_options if m not in node.explored_moves
                    ]
                    if unexplored_moves:
                        best_node = node
                        best_move = unexplored_moves[0]
                        best_num = len(move_options)

            if best_num == 2:
                break

            for explored_node in node.explored_moves.values():
                if explored_node is not None:
                    stack.append((explored_node, depth + 1))

        if best_node is None:
            raise Exception("No moves to explore.")

        print(f"Exploring move at depth {depth} with {best_num} options.")
        return best_node, best_move

    def build_tree(self) -> GameTreeNode[S]:
        root = GameTreeRoot(self.start_state)

        while True:
            node, move = self.choose_next_explore(root)
            node.explore_move(move)

    def solve(self) -> S:
        try:
            self.build_tree()
        except SolutionFound as e:
            solution = e.state
        assert solution.is_solved(), "Returned solution is not actually solved."
        return solution
