import re
from tabulate import tabulate
from constants import MODES_DATA, ROMAN_DEGREES
from utils.common import (
    get_diatonic_7th_chord,
    get_note_from_index,
    get_note_index,
    get_roman_numeral,
)
from utils.mode_detection import detect_mode, guess_possible_tonics


def create_modal_substitution_table(base_progression, verbose=False):
    """
    Analyzes a chord progression, detects its mode,
    and creates a substitution table showing how it would be reinterpreted
    in other modes by borrowing chords of equivalent degrees.
    """
    if not base_progression or len(base_progression) < 2:
        print("The progression is empty or too short.")
        return
    print(f"\nAnalyzing progression '{' -> '.join(base_progression)}'")

    # Detect the most probable tonic
    tonic_candidates = guess_possible_tonics(base_progression)
    if tonic_candidates:
        tonic = tonic_candidates[0][0]

    detected_tonic_index = get_note_index(tonic)

    # Then the mode from the tonic
    original_mode = detect_mode(base_progression, tonic)

    tonic_name = get_note_from_index(detected_tonic_index)
    full_analysis_tuples = [
        get_roman_numeral(chord, detected_tonic_index, original_mode)
        for chord in base_progression
    ]

    expected_numerals_list = [result[0] for result in full_analysis_tuples]
    found_numerals_list = [result[1] for result in full_analysis_tuples]

    print(f"\n--- {tonic_name} {original_mode} ---")
    print(f"Attendus : {' -> '.join(expected_numerals_list)}")
    print(f"Réels    : {' -> '.join(found_numerals_list)}")

    chords_to_substitute = []
    original_numerals_tuples = []

    for i, chord in enumerate(base_progression):
        chords_to_substitute.append(chord)
        original_numerals_tuples.append(full_analysis_tuples[i])

    if not chords_to_substitute and base_progression:
        chords_to_substitute = base_progression[1:]
        original_numerals_tuples = full_analysis_tuples[1:]

    degrees_to_borrow = []
    for expected, found in original_numerals_tuples:
        import re

        match = re.match(r"^[ivxIVX]+", found)
        if match:
            base_numeral_str = match.group(0)

            try:
                degree_num = ROMAN_DEGREES.index(base_numeral_str.upper()) + 1
                degrees_to_borrow.append(degree_num)
            except ValueError:
                continue
        else:
            degrees_to_borrow.append(None)

    table_data = []
    headers = ["Mode", "Substitution"]
    if verbose:
        headers.insert(
            1,
            "Borrowed Scale (Relative)",
        )
        headers.insert(
            2,
            f"Borrowed Degrees ({' '.join(found_numerals_list)})",
        )

    for mode_name, (_, _, interval) in MODES_DATA.items():
        # Transpose the tonic relatively for each mode
        relative_tonic_index = (detected_tonic_index + interval + 12) % 12

        borrowed_chords, new_progression = get_substitutions(
            base_progression,
            relative_tonic_index,
            degrees_to_borrow,
        )

        # Highlight the original mode
        mode_label = (
            mode_name + " (Original)" if mode_name == original_mode else mode_name
        )

        row = [
            mode_label,
            format_chords_for_table(new_progression),
        ]
        if verbose:
            row.insert(
                1,
                f"{get_note_from_index(relative_tonic_index)} Major",
            )
            row.insert(
                2,
                format_chords_for_table(borrowed_chords),
            )
        table_data.append(row)

    print(tabulate(table_data, headers=headers, tablefmt="grid"))


def create_modal_harmonization_table(progression):
    """
    Analyse une progression d'accords, détecte sa tonalité, et génère une table
    de réharmonisation par échange modal parallèle.
    """
    if not progression or len(progression) < 1:
        print("La progression est vide.")
        return

    print(f"\nAnalyzing progression '{' -> '.join(progression)}'")

    # 1. Détection de la tonique et du mode
    tonic_candidates = guess_possible_tonics(progression)
    if not tonic_candidates:
        print("Erreur : Impossible de déterminer une tonique probable.")
        return

    tonic_name = tonic_candidates[0][0]
    tonic_index = get_note_index(tonic_name)
    original_mode = detect_mode(progression, tonic_name)

    # 2. Analyse en chiffres romains
    analysis_tuples = [
        get_roman_numeral(chord, tonic_index, original_mode) for chord in progression
    ]
    expected_numerals = [r[0] for r in analysis_tuples]
    found_numerals = [r[1] for r in analysis_tuples]

    print(f"\n{tonic_name} {original_mode}")
    print(f"Supposed : {' -> '.join(expected_numerals)}")
    print(f"Actual   : {' -> '.join(found_numerals)}")

    # 3. Conversion des chiffres romains en degrés numériques pour la substitution
    degrees_to_borrow = []
    for numeral in found_numerals:
        clean_numeral = re.sub(r"[()°b#]", "", numeral)
        match = re.match(r"^[ivxIVX]+", clean_numeral)
        if match:
            try:
                degree_num = ROMAN_DEGREES.index(match.group(0).upper()) + 1
                degrees_to_borrow.append(degree_num)
            except ValueError:
                degrees_to_borrow.append(None)
        else:
            degrees_to_borrow.append(None)

    # 4. Création de la table de substitution
    table_data = []
    headers = ["Source Mode", "Harmonization"]

    for mode_name in MODES_DATA:
        # Pour chaque mode, on génère la séquence d'accords correspondante
        harmonized_chords = [
            get_diatonic_7th_chord(deg, tonic_index, mode_name)
            for deg in degrees_to_borrow
        ]

        mode_label = f"{mode_name}"
        if mode_name == original_mode:
            mode_label += " (Original)"

        row = [f"{tonic_name} {mode_label}", format_chords_for_table(harmonized_chords)]
        table_data.append(row)

    print(tabulate(table_data, headers=headers, tablefmt="grid"))


def get_substitutions(
    base_progression,
    relative_tonic_index,
    degrees_to_borrow,
):
    # Get the equivalent chords from the new mode
    borrowed_chords = [
        get_diatonic_7th_chord(
            deg,
            relative_tonic_index,
        )
        for i, deg in enumerate(degrees_to_borrow)
    ]

    # Reconstruct the full progression with substitutions
    new_progression_chords = []
    borrowed_idx = 0
    for _ in base_progression:
        new_progression_chords.append(borrowed_chords[borrowed_idx])
        borrowed_idx += 1

    return borrowed_chords, new_progression_chords


# Formats a list of chord names for display in table columns
def format_chords_for_table(chords, width=7):
    if isinstance(chords, str):
        chords_list = chords.split(" - ")
    else:
        chords_list = chords
    formatted = [f"{chord if chord else '-':<{width}}" for chord in chords_list]
    return " ".join(formatted)
