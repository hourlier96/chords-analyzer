from constants import (
    MODES_DATA,
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
    if core_quality in ["m", "dim"] or "maj7" in quality:
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


def is_chord_compatible(found_quality, expected_quality):
    found_core = _get_core_quality(found_quality)
    expected_core = _get_core_quality(expected_quality)

    if found_core == expected_core:
        return True

    # Gestion spécifique (exemple)
    if found_core == "major" and expected_core == "major":
        return True
    if found_core == "minor" and expected_core == "minor":
        return True
    if found_core == "diminished" and expected_core == "diminished":
        return True

    return False


def _get_core_quality(quality):
    if quality in CORE_QUALITIES:
        return CORE_QUALITIES[quality]
    # Cas non reconnu : essayer de simplifier
    if quality.startswith("maj"):
        return "major"
    if quality.startswith("m"):
        return "minor"
    if quality.startswith("dim") or quality.startswith("d"):
        return "diminished"
    if quality.startswith("aug"):
        return "augmented"
    return "major"  # fallback
