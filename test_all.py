from main import GridState
import pytest


@pytest.mark.parametrize(
    "box_size,expected_result",
    [
        (
            None,
            """╔═════════╗
║ 1 2 3 4 ║
║ 3 4 1 2 ║
║ 2 1 4 3 ║
║ 4 3 2 1 ║
╚═════════╝
""",
        ),
        (
            2,
            """╔═════╦═════╗
║ 1 2 ║ 3 4 ║
║ 3 4 ║ 1 2 ║
╠═════╬═════╣
║ 2 1 ║ 4 3 ║
║ 4 3 ║ 2 1 ║
╚═════╩═════╝
""",
        ),
    ],
)
def test_grid_state_print(box_size, expected_result, ):
    grid_state = GridState(size=4, box_size=box_size, max_value=4)
    grid_state.data = [
        [1, 2, 3, 4],
        [3, 4, 1, 2],
        [2, 1, 4, 3],
        [4, 3, 2, 1],
    ]

    assert str(grid_state) == expected_result


if __name__ == "__main__":
    pytest.main()
