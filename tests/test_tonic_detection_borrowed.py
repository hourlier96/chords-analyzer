from modal_substitution.utils.utils import guess_possible_tonics


def test_tonic_aeolian_with_major_dominant():
    """
    Teste la cadence la plus commune en mode mineur : i - V - i.
    Le 'E' majeur n'est pas diatonique en La éolien (qui a un Em), mais il confirme 'A' comme tonique.
    """
    progression = ["Am", "E", "Am"]
    expected_tonic = "A"

    tonic_candidates = guess_possible_tonics(progression)
    detected_tonic, _ = tonic_candidates[0]
    assert detected_tonic == expected_tonic


def test_tonic_dorian_with_major_dominant():
    """
    Similaire au cas éolien, teste la présence d'un V majeur dans un contexte dorien.
    """
    progression = ["Dm", "A", "G", "Dm"]
    expected_tonic = "D"

    tonic_candidates = guess_possible_tonics(progression)
    detected_tonic, _ = tonic_candidates[0]
    assert detected_tonic == expected_tonic


def test_tonic_with_secondary_dominant():
    """
    Teste une progression avec un dominant secondaire (E7 est le V7 de Am).
    L'algorithme ne doit pas se laisser tromper par le 'E7' et doit identifier 'C' comme tonique globale.
    """
    progression = ["C", "E7", "Am", "G"]
    expected_tonic = "C"

    tonic_candidates = guess_possible_tonics(progression)
    detected_tonic, _ = tonic_candidates[0]
    assert detected_tonic == expected_tonic


def test_tonic_with_modal_interchange_subdominant():
    """
    Teste l'emprunt modal avec la sous-dominante mineure (Fm) dans une tonalité majeure (Do).
    Très courant dans la pop et la musique de film.
    """
    progression = ["C", "F", "Fm", "C"]
    expected_tonic = "C"

    tonic_candidates = guess_possible_tonics(progression)
    detected_tonic, _ = tonic_candidates[0]
    assert detected_tonic == expected_tonic


def test_tonic_starting_on_submediant_vi():
    """
    Teste une progression qui ne commence pas sur la tonique.
    Le 'vi-IV-I-V' est très commun. La tonique 'F' apparaît en 3ème position.
    """
    progression = ["Dm", "Bb", "F", "C"]
    expected_tonic = "F"

    tonic_candidates = guess_possible_tonics(progression)
    detected_tonic, _ = tonic_candidates[0]
    assert detected_tonic == expected_tonic


def test_tonic_relative_major_minor_ambiguity():
    """
    Cette progression utilise des accords communs à Do majeur (vi-V-I) et La mineur (i-VII-III).
    Le contexte et l'ordre devraient privilégier 'C' comme centre tonal.
    """
    progression = ["Am", "G", "C"]
    expected_tonic = "C"

    tonic_candidates = guess_possible_tonics(progression)
    detected_tonic, _ = tonic_candidates[0]
    assert detected_tonic == expected_tonic


def test_tonic_ending_on_deceptive_cadence():
    """
    La progression se termine sur le vi (C#m), ce qui pourrait tromper un algo qui surpondère le dernier accord.
    La cadence V-vi (B7-C#m) renforce pourtant bien 'E' comme tonique.
    """
    progression = ["E", "A", "B7", "C#m"]
    expected_tonic = "E"

    tonic_candidates = guess_possible_tonics(progression)
    detected_tonic, _ = tonic_candidates[0]
    assert detected_tonic == expected_tonic


def test_tonic_mixolydian_flat_vii():
    """
    Teste une progression blues/rock typique avec un bVII (G en La majeur).
    Confirme que l'algorithme ne se limite pas aux gammes majeures/mineures standard.
    """
    progression = ["A", "G", "D", "A"]
    expected_tonic = "A"

    tonic_candidates = guess_possible_tonics(progression)
    detected_tonic, _ = tonic_candidates[0]
    assert detected_tonic == expected_tonic


def test_tonic_with_chromatic_passing_chord():
    """
    Teste la gestion d'un accord de passage chromatique.
    Le 'Gb' est un accord de passage entre 'G' et 'F'. La tonalité globale est clairement Do.
    """
    progression = ["C", "G", "Gb", "F"]
    expected_tonic = "C"

    tonic_candidates = guess_possible_tonics(progression)
    detected_tonic, _ = tonic_candidates[0]
    assert detected_tonic == expected_tonic


def test_tonic_four_chords_of_pop():
    """
    Un dernier test de confirmation avec la progression la plus célèbre du monde,
    dans une tonalité autre que Do, pour s'assurer que la logique est universelle.
    """
    progression = ["G", "D", "Em", "C"]
    expected_tonic = "G"

    tonic_candidates = guess_possible_tonics(progression)
    detected_tonic, _ = tonic_candidates[0]
    assert detected_tonic == expected_tonic
