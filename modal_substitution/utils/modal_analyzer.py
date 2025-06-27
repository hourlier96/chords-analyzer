from modal_substitution.utils.utils import (
    get_note_index,
    parse_chord,
    is_chord_compatible,
)
from modal_substitution.constants import CHARACTERISTIC_DEGREES, MODES_DATA


def detect_mode(progression, tonic):
    """
    Détecte le mode le plus probable pour une progression et une tonique données,
    en se basant sur la compatibilité diatonique et le poids des accords caractéristiques.
    """
    tonic_idx = get_note_index(tonic)
    if tonic_idx is None or not progression:
        return None

    parsed = [parse_chord(c) for c in progression]
    if None in parsed:
        return None

    best_mode_name = None
    best_score = -float("inf")

    for mode_name, (intervals, qualities, _) in MODES_DATA.items():

        current_score = 0

        # On récupère les degrés caractéristiques pour ce mode
        characteristic_degrees = CHARACTERISTIC_DEGREES.get(mode_name, [])

        for c_idx, c_qual in parsed:
            try:
                interval = (c_idx - tonic_idx + 12) % 12
                degree = intervals.index(interval)

                if is_chord_compatible(c_qual, qualities[degree]):
                    # +1 point pour chaque accord compatible
                    current_score += 1
                    # +3 points bonus si c'est un accord caractéristique du mode
                    if degree in characteristic_degrees:
                        current_score += 3
                else:
                    # -1 point pour une qualité incorrecte
                    current_score -= 1
            except ValueError:
                # -2 points pour un accord totalement hors gamme
                current_score -= 2

        # Ambiguité totale: préference par défaut
        if mode_name in ["Ionian", "Aeolian"]:
            current_score += 0.1

        if current_score > best_score:
            best_score = current_score
            best_mode_name = mode_name

    return best_mode_name
