from music21 import scale, chord, pitch


def parse_chord_robust(chord_str):
    """
    Analyse une chaîne de caractères d'accord de manière robuste et retourne un objet Chord.
    """
    try:
        # Tente la méthode directe, qui fonctionne pour "C", "G7", etc.
        return chord.Chord(chord_str)
    except Exception:
        # En cas d'échec, tente de gérer les cas courants comme "Am", "F#m", "Bdim"
        try:
            if chord_str.endswith("dim"):
                root = chord_str[:-3]
                return chord.Chord(f"{root} diminished")
            if chord_str.endswith("m"):
                root = chord_str[:-1]
                return chord.Chord(f"{root} minor")
        except Exception:
            return None
    return None


def trouver_tonalite(progression_accords):
    """
    Analyse une progression d'accords pour trouver la tonalité la plus probable
    en se basant sur la correspondance de toutes les notes des accords.
    """
    # Étape 1 : Initialiser les 24 tonalités possibles (majeures et mineures)
    scores = {}
    possible_keys = []
    for i in range(12):
        possible_keys.append(scale.MajorScale(pitch.Pitch(i)))
        possible_keys.append(scale.MinorScale(pitch.Pitch(i)))

    for key in possible_keys:
        scores[key.name] = 0

    # Étape 2 : Analyser chaque accord de la progression
    for accord_str in progression_accords:
        accord_obj = parse_chord_robust(accord_str)
        if accord_obj is None:
            print(f"Avertissement : L'accord '{accord_str}' n'a pas pu être analysé.")
            continue

        notes_accord = {p.name for p in accord_obj.pitches}

        # Étape 3 : Comparer l'accord à chaque tonalité possible
        for key in possible_keys:
            notes_gamme = {p.name for p in key.pitches}

            # Score de base : +1 pour chaque note de l'accord qui est dans la gamme
            correspondance = len(notes_accord.intersection(notes_gamme))
            scores[key.name] += correspondance

            # Bonus si l'accord est "parfaitement" diatonique
            if correspondance == len(notes_accord):
                scores[key.name] += 1

                # Bonus si la fondamentale est la tonique (I) ou la dominante (V)
                if accord_obj.root().name == key.tonic.name:
                    scores[key.name] += 2  # La tonique est très importante
                if accord_obj.root().name == key.getDominant():
                    scores[key.name] += 1  # La dominante aussi

    # Étape 4 : Trouver le meilleur score
    if not any(scores.values()):
        return None, None

    meilleure_tonalite_nom = max(scores, key=scores.get)

    # Formatter le résultat
    parts = meilleure_tonalite_nom.split(" ")
    return parts[0], parts[1]


# --- Exemples d'utilisation ---

print("--- Analyse de la progression en Do Mineur / Mi bémol Majeur ---")
progression_test = ["Cm", "Ab", "Eb", "Bb"]
tonique, mode = trouver_tonalite(progression_test)
if tonique:
    # Le résultat attendu est Eb major (vi-IV-I-V) ou C minor (i-VI-III-VII)
    # L'algorithme favorise souvent le majeur car il contient la dominante de son relatif mineur.
    print(f"Progression : {progression_test}")
    print(f"La tonalité est : {tonique} {mode}\n")
else:
    print("Pas de tonique trouvé\n")


print("--- Analyse de la progression en La Majeur ---")
accords_la_majeur = ["A", "D", "F#m", "E"]
tonique, mode = trouver_tonalite(accords_la_majeur)
if tonique:
    print(f"Progression : {accords_la_majeur}")
    print(f"La tonalité est : {tonique} {mode}\n")
else:
    print("Pas de tonique trouvé\n")
