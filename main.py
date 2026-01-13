from abc import ABC, abstractmethod
from typing import Self


class State(ABC):
    @abstractmethod
    def print(self): ...

    @abstractmethod
    def copy(self) -> Self: ...

class Move(ABC):
    @abstractmethod
    def play(self, state: State) -> None: ...

    @abstractmethod
    def undo(self, state: State) -> None: ...

class GridState(State):
    def __init__(self, size: int, box_size=None) -> None:
        assert size > 0
        assert box_size is None or (size % box_size == 0 and size // box_size > 1)
        self.size = size
        self._box_size = box_size
        self.grid = [[None for _ in range(size)] for _ in range(size)]

    def print(self):
        if self._box_size:
            num_boxes = self.size // self._box_size
            box_edge = "═" * (self._box_size * 2 + 1)
            print("╔" + (box_edge + "╦") * (num_boxes - 1) + box_edge + "╗")

            for i, row in enumerate(self.grid):
                print("║", end=" ")
                for j, cell in enumerate(row):
                    if cell is None:
                        cell = " "
                    print(cell, end=" ")
                    if (j + 1) % self._box_size == 0 and self._box_size and j + 1 < self.size:
                        print("║", end=" ")
                print("║")
                if (i + 1) % self._box_size == 0 and self._box_size and i + 1 < self.size:
                    print("╠" + (box_edge + "╬") * (num_boxes - 1) + box_edge + "╣")
            print("╚" + (box_edge + "╩") * (num_boxes - 1) + box_edge + "╝")
        else:
            print("╔" + "═" * (self.size * 2 + 1) + "╗")
            for i, row in enumerate(self.grid):
                print("║ " + " ".join(" " if cell is None else str(cell) for cell in row) + " ║")
            print("╚" + "═" * (self.size * 2 + 1) + "╝")


    def copy(self):
        new_state = GridState(self.size, self._box_size)
        new_state.grid = [row[:] for row in self.grid]
        return new_state

class Moves(ABC):
    def __init__(self) -> None:
        self.is_legal = None
    pass


class GameRules(ABC):
    @abstractmethod
    def is_legal(self, data: State) -> bool: ...

    @abstractmethod
    def is_solved(self, data: State) -> bool: ...

    @abstractmethod
    def generate_moves(self, data: State) -> list[list[Move]]: ...


class GameEngine:
    def __init__(self, start_state: State, rules: GameRules) -> None:
        self.state = start_state
        self.rules = rules
        assert self.rules.is_legal(self.state), "Starting state is not legal."

    def solve(self):
        # TODO implement BFS instead of DFS!
        while not self.rules.is_solved(self.state):
            self.state.print()
            move_options = self.rules.generate_moves(self.state)

            moves_played = False

            option_count = []

            for i, options in enumerate(move_options):
                legal_options = 0
                last_legal_move = None
                for move in options:
                    move.play(self.state)
                    if self.rules.is_legal(self.state):
                        legal_options += 1
                        last_legal_move = move
                        move.is_legal = True
                    else:
                        move.is_legal = False
                    move.undo(self.state)
                option_count.append((i, legal_options))
                if legal_options == 1:
                    last_legal_move.play(self.state)
                    moves_played = True


            if not moves_played:
                option_count = sorted(option_count, key=lambda x: x[1])

                for i, count in option_count:
                    moves_tried = 0

                    for move in move_options[i]:
                        if not move.is_legal:
                            continue
                        move.play(self.state)
                        branch = GameEngine(self.state.copy(), self.rules)
                        try:
                            return branch.solve()
                        except Exception:
                            move.undo(self.state)
                            moves_tried += 1
                    
                    assert moves_tried == count


                print(min(option_count))
                raise Exception("No obvious move, but puzzle is not solved.")
            

        return self.state
