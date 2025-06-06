from tabulate import tabulate
from harmonic_substitution.constants import FUNCTIONS_BY_KEY
from harmonic_substitution.utils.utils import (
    get_function_for_chord,
)


def create_harmonical_substitution_table(progression, tonic):
    func_map = FUNCTIONS_BY_KEY[tonic]
    table_data = []

    for chord in progression:
        func = get_function_for_chord(chord, tonic)
        substitutions = [alt for alt in func_map.get(func, []) if alt != chord]
        table_data.append(
            [chord, func, ", ".join(substitutions) if substitutions else "-"]
        )

    headers = ["Chord", "Function", "Substitutions"]
    print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
