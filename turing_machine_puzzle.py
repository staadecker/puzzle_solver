from typing import Callable
from itertools import product

# triangle = 0
# square = 1
# circle = 2


class Card:
    def __init__(
        self, num_options: int, rule: Callable[[tuple[int, int, int], int], bool]
    ) -> None:
        self.num_options = num_options
        self.rule = rule


class CompareCard(Card):
    def __init__(
        self,
        value: Callable[[tuple[int, int, int]], int],
        threshold: Callable[[tuple[int, int, int]], int],
    ) -> None:
        def rule(guess: tuple[int, int, int], setting: int) -> bool:
            v = value(guess)
            t = threshold(guess)
            match setting:
                case 0:
                    return v < t
                case 1:
                    return v == t
                case 2:
                    return v > t
                case _:
                    raise ValueError("Invalid setting")

        super().__init__(num_options=3, rule=rule)


def solve(cards):
    possible_settings = [card.num_options for card in cards]

    valid_settings = []

    for setting_combination in product(
        *[range(num_options) for num_options in possible_settings]
    ):
        valid, last_guess = find_guess(cards, setting_combination)
        if valid == 1:
            # print(
            #     f"Found unique setting combination {setting_combination} with guess {last_guess}"
            # )
            valid_settings.append((setting_combination, last_guess))

    valid_not_unnecessary = []

    assert len(valid_settings) > 0, "No valid settings found"

    for valid_setting, last_guess in valid_settings:
        for skip_card in range(len(cards)):
            modified_cards = [card for i, card in enumerate(cards) if i != skip_card]
            modified_settings = tuple(
                setting for i, setting in enumerate(valid_setting) if i != skip_card
            )
            valid, _ = find_guess(modified_cards, modified_settings)
            # print(
            #     f"Setting {valid_setting} without card {skip_card} gives {valid} valid guesses"
            # )
            if valid == 1:
                # print("Setting", valid_setting, "is unnecessary due to card", skip_card)
                break
        else:
            valid_not_unnecessary.append((valid_setting, last_guess))

    if len(valid_not_unnecessary) == 0:
        print("All valid settings are unnecessary:")
        for settings, guess in valid_settings:
            print(f"  Settings: {settings}, Guess: {guess}")
        return

    print(valid_not_unnecessary)

    assert len(valid_not_unnecessary) == 1, "Multiple valid settings found"
    answer = find_guess(cards, valid_not_unnecessary[0][0])
    print("Final answer:", answer[1])


def find_guess(cards, settings: tuple[int, ...]) -> tuple[int, tuple[int, int, int]]:
    valid_guess = set()
    for guess in product(range(1, 10), repeat=3):
        if all(card.rule(guess, setting) for card, setting in zip(cards, settings)):
            valid_guess.add(guess)
    return len(valid_guess), next(iter(valid_guess)) if valid_guess else None


### Problem 6

problem_6 = [
    CompareCard(value=lambda guess: guess[1], threshold=lambda guess: 3),
    Card(
        num_options=2,
        rule=lambda guess, setting: (
            (sum(guess) % 2 == 0) if setting == 0 else (sum(guess) % 2 == 1)
        ),
    ),
    Card(
        num_options=3,
        rule=lambda g, s: g[s] >= g[(s + 1) % 3] and g[s] >= g[(s + 2) % 3],
    ),
    CompareCard(
        value=lambda guess: guess[0] + guess[1],
        threshold=lambda guess: guess[2],
    ),
    CompareCard(
        value=lambda guess: guess[0] * guess[1] * guess[2],
        threshold=lambda guess: 40,
    ),
]


### Problem 4 

def not_same_rule(guess: tuple[int, int, int], setting: int) -> bool:
    match setting:
        case 0:
            return guess[0] != guess[1]
        case 1:
            return guess[0] != guess[2]
        case 2:
            return guess[1] != guess[2]
        case _:
            raise ValueError("Invalid setting")

problem_4 = [
    CompareCard(value=lambda guess: guess[0], threshold=lambda guess: 1),
    CompareCard(value=lambda guess: guess[1], threshold=lambda guess: 4),
    Card(num_options=3, rule=lambda guess, setting: sum(guess) % (setting + 3) == 0),
] + [Card(num_options=3, rule=not_same_rule)] * 3

### Problem 5

problem_5 = [
    CompareCard(value=lambda guess: guess[0], threshold=lambda guess: 3),
    CompareCard(value=lambda guess: guess[0], threshold=lambda guess: guess[1]),
    CompareCard(value=lambda guess: sum(guess), threshold=lambda guess: 6),
    Card(num_options=3, rule=lambda guess, setting: guess[setting] > 3),
    Card(
        num_options=20,
        rule=lambda guess, setting: sum(v == ((setting // 4) + 1) for v in guess)
        == setting % 4,
    ),
]


### Example B

card_bA = CompareCard(value=lambda guess: guess[0], threshold=lambda guess: 1)
card_bB = CompareCard(value=lambda guess: guess[0], threshold=lambda guess: 3)
card_bC = CompareCard(value=lambda guess: guess[1], threshold=lambda guess: 3)
card_bD = Card(
    num_options=4, rule=lambda guess, setting: sum(v == 1 for v in guess) == setting
)
example_b = [card_bA, card_bB, card_bC, card_bD]

### Example A

example_A = [Card(num_options=4, rule=lambda guess, setting: sum(v == 4 for v in guess) == setting)]

if __name__ == "__main__":
    solve(example_A)
    solve(example_b)
    solve(problem_4)
    # solve(problem_5)
    solve(problem_6)


# triangle = 0
# square = 1
# circle = 2
