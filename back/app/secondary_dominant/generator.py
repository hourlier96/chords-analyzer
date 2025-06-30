from app.utils.common import (
    _get_core_quality,
    get_note_from_index,
    get_note_index,
    get_roman_numeral,
    parse_chord,
)


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
