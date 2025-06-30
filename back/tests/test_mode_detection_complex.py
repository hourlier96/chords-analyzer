from app.utils.mode_detection import detect_mode, guess_possible_tonics


def test_mode_for_vi_IV_I_V_is_ionian():
    """
    Pour une progression vi-IV-I-V en Do majeur, le mode doit être Ionien.
    """
    progression = ["Am", "F", "C", "G"]
    tonic = "C"
    expected_mode = "Ionian"

    guessed_tonic = guess_possible_tonics(progression)[0][0]
    assert (
        guessed_tonic == tonic
    ), f"Tonic detection failed, expected {tonic} but got {guessed_tonic}"

    detected_mode = detect_mode(progression, guessed_tonic)
    assert detected_mode == expected_mode


def test_mode_for_iii_vi_IV_I_is_ionian():
    """
    Pour une progression iii-vi-IV-I en Sol majeur, le mode doit être Ionien.
    """
    progression = ["Bm", "Em", "C", "G"]
    tonic = "G"
    expected_mode = "Ionian"

    guessed_tonic = guess_possible_tonics(progression)[0][0]
    assert guessed_tonic == tonic

    detected_mode = detect_mode(progression, guessed_tonic)
    assert detected_mode == expected_mode


def test_mode_for_borrowed_V_is_aeolian():
    """
    Pour une cadence i-V-i en La mineur, même avec un V majeur emprunté,
    le mode de base le plus juste est Éolien (mineur naturel).
    """
    progression = ["Am", "E7", "Am"]
    tonic = "A"
    expected_mode = "Aeolian"

    guessed_tonic = guess_possible_tonics(progression)[0][0]
    assert guessed_tonic == tonic

    detected_mode = detect_mode(progression, guessed_tonic)
    assert detected_mode == expected_mode


def test_mode_for_borrowed_V_with_major_IV_is_dorian():
    """
    Pour une progression en Ré mineur qui contient un IV majeur (Sol),
    la signature du mode Dorien, le mode détecté doit être Dorien.
    """
    progression = ["Dm", "A", "G", "Dm"]
    tonic = "D"
    expected_mode = "Dorian"

    guessed_tonic = guess_possible_tonics(progression)[0][0]
    assert guessed_tonic == tonic

    detected_mode = detect_mode(progression, guessed_tonic)
    assert detected_mode == expected_mode


def test_mode_for_modal_interchange_is_ionian():
    """
    Malgré l'emprunt du iv mineur (Fm), le contexte général (C et F majeur)
    ancre la progression en mode Ionien.
    """
    progression = ["C", "F", "Fm", "C"]
    tonic = "C"
    expected_mode = "Ionian"

    guessed_tonic = guess_possible_tonics(progression)[0][0]
    assert guessed_tonic == tonic

    detected_mode = detect_mode(progression, guessed_tonic)
    assert detected_mode == expected_mode


def test_mode_for_flat_vii_prog_is_mixolydian():
    """
    La présence du bVII (accord de Sol en La) est la signature du mode Mixolydien.
    """
    progression = ["A", "G", "D", "A"]
    tonic = "A"
    expected_mode = "Mixolydian"

    guessed_tonic = guess_possible_tonics(progression)[0][0]
    assert guessed_tonic == tonic

    detected_mode = detect_mode(progression, guessed_tonic)
    assert detected_mode == expected_mode


def test_mode_for_lydian_ambiguity_winner_is_ionian():
    """
    Pour la progression C-D-Em-G, la tonique la plus forte est G.
    Le mode correspondant pour cette tonalité est donc G Ionien.
    """
    progression = ["C", "D", "Em", "G"]
    tonic = "G"
    expected_mode = "Ionian"

    guessed_tonic = guess_possible_tonics(progression)[0][0]
    assert guessed_tonic == tonic

    detected_mode = detect_mode(progression, guessed_tonic)
    assert detected_mode == expected_mode
