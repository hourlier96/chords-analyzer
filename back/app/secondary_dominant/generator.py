from app.utils.common import (
    _get_core_quality,
    get_note_from_index,
    get_note_index,
    is_chord_compatible,
    parse_chord,
)
from constants import CORE_QUALITIES, MODES_DATA, ROMAN_DEGREES


def _format_roman_numeral_from_quality(base_numeral, quality, core_qualities_map):
    """
    Fonction aide : met en forme un chiffrage romain (ex: 'V') et une qualité ('m7')
    en une chaîne de caractères finale (ex: 'v7').
    """
    display_numeral = base_numeral
    core_quality = core_qualities_map.get(quality, "major")  # "major" par défaut
    if core_quality in ["minor", "diminished"]:
        display_numeral = display_numeral.lower()

    suffix_map = {
        "maj7": "maj7",
        "m7": "7",
        "7": "7",
        "m7b5": "ø7",
        "dim7": "°7",
        "dim": "°",
    }
    suffix = suffix_map.get(quality, "")

    return display_numeral + suffix


def get_roman_numeral(chord_name, tonic_index, mode_name):
    """
    Analyse un accord et retourne un tuple contenant le chiffrage attendu (diatonique)
    et le chiffrage réel (joué).
    """
    parsed_chord = parse_chord(chord_name)
    if not parsed_chord:
        return (f"({chord_name})", f"({chord_name})")

    chord_index, found_quality = parsed_chord
    interval = (chord_index - tonic_index + 12) % 12

    mode_intervals, mode_qualities, _ = MODES_DATA[mode_name]

    if interval not in mode_intervals:
        return (f"({chord_name})", f"({chord_name})")

    degree_index = mode_intervals.index(interval)
    base_numeral = ROMAN_DEGREES[degree_index]

    expected_quality = mode_qualities[degree_index]

    expected_numeral = _format_roman_numeral_from_quality(
        base_numeral, expected_quality, CORE_QUALITIES
    )

    found_numeral = _format_roman_numeral_from_quality(
        base_numeral, found_quality, CORE_QUALITIES
    )

    is_borrowed = not is_chord_compatible(found_quality, expected_quality)
    found_numeral = found_numeral if not is_borrowed else f"({found_numeral})"
    return (
        expected_numeral,
        found_numeral,
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
