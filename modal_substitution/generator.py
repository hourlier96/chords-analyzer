from tabulate import tabulate
from modal_substitution.utils.modal_analyzer import detect_intelligent_mode
from modal_substitution.constants import MODES_DATA, ROMAN_DEGREES
from modal_substitution.utils.utils import (
    format_chords_for_table,
    get_diatonic_7th_chord,
    get_note_from_index,
    get_roman_numeral,
)


def create_modal_substitution_table(base_progression, tonic=None):
    """
    Analyzes a chord progression, detects its mode,
    and creates a substitution table showing how it would be reinterpreted
    in other modes by borrowing chords of equivalent degrees.
    """
    if tonic and tonic not in base_progression:
        print(
            f"Warning: Tonic '{tonic}' not found in the progression. Using default tonic '{base_progression[0]}'."
        )
        tonic = None

    if not base_progression or len(base_progression) < 2:
        print("The progression is empty or too short.")
        return

    print("\nTonic:", tonic if tonic else base_progression[0])
    print(f"Analyzing progression '{' -> '.join(base_progression)}'")

    # Detect the most probable mode
    detected_tonic_index, original_mode = detect_intelligent_mode(
        base_progression, tonic
    )
    if not original_mode:
        print(
            "No mode detected, can't create substitution table. It seems the progression is not diatonic."
        )
        return

    tonic_name = get_note_from_index(detected_tonic_index)

    print(
        f"Most probable mode : {tonic_name} {original_mode} - {' '.join([get_roman_numeral(chord, detected_tonic_index, original_mode) for chord in base_progression])}"
    )

    # Try to find an actual chord that matches the tonic

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

    # Handle failed parsing
    if None in degrees_to_borrow:
        print(
            "Warning: One or more chords could not be analyzed as clear degrees. The detected mode may be incorrect."
        )
        degrees_to_borrow = [d for d in degrees_to_borrow if d is not None]
    # Create the substitution table
    table_data = []
    headers = [
        "Mode",
        "Borrowed Scale (Relative)",
        f"Borrowed Degrees ({' '.join(original_numerals)})",
        "Substitution",
    ]

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
            f"{get_note_from_index(relative_tonic_index)} Major",
            format_chords_for_table(borrowed_chords),
            format_chords_for_table(new_progression),
        ]
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
