def grid_data_to_str(data, box_size: int | None = None, none_value: str = " ") -> str:
    pretty_data = [
        [none_value if cell is None else cell for cell in row] for row in data
    ]
    size = len(pretty_data)
    result = ""
    if box_size:
        num_boxes = size // box_size
        box_edge = "═" * (box_size * 2 + 1)
        result += "╔" + (box_edge + "╦") * (num_boxes - 1) + box_edge + "╗\n"

        for i, row in enumerate(pretty_data):
            result += "║ "
            for j, cell in enumerate(row):
                if cell is None:
                    cell = " "
                result += str(cell) + " "
                if (j + 1) % box_size == 0 and box_size and j + 1 < size:
                    result += "║ "
            result += "║\n"
            if (i + 1) % box_size == 0 and box_size and i + 1 < size:
                result += "╠" + (box_edge + "╬") * (num_boxes - 1) + box_edge + "╣\n"
        result += "╚" + (box_edge + "╩") * (num_boxes - 1) + box_edge + "╝\n"
    else:
        result += "╔" + "═" * (size * 2 + 1) + "╗\n"
        for i, row in enumerate(pretty_data):
            result += (
                "║ "
                + " ".join(" " if cell is None else str(cell) for cell in row)
                + " ║\n"
            )
        result += "╚" + "═" * (size * 2 + 1) + "╝\n"
    return result


def concat_str_horizontally(*strs: str) -> str:
    lines = [s.splitlines() for s in strs]
    max_lines = max(len(l) for l in lines)
    for l in lines:
        while len(l) < max_lines:
            l.append("")

    result_lines = []
    for i in range(max_lines):
        result_lines.append("\t".join(l[i] for l in lines))
    return "\n".join(result_lines)
