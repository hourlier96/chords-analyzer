from constants import (
    MODES_DATA,
    NOTE_INDEX_MAP,
    NOTES,
    CORE_QUALITIES,
)


# Returns the chromatic index (0–11) for a given note string
def get_note_index(note_str):
    note_map = {
        "DB": "C#",
        "EB": "D#",
        "FB": "E",
        "GB": "F#",
        "AB": "G#",
        "BB": "A#",
        "B#": "C",
    }

    # Normalize the note by stripping extensions and accidentals
    clean_note = (
        note_str.upper()
        .replace("♭", "B")
        .split("M")[0]
        .split("m")[0]
        .split("°")[0]
        .split("dim")[0]
        .split("7")[0]
        .split("ø")[0]
    )

    # Special case for "Cb" (B double flat)
    if clean_note == "CB":
        return 11

    # Map enharmonic equivalents
    if clean_note in note_map:
        clean_note = note_map[clean_note]

    # Return chromatic index
    if len(clean_note) > 1 and clean_note[1] in ["#", "B"]:
        return NOTES.index(clean_note[:2])
    return NOTES.index(clean_note[0])


# Returns note name from chromatic index (0–11)
def get_note_from_index(index):
    return NOTES[index % 12]


# Parses a chord name and returns its root index and a normalized quality string
def parse_chord(chord_name):
    chord_name = chord_name.strip()

    # Utilisation des qualités reconnues depuis CORE_QUALITIES
    KNOWN_QUALITIES = sorted(CORE_QUALITIES.keys(), key=lambda q: -len(q))

    for quality in KNOWN_QUALITIES:
        if chord_name.endswith(quality):
            root = chord_name[: -len(quality)] if len(quality) > 0 else chord_name
            try:
                root_index = get_note_index(root)
                return root_index, quality
            except ValueError:
                return None

    # Si aucun suffixe ne matche, on tente un accord majeur simple
    try:
        root_index = get_note_index(chord_name)
        return root_index, ""
    except ValueError:
        return None


def is_dominant_chord(chord_name, parsed_chord=None):
    """
    Vérifie si un accord est un accord de dominante.
    Un accord est considéré comme dominant s'il a une tierce majeure et une septième mineure.
    Pour simplifier, on cible les accords majeurs ou '7'.
    """
    if not parsed_chord:
        parsed_chord = parse_chord(chord_name)
    if not parsed_chord:
        return False

    _, quality = parsed_chord
    core_quality = _get_core_quality(quality)
    # Un accord de dominante n'est ni mineur, ni diminué.
    # On exclut aussi le 'maj7' qui a une septième majeure.
    if core_quality in ["minor", "diminished", "suspended"] or "maj7" in quality:
        return False

    return True


# Returns a diatonic 7th chord for a degree and tonic, with optional simplification
def get_diatonic_7th_chord(degree, key_tonic_index, mode_name="Ionian"):
    """
    Génère un accord de septième diatonique à partir d'un degré, d'une tonique et d'un mode.
    Cette version est robuste et gère les degrés invalides.
    """
    if degree is None or not (1 <= degree <= 7):
        return None

    mode_intervals, mode_qualities, _ = MODES_DATA[mode_name]

    chord_root_index = (key_tonic_index + mode_intervals[degree - 1]) % 12
    quality = mode_qualities[degree - 1]
    name = get_note_from_index(chord_root_index)

    return name + quality


def _get_core_quality(quality):
    if quality in CORE_QUALITIES:
        return CORE_QUALITIES[quality]
    # Cas non reconnu : essayer de simplifier
    if quality.startswith("maj"):
        return "major"
    if quality.startswith("m"):
        return "minor"
    if quality.startswith("dim") or quality.startswith("d") or quality.startswith("°"):
        return "diminished"
    if quality.startswith("aug") or quality.startswith("+"):
        return "augmented"
    if "sus" in quality:
        return "suspended"
    return "major"  # fallback


def get_scale_notes(key_tonic_str: str, mode_name: str) -> list[str]:
    """
    Génère la liste des notes d'une gamme à partir d'une tonique et d'un mode.

    Utilise la base de données MODES_DATA pour construire la gamme.

    Args:
        key_tonic_str (str): La note tonique de la gamme (ex: "C", "F#", "Bb").
        mode_name (str): Le nom du mode. Doit être une clé de MODES_DATA.
                         La recherche est insensible à la casse.

    Returns:
        list[str]: Une liste de 7 notes (chaînes de caractères) constituant la gamme.

    Raises:
        ValueError: Si la tonique ou le mode est invalide.
    """
    # 1. Valider et normaliser la tonique
    tonic_normalized = (
        key_tonic_str.upper().replace("B", "#")
        if "b" in key_tonic_str.lower()
        else key_tonic_str.upper()
    )
    if tonic_normalized not in NOTE_INDEX_MAP:
        raise ValueError(f"Tonic '{key_tonic_str}' is not a valid note name.")

    tonic_index = NOTE_INDEX_MAP[tonic_normalized]

    # 2. Valider le mode (recherche insensible à la casse)
    found_mode_key = None
    for key in MODES_DATA:
        if key.lower() == mode_name.lower():
            found_mode_key = key
            break

    if not found_mode_key:
        raise ValueError(
            f"Mode '{mode_name}' not found. Check spelling and available modes."
        )

    # 3. Récupérer les intervalles et construire la gamme
    intervals = MODES_DATA[found_mode_key][0]

    scale_notes = []
    for interval in intervals:
        note_index = (tonic_index + interval) % 12
        scale_notes.append(NOTES[note_index])

    return scale_notes


def get_chord_notes(chord_name: str) -> list[str] | None:
    """
    Analyse un nom d'accord et renvoie ses notes constitutives.

    Args:
        chord_name (str): Le nom de l'accord (ex: "C", "F#m7", "Gbsus4").

    Returns:
        list[str] | None: Une liste de notes ou None si l'accord est invalide.
    """
    # Formules d'accords (intervalles en demi-tons depuis la racine)
    CHORD_FORMULAS = {
        # --- Triades de base ---
        "": [0, 4, 7],  # Majeur (ex: C)
        "M": [0, 4, 7],  # Majeur (ex: CM)
        "m": [0, 3, 7],  # mineur (ex: Cm)
        "min": [0, 3, 7],
        "dim": [0, 3, 6],  # diminué (ex: Cdim)
        "d": [0, 3, 6],
        "aug": [0, 4, 8],  # augmenté (ex: Caug)
        # --- Accords suspendus ---
        "sus2": [0, 2, 7],
        "sus4": [0, 5, 7],
        "7sus2": [0, 2, 7, 10],
        "7sus4": [0, 5, 7, 10],
        # --- Accords de 7ème ---
        "7": [0, 4, 7, 10],  # 7e de dominante
        "maj7": [0, 4, 7, 11],  # 7e majeure
        "m7": [0, 3, 7, 10],  # 7e mineure
        "dim7": [0, 3, 6, 9],  # 7e diminuée
        "m7b5": [0, 3, 6, 10],  # 7e mineure quinte bémol (demi-diminué)
        "m(maj7)": [0, 3, 7, 11],  # mineur 7e majeure
        "maj7#5": [0, 4, 8, 11],
        # --- Accords de 6ème ---
        "m6": [0, 3, 7, 9],  # mineur 6
        # --- Accords de 9ème ---
        "maj9": [0, 4, 7, 11, 14],  # Majeur 9
        "m9": [0, 3, 7, 10, 14],  # mineur 9
        "7b9": [0, 4, 7, 10, 13],  # Dominant 7 bémol 9
        "7#9": [0, 4, 7, 10, 15],  # Dominant 7 dièse 9
        # --- Accords de 11ème ---
        # Note: La 3ce est souvent omise dans les accords de 11e, mais incluse ici pour l'analyse complète
        "m11": [0, 3, 7, 10, 14, 17],  # mineur 11
        # --- Accords de 13ème ---
        # Note: La 11e est souvent omise, mais incluse ici.
        "13": [0, 4, 7, 10, 14, 21],  # Dominant 13
        # --- Accords de dominante altérés ---
        "7b5": [0, 4, 6, 10],  # Dominant 7 bémol 5
        "7#5": [0, 4, 8, 10],  # Dominant 7 dièse 5
    }

    # 1. Analyser la racine et la qualité
    root, quality = "", ""
    if len(chord_name) > 1 and chord_name[1] in ("#", "b"):
        root = chord_name[:2]
        quality = chord_name[2:]
    else:
        root = chord_name[0]
        quality = chord_name[1:]

    # Normaliser la racine pour la recherche
    root_normalized = root.upper()
    if root_normalized not in NOTE_INDEX_MAP:
        return None  # Racine invalide

    if quality not in CHORD_FORMULAS:
        return None  # Qualité d'accord non supportée

    # 2. Construire les notes de l'accord
    tonic_index = NOTE_INDEX_MAP[root_normalized]
    intervals = CHORD_FORMULAS[quality]

    chord_notes = []
    for interval in intervals:
        note_index = (tonic_index + interval) % 12
        chord_notes.append(NOTES[note_index])

    return chord_notes


def is_chord_diatonic(chord_name: str, key_tonic_str: str, mode_name: str) -> bool:
    """
    Vérifie si toutes les notes d'un accord appartiennent à une gamme donnée.

    Args:
        chord_name (str): Le nom de l'accord à vérifier (ex: "Am7", "Csus2").
        key_tonic_str (str): La note tonique de la gamme (ex: "C", "F#").
        mode_name (str): Le nom du mode (ex: "Ionian", "Dorian").

    Returns:
        bool: True si l'accord est diatonique, False sinon.
    """
    try:
        # 1. Obtenir les notes de la gamme de la tonalité.
        scale_notes = get_scale_notes(key_tonic_str, mode_name)

        # 2. Obtenir les notes constitutives de l'accord
        chord_notes = get_chord_notes(chord_name)

        # Gérer les cas où l'accord ou la gamme est invalide.
        if not scale_notes or not chord_notes:
            return False

    except ValueError:
        # Si get_scale_notes lève une erreur, l'accord n'est pas diatonique.
        return False

    # 3. Vérifier si chaque note de l'accord est dans la gamme.
    scale_notes_set = set(scale_notes)
    for note in chord_notes:
        if note not in scale_notes_set:
            return False  # Au moins une note est en dehors de la gamme.

    # 4. Si toutes les notes sont dans la gamme, l'accord est diatonique.
    return True
