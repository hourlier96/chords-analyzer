from app.utils.chords_analyzer import analyze_chord_in_context


def test_analyze_diatonic_major_triad():
    """
    Teste l'analyse d'une triade majeure diatonique (IV en Do Ionian).
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


# --- CAS NON-DIATONIQUES (Comportement mis à jour) ---


def test_analyze_secondary_dominant():
    """
    CORRIGÉ: Teste un accord dont la fondamentale est diatonique mais la qualité est altérée (II majeur, ou V/V).
    Avec la logique corrigée, la fonction doit s'attendre à l'accord diatonique du mode ACTUEL (ii7).
    """
    result = analyze_chord_in_context("D", 0, "Ionian")  # D majeur en Do majeur
    expected = {
        "chord": "D",
        "found_numeral": "II",  # Majeur, donc chiffrage en majuscules
        "expected_numeral": "ii7",  # Attendu diatoniquement : Dm7
        "found_quality": "",
        "expected_quality": "m7",
        "expected_chord_name": "Dm7",
        "is_diatonic": False,  # Non diatonique car il contient un F#
    }
    assert result == expected


def test_analyze_neapolitan_chord():
    """
    MIS À JOUR: Teste un accord sur une fondamentale chromatique (bII).
    Le chiffrage trouvé est maintenant précis (bIImaj) au lieu de générique.
    L'accord attendu est N/A car bII n'est pas dans le mode parallèle (Do éolien).
    """
    result = analyze_chord_in_context("Dbmaj7", 0, "Ionian")  # Dbmaj7 en Do majeur
    expected = {
        "chord": "Dbmaj7",
        "found_numeral": "bIImaj7",  # Analyse chromatique précise
        "expected_numeral": "N/A",  # Pas d'équivalent direct dans le mode parallèle
        "found_quality": "maj7",
        "expected_quality": None,
        "expected_chord_name": "N/A",
        "is_diatonic": False,
    }
    assert result == expected


def test_analyze_v7_in_minor_key_borrowing_from_major():
    """
    MIS À JOUR: Teste le V7 en mode mineur.
    L'accord attendu est maintenant V7, car il est considéré comme un emprunt au mode parallèle majeur (La Ionien),
    où le V7 est l'accord naturel.
    """
    result = analyze_chord_in_context("E7", 9, "Aeolian")  # E7 en La mineur
    expected = {
        "chord": "E7",
        "found_numeral": "V7",
        "expected_numeral": "V7",  # Attendu via emprunt au parallèle majeur (A Ionian)
        "found_quality": "7",
        "expected_quality": "7",  # La qualité attendue de l'emprunt
        "expected_chord_name": "E7",
        "is_diatonic": False,  # Non diatonique à La éolien car il contient un G#
    }
    assert result == expected


# --- NOUVEAU TEST: Cas spécifique de la demande initiale ---


def test_analyze_borrowed_chord_from_parallel_minor():
    """
    NOUVEAU TEST: Valide le cas exact de la demande : un accord sur bIII (D#) en Do majeur.
    La fonction doit l'analyser comme bIII et trouver l'accord attendu (bIIImaj7) depuis le mode parallèle mineur.
    """
    result = analyze_chord_in_context("D#add9", 0, "Ionian")  # D#add9 en Do majeur
    expected = {
        "chord": "D#add9",
        "found_numeral": "bIIIadd9",  # Chiffrage chromatique précis
        "expected_numeral": "bIIImaj7",  # Accord attendu via emprunt (Ebmaj7 de C Aeolian)
        "found_quality": "add9",
        "expected_quality": "maj7",
        "expected_chord_name": "Ebmaj7",  # Nom correct avec enharmonie
        "is_diatonic": False,  # Non diatonique
    }
    assert result == expected
