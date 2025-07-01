import re
from constants import (
    CORE_QUALITIES,
    MODES_DATA,
    ROMAN_DEGREES,
)
from app.utils.common import (
    get_note_index,
    is_chord_compatible,
    parse_chord,
)


def find_possible_modes_for_chord(borrowed_chord_name, tonic_name):
    """
    Analyse un accord emprunté et retourne la liste des modes parallèles
    auxquels il pourrait appartenir diatoniquement.

    Args:
        borrowed_chord_name (str): Le nom de l'accord à analyser (ex: "Emaj7").
        tonic_name (str): La tonique de référence (ex: "C#").

    Returns:
        list: Une liste de noms de modes (ex: ['Dorian', 'Aeolian']).
    """
    possible_modes = []
    parsed_borrowed_chord = parse_chord(borrowed_chord_name)
    if not parsed_borrowed_chord:
        return []

    borrowed_root_index, borrowed_quality = parsed_borrowed_chord
    tonic_index = get_note_index(tonic_name)

    # On teste chaque mode défini dans nos données
    for mode_name, (intervals, qualities, _) in MODES_DATA.items():
        # 1. Calculer l'intervalle entre la tonique et la fondamentale de l'accord emprunté
        interval_from_tonic = (borrowed_root_index - tonic_index + 12) % 12

        # 2. Vérifier si la fondamentale de l'accord appartient à l'échelle de ce mode
        if interval_from_tonic in intervals:
            degree_index = intervals.index(interval_from_tonic)

            # 3. Récupérer la qualité d'accord attendue pour ce degré dans ce mode
            expected_quality = qualities[degree_index]

            # 4. Vérifier si la qualité réelle de l'accord est compatible avec la qualité attendue
            if is_chord_compatible(borrowed_quality, expected_quality):
                # C'est un match ! L'accord est diatonique à ce mode.
                possible_modes.append(mode_name)

    return possible_modes


def get_borrowed_chords(
    quality_analysis: list[dict], tonic_name: str, original_mode: str
) -> dict:
    """
    Identifie les accords empruntés à partir d'une analyse détaillée.

    Args:
        quality_analysis: La liste de dictionnaires retournée par l'analyse.
        tonic_name: La tonique de référence.
        original_mode: Le mode de référence.

    Returns:
        Un dictionnaire des accords empruntés et des modes dont ils pourraient provenir.
    """
    borrowed_chords = {}

    # On vérifie la nature du mode d'origine (majeur ou mineur)
    original_mode_core_quality = CORE_QUALITIES.get(
        MODES_DATA[original_mode][1][0], "major"
    )

    for analysis_item in quality_analysis:

        # On ne traite que les accords qui ne sont pas diatoniques
        if not analysis_item.get("is_diatonic"):

            chord_name = analysis_item["chord"]
            found_quality = analysis_item["found_quality"]
            base_numeral = analysis_item["found_numeral"]  # ex: "V"

            # --- Règle d'exception pour le V7 en mode mineur ---
            # Si le mode d'origine est mineur, que l'accord est un Vème degré
            # et que la qualité jouée est une 7ème de dominante,
            # on le considère comme une altération standard et non un emprunt.
            if (
                original_mode_core_quality == "minor"
                and base_numeral == "V"
                and found_quality == "7"
            ):
                continue  # On passe à l'accord suivant

            # --- C'est un véritable accord emprunté ---
            # On cherche de quels autres modes de la même tonique il pourrait provenir
            # (Cette partie fait appel à une fonction que vous devez avoir)
            possible_modes = find_possible_modes_for_chord(chord_name, tonic_name)

            if possible_modes:
                # On s'assure de ne pas lister le mode d'origine lui-même
                modes_str_list = [
                    f"{mode}" for mode in possible_modes if mode != original_mode
                ]
                if modes_str_list:
                    borrowed_chords[chord_name] = modes_str_list

    return borrowed_chords
