from constants import CHARACTERISTIC_DEGREES, MODES_DATA, TYPICAL_PATTERNS
from utils.common import (
    get_note_from_index,
    get_note_index,
    is_chord_compatible,
    parse_chord,
)


def _get_degrees_for_hypothesis(parsed_progression, tonic_idx, mode_intervals):
    try:
        return [
            mode_intervals.index((c[0] - tonic_idx + 12) % 12)
            for c in parsed_progression
        ]
    except ValueError:
        return None


def guess_by_exact_pattern(parsed, modes_data, typical_patterns):
    for tonic_idx in range(12):
        for mode_name, (intervals, qualities, _) in modes_data.items():
            degrees = _get_degrees_for_hypothesis(parsed, tonic_idx, intervals)
            if degrees is None:
                continue

            for pattern in typical_patterns.get(mode_name, []):
                if degrees == pattern["degrees"]:
                    is_fully_compatible = all(
                        is_chord_compatible(parsed[i][1], qualities[degree])
                        for i, degree in enumerate(degrees)
                    )
                    if is_fully_compatible:
                        tonic_note = get_note_from_index(tonic_idx)
                        return [(tonic_note, 100)]
    return None


def guess_by_harmonic_weight(parsed, modes_data):
    tonic_scores = {}
    for tonic_idx in range(12):
        # On se concentre sur les modes les plus courants
        hypotheses = {"Ionian": modes_data["Ionian"], "Aeolian": modes_data["Aeolian"]}
        best_score = -float("inf")
        best_mode_for_tonic = None

        for mode_name, (intervals, qualities, _) in hypotheses.items():
            score = 0
            # --- AMÉLIORATION 2 : Poids positionnel ---
            # Le premier et le dernier accord sont plus importants
            positional_weights = (
                [1.5] + [1.0] * (len(parsed) - 2) + [1.5] if len(parsed) > 1 else [1.5]
            )

            for i, (c_idx, c_qual) in enumerate(parsed):
                current_chord_score = 0
                try:
                    interval = (c_idx - tonic_idx + 12) % 12
                    degree = intervals.index(interval)

                    # --- CORRECTION 1 : GESTION DE LA TIERCE DE PICARDIE ---
                    # Cas spécial pour la tonique en mode mineur
                    if degree == 0 and mode_name == "Aeolian" and "m" not in c_qual:
                        # C'est une Tierce de Picardie potentielle ! C'est très positif.
                        current_chord_score += 4  # Gros bonus

                    # Logique de scoring normale
                    elif not is_chord_compatible(c_qual, qualities[degree]):
                        current_chord_score -= 2  # Pénalité pour incompatibilité
                        continue
                    else:
                        if degree == 0:
                            current_chord_score += 3  # Tonique
                        elif degree == 4:  # Dominante
                            if "m" not in c_qual and "dim" not in c_qual:
                                current_chord_score += 2
                        elif degree == 3:
                            current_chord_score += 1  # Sous-dominante
                        else:
                            current_chord_score += 0.5

                except ValueError:
                    current_chord_score -= (
                        2  # Pénalité si l'accord n'est pas dans la gamme
                    )

                # Appliquer le poids positionnel
                score += current_chord_score * positional_weights[i]

            if score > best_score:
                best_score = score
                # best_mode_for_tonic = mode_name

        tonic_note = get_note_from_index(tonic_idx)
        # On peut stocker le score et le mode trouvé pour plus de détails
        tonic_scores[tonic_note] = best_score

    return sorted(tonic_scores.items(), key=lambda x: x[1], reverse=True)


def guess_possible_tonics(progression):
    """Fonction principale qui orchestre les deux stratégies."""
    if not progression:
        return []

    parsed = [parse_chord(c) for c in progression]
    if None in parsed:
        return []

    pattern_guess = guess_by_exact_pattern(parsed, MODES_DATA, TYPICAL_PATTERNS)
    if pattern_guess:
        return pattern_guess

    return guess_by_harmonic_weight(parsed, MODES_DATA)


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
