# Assurez-vous que le chemin d'importation est correct pour votre structure de projet.
# Par exemple: from app.analysis.chord_analyzer import analyze_chord_in_context
from app.utils.chords_analyzer import (
    analyze_chord_in_context,
)  # À remplacer par le bon import

# --- Tests Unitaires pour `analyze_chord_in_context` ---


def test_analyze_diatonic_major_triad():
    """
    Teste l'analyse d'une triade majeure diatonique simple (IV en Do Ionian).
    La fonction doit reconnaître que c'est une triade (F) là où un accord de 7e (Fmaj7) est attendu.
    """
    result = analyze_chord_in_context("F", 0, "Ionian")  # F en Do majeur
    expected = {
        "chord": "F",
        "found_numeral": "IV",
        "expected_numeral": "IVmaj7",
        "found_quality": "",  # Triade majeure
        "expected_quality": "maj7",
        "expected_chord_name": "Fmaj7",
        "is_diatonic": True,
    }
    assert result == expected


def test_analyze_diatonic_minor7_chord():
    """
    Teste l'analyse d'un accord de 7e mineure parfaitement diatonique (ii7 en Do Ionian).
    """
    result = analyze_chord_in_context("Dm7", 0, "Ionian")  # Dm7 en Do majeur
    expected = {
        "chord": "Dm7",
        "found_numeral": "ii7",
        "expected_numeral": "ii7",
        "found_quality": "m7",
        "expected_quality": "m7",
        "expected_chord_name": "Dm7",
        "is_diatonic": True,
    }
    assert result == expected


def test_analyze_diatonic_half_diminished_chord():
    """
    Teste l'analyse d'un accord de 7e demi-diminué et la mise en forme du chiffrage (ø7).
    """
    result = analyze_chord_in_context("Bm7b5", 0, "Ionian")  # Bm7b5 en Do majeur
    expected = {
        "chord": "Bm7b5",
        "found_numeral": "viiø7",
        "expected_numeral": "viiø7",
        "found_quality": "m7b5",
        "expected_quality": "m7b5",
        "expected_chord_name": "Bm7b5",
        "is_diatonic": True,
    }
    assert result == expected


def test_analyze_non_diatonic_altered_quality():
    """
    Teste un accord dont la fondamentale est diatonique mais la qualité est altérée (II majeur au lieu de ii mineur).
    """
    result = analyze_chord_in_context("D", 0, "Ionian")  # D majeur en Do majeur
    expected = {
        "chord": "D",
        "found_numeral": "II",  # Majeur, donc chiffrage en majuscules
        "expected_numeral": "ii7",  # Attendu : Dm7
        "found_quality": "",
        "expected_quality": "m7",
        "expected_chord_name": "Dm7",
        "is_diatonic": False,  # Non diatonique car il contient un F#
    }
    assert result == expected


def test_analyze_non_diatonic_chromatic_root():
    """
    Teste un accord dont la fondamentale n'appartient pas à la gamme.
    La fonction doit retourner une analyse limitée.
    """
    result = analyze_chord_in_context("Dbmaj", 0, "Ionian")  # Db majeur en Do majeur
    expected = {
        "chord": "Dbmaj",
        "found_numeral": "(Dbmaj)",  # Notation spéciale pour les accords hors gamme
        "expected_numeral": "N/A",
        "found_quality": "maj",
        "expected_quality": None,
        "is_diatonic": False,
    }
    assert result == expected


def test_analyze_v7_in_minor_key():
    """
    Teste l'analyse du V7 dans un mode mineur naturel (Aeolian).
    C'est un cas classique d'altération non diatonique.
    """
    result = analyze_chord_in_context("E7", 9, "Aeolian")  # E7 en La mineur
    expected = {
        "chord": "E7",
        "found_numeral": "V7",
        "expected_numeral": "v7",  # Le V diatonique est mineur (Em7)
        "found_quality": "7",
        "expected_quality": "m7",
        "expected_chord_name": "Em7",
        "is_diatonic": False,  # Non diatonique car il contient un G#
    }
    assert result == expected
