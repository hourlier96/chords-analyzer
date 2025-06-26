from tabulate import tabulate
from modal_substitution.utils.modal_analyzer import detect_mode
from modal_substitution.constants import MODES_DATA, ROMAN_DEGREES
from modal_substitution.utils.utils import (
    format_chords_for_table,
    get_diatonic_7th_chord,
    get_note_from_index,
    get_note_index,
    get_roman_numeral,
    guess_possible_tonics,
)


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

    if not original_mode:
        print(
            "No mode detected, can't create substitution table. It seems the progression is not diatonic."
        )
        return

    tonic_name = get_note_from_index(detected_tonic_index)
    print(
        f"{tonic_name} {original_mode} - {' '.join([get_roman_numeral(chord, detected_tonic_index, original_mode) for chord in base_progression])}"
    )

    # Remove tonic chord(s) from substitution candidates
    chords_to_substitute = [c for c in base_progression]
    if not chords_to_substitute:
        chords_to_substitute = base_progression[1:]  # fallback

    # Get Roman numeral representation of non-tonic chords
    original_numerals = [
        get_roman_numeral(c, detected_tonic_index, original_mode)
        for c in chords_to_substitute
    ]

    # Try to convert numerals to degree numbers (1-7)
    degrees_to_borrow = []
    for numeral in original_numerals:
        try:
            numeral_cleaned = (
                numeral.upper()
                .replace("MAJ7", "")
                .replace("M7", "")
                .replace("Ø7", "")
                .replace("°7", "")
                .replace("7", "")
            )
            degrees_to_borrow.append(ROMAN_DEGREES.index(numeral_cleaned) + 1)
        except ValueError:
            degrees_to_borrow.append(None)

    # Create the substitution table
    table_data = []
    headers = ["Mode", "Substitution"]
    if verbose:
        headers.insert(
            1,
            "Borrowed Scale (Relative)",
        )
        headers.insert(
            2,
            f"Borrowed Degrees ({' '.join(original_numerals)})",
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
