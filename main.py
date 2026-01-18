from abc import ABC, abstractmethod
from typing import Self, Callable, Generic, TypeVar, Iterable, Sequence, Optional


class State(ABC):
    def __init__(self, data, moves_played=0):
        self.data = data
        self.moves_played = moves_played

    @abstractmethod
    def print(self): ...

    @abstractmethod
    def copy(self) -> Self: ...


S = TypeVar("S", bound=State)


class Move(ABC, Generic[S]):
    def __init__(self):
        self.is_legal = True

    @abstractmethod
    def _play(self, state: S) -> None: ...

    @abstractmethod
    def _undo(self, state: S) -> None: ...

    def play(self, state: S) -> None:
        self._play(state)
        state.moves_played += 1

    def undo(self, state: S) -> None:
        self._undo(state)
        state.moves_played -= 1


class GridState(State):
    def __init__(self, size: int, box_size=None, moves_played=0) -> None:
        assert size > 0
        assert box_size is None or (size % box_size == 0 and size // box_size > 1)
        self.size = size
        self._box_size = box_size
        super().__init__(
            data=[[None for _ in range(size)] for _ in range(size)],
            moves_played=moves_played,
        )

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

    def copy(self):
        new_state = GridState(self.size, self._box_size, self.moves_played)
        new_state.data = [row[:] for row in self.data]
        return new_state


class Constraint(Generic[S], ABC):
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def check(self, state: S) -> bool: ...


class ConstraintNoDuplicates(Constraint[S]):
    def __init__(
        self, state_to_values: Callable[[S], Iterable], name, exceptions=(None,)
    ) -> None:
        super().__init__(name)
        self.state_to_values = state_to_values
        self.exceptions = exceptions

    def check(self, state: S) -> bool:
        values = self.state_to_values(state)
        seen = set()
        for item in values:
            if item in self.exceptions:
                continue
            if item in seen:
                return False
            seen.add(item)
        return True


class SolutionFound(Exception, Generic[S]):
    def __init__(self, state: S):
        self.state = state


class GameRules(ABC, Generic[S]):
    def __init__(self, constraints: Sequence[Constraint[S]]) -> None:
        super().__init__()
        self.constraints = constraints

    def is_legal(self, state: S) -> bool:
        return all(constraint.check(state) for constraint in self.constraints)

    @abstractmethod
    def is_solved(self, state: S) -> bool: ...
    @abstractmethod
    def _generate_moves(self, state: S) -> Iterable[list[Move]]: ...

    def generate_legal_moves(self, state: S) -> list[list[Move]]:
        legal_moves = []
        for move_options in self._generate_moves(state):
            legal_options = []
            for move in move_options:
                move.play(state)
                if self.is_legal(state):
                    legal_options.append(move)
                move.undo(state)
            legal_moves.append(legal_options)
        return legal_moves


def play_necessary_moves(
    state: S, rules: GameRules[S]
) -> tuple[S, list[list[Move]], int]:
    moves_played = None
    while moves_played is None or moves_played > 0:
        least_options = float("inf")
        moves_played = 0
        legal_moves = rules.generate_legal_moves(state)
        for move_options in legal_moves:
            num_move_options = len(move_options)
            if num_move_options == 1:
                move_options[0].play(state)
                moves_played += 1
            if num_move_options == 0:
                return state, [], 0
            least_options = min(num_move_options, least_options)

    if rules.is_solved(state):
        raise SolutionFound(state)

    assert least_options != 1, "Should have played all necessary moves."

    return state, legal_moves, least_options  # type: ignore


class GameTreeNode(Generic[S]):
    def __init__(self, state: S, parent: "GameTreeNode[S]", parent_move: Move[S], rules: GameRules[S]):
        self.parent = parent
        self.parent_move = parent_move
        self.rules = rules
        self.explored_moves: dict[Move, Optional["GameTreeNode[S]"]] = {}
        self.state = state

    def initialize(self):
        self.state, self.legal_moves, self.least_options = play_necessary_moves(
            self.state, self.rules
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

    def replace_child_with(
        self, move: Move[S], new_child: "GameTreeNode[S]"
    ):
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
            new_node = GameTreeNode(self.state, self.parent, self.parent_move, self.rules)
            self.parent.replace_child_with(self.parent_move, new_node)
            new_node.initialize()

    def explore_move(self, move: Move):
        new_state = self.state.copy()
        move.play(new_state)

        child_node = GameTreeNode(new_state, self, move, self.rules)
        self.explored_moves[move] = child_node
        child_node.initialize()


class GameTreeRoot(GameTreeNode[S]):
    def __init__(self, rules: GameRules[S], starting_state: S):
        self.rules = rules
        self.starting_node = GameTreeNode(starting_state, self, None, rules).initialize()

    def replace_child_with(
        self, old_child: "GameTreeNode[S]", new_child: "GameTreeNode[S]"
    ):
        self.starting_node = new_child
        print(f"Root node on move {self.starting_node.state.moves_played}")

    def mark_child_as_illegal(self, child: "GameTreeNode[S]"):
        raise Exception("No solution exists.")


class GameEngine(Generic[S]):
    def __init__(self, start_state: S, rules: GameRules[S]) -> None:
        self.start_state = start_state
        self.rules = rules
        assert self.rules.is_legal(self.start_state), "Starting state is not legal."

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
                    unexplored_moves = [m for m in move_options if m not in node.explored_moves]
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
        root = GameTreeRoot(self.rules, self.start_state)

        while True:
            node, move = self.choose_next_explore(root)
            node.explore_move(move)

    def solve(self) -> S:
        try:
            self.build_tree()
        except SolutionFound as e:
            solution = e.state
        assert self.rules.is_solved(solution)
        return solution
