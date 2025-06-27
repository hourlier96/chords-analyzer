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
    full_analysis_tuples = [
        get_roman_numeral(chord, detected_tonic_index, original_mode)
        for chord in base_progression
    ]

    # 2. On prépare les chaînes de caractères pour l'affichage demandé.
    # On sépare les degrés attendus et les degrés réels en deux listes distinctes.
    expected_numerals_list = [result[0] for result in full_analysis_tuples]
    found_numerals_list = [result[1] for result in full_analysis_tuples]

    # 3. On affiche le résultat dans le format souhaité.
    print(f"\n--- Analyse pour {tonic_name} {original_mode} ---")
    print(f"Attendus : {' -> '.join(expected_numerals_list)}")
    print(f"Réels    : {' -> '.join(found_numerals_list)}")

    # 4. On filtre correctement les accords à substituer (ceux qui ne sont pas la tonique).
    # Cette logique est maintenant correcte et se base sur le chiffrage attendu.
    chords_to_substitute = []
    # On stocke aussi les chiffrages correspondants pour un usage ultérieur
    original_numerals_tuples = []

    for i, chord in enumerate(base_progression):
        chords_to_substitute.append(chord)
        original_numerals_tuples.append(full_analysis_tuples[i])

    # Fallback de sécurité si la progression ne contenait que des accords de tonique
    if not chords_to_substitute and base_progression:
        chords_to_substitute = base_progression[1:]
        original_numerals_tuples = full_analysis_tuples[1:]

    # 5. On convertit les chiffrages en degrés numériques (1-7).
    # Cette partie fonctionne maintenant avec la liste de tuples.
    degrees_to_borrow = []
    for expected, found in original_numerals_tuples:
        # On se base sur le chiffrage réel (found) pour la conversion.
        # On retire les suffixes comme 'maj7', '7', etc. pour ne garder que le chiffre.
        # Ex: "Vmaj7" -> "V", "vi" -> "vi"
        import re

        match = re.match(r"^[ivxIVX]+", found)
        if match:
            base_numeral_str = match.group(0)

            # On trouve l'index dans la liste ROMAN_DEGREES (en majuscule) et on ajoute 1.
            try:
                degree_num = ROMAN_DEGREES.index(base_numeral_str.upper()) + 1
                degrees_to_borrow.append(degree_num)
            except ValueError:
                # Gère le cas où le chiffrage ne serait pas standard
                continue
        else:
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
