from tabulate import tabulate

from utils.common import (
    _get_core_quality,
    get_note_from_index,
    get_note_index,
    get_roman_numeral,
    parse_chord,
)
from utils.mode_detection import detect_mode, guess_possible_tonics


def get_secondary_dominant_for_target(target_chord_name, tonic_name, mode_name):
    """
    Calcule la dominante (primaire ou secondaire) qui cible un accord donné.
    Retourne la dominante et son analyse fonctionnelle dans la tonalité.
    """
    parsed_target = parse_chord(target_chord_name)
    if not parsed_target:
        return "N/A", "Accord non reconnu"

    target_root_index, target_quality = parsed_target

    # On ne crée généralement pas de dominante pour une cible diminuée.
    if _get_core_quality(target_quality) == "dim":
        return "N/A", "(Cible diminuée)"

    # 1. Trouver la fondamentale de la dominante (une quinte juste au-dessus de la cible)
    dominant_root_index = (target_root_index + 7) % 12
    dominant_root_name = get_note_from_index(dominant_root_index)

    # La dominante est toujours un accord de 7ème.
    dominant_chord = f"{dominant_root_name}7"

    # 2. Analyser la fonction de cette dominante dans la tonalité
    tonic_index = get_note_index(tonic_name)

    # Obtenir le chiffrage romain de la cible pour l'analyse
    _, target_numeral = get_roman_numeral(target_chord_name, tonic_index, mode_name)

    # Cas spécial : si la cible est la tonique (I), c'est la dominante primaire
    if target_numeral.upper() in ["I", "(I)"]:
        analysis = "V7 (Dominante Primaire)"
    else:
        analysis = f"V7/{target_numeral}"

    return dominant_chord, analysis


def create_secondary_dominant_table(progression):
    """
    Analyse une progression et crée une table montrant la dominante secondaire
    potentielle pour chaque accord de la progression.
    """
    if not progression or len(progression) < 1:
        print("La progression est vide.")
        return

    print("\nSecondary Dominants")

    tonic_candidates = guess_possible_tonics(progression)
    tonic_name = tonic_candidates[0][0]
    mode_name = detect_mode(progression, tonic_name)
    if not mode_name:
        mode_name = "Ionian"  # Fallback
    print(f"{tonic_name} {mode_name}")

    table_data = []
    headers = ["Dominant", "Chord", "Analyze"]

    for chord in progression:
        if tonic_name:
            secondary_dominant, analysis = get_secondary_dominant_for_target(
                chord, tonic_name, mode_name
            )
            table_data.append([secondary_dominant, chord, analysis])
        else:
            secondary_dominant, _ = get_secondary_dominant_for_target(
                chord, "C", "Ionian"
            )
            table_data.append([secondary_dominant, chord, "N/A (Tonalité inconnue)"])

    print(tabulate(table_data, headers=headers, tablefmt="grid"))
