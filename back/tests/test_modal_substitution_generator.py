import pytest

from app.modal_substitution.generator import get_degrees_to_borrow, get_substitutions


class TestGetDegreesToBorrow:
    def test_empty_list(self):
        """Vérifie qu'une liste vide en entrée retourne une liste vide."""
        assert get_degrees_to_borrow([]) == []

    @pytest.mark.parametrize(
        "analysis, expected",
        [
            (
                [
                    {"found_numeral": "Imaj7"},
                    {"found_numeral": "V7"},
                    {"found_numeral": "vi-7"},
                ],
                [1, 5, 6],
            ),
            ([{"found_numeral": "(V7/V)"}, {"found_numeral": "ii-7"}], [None, 2]),
            ([{}, {"found_numeral": ""}], [None, None]),
            (
                [
                    {"found_numeral": "IVmaj7"},
                    {"found_numeral": "(iii-7)"},
                    {"found_numeral": "V7"},
                ],
                [4, None, 5],
            ),
            ([{"found_numeral": "VIII"}], [None]),
        ],
    )
    def test_various_cases(self, analysis, expected):
        """Teste plusieurs scénarios de conversion de chiffrages en degrés."""
        assert get_degrees_to_borrow(analysis) == expected


class TestGetSubstitutions:
    def test_basic_substitution_ionian(self):
        """
        Teste une substitution en Do Ionien.
        """
        base_prog = [{}, {}, {}]
        degrees = [2, 5, 1]
        result = get_substitutions(base_prog, 0, degrees)  # Tonique = C

        expected = [
            {"chord": "Dm7", "roman": "ii", "quality": "m7"},
            {"chord": "G7", "roman": "V", "quality": "7"},
            {"chord": "Cmaj7", "roman": "I", "quality": "maj7"},
        ]
        assert result == expected

    def test_substitution_with_none_in_d_major(self):
        """
        Teste une substitution en Ré, en supposant le mode Ionien (Majeur) par défaut.
        """
        base_prog = [{}, {}]
        degrees = [4, None]
        result = get_substitutions(base_prog, 2, degrees)  # Tonique = D

        expected = [
            # Le IVème degré de Ré Majeur est Sol majeur 7 (Gmaj7).
            {"chord": "Gmaj7", "roman": "IV", "quality": "maj7"},
            {"chord": "N/A", "roman": None, "quality": None},
        ]
        assert result == expected

    def test_cycling_of_borrowed_chords_in_g_major(self):
        """
        Vérifie que la liste de substitution se répète en Sol,
        en supposant le mode Ionien (Majeur) par défaut.
        """
        base_prog = [{}, {}, {}, {}]  # 4 accords
        degrees = [6, 4]  # 2 substitutions
        result = get_substitutions(base_prog, 7, degrees)  # Tonique = G

        # Le VIème degré de Sol Majeur est Mi mineur 7 (Em7).
        sub1 = {"chord": "Em7", "roman": "vi", "quality": "m7"}
        # Le IVème degré de Sol Majeur est Do majeur 7 (Cmaj7).
        sub2 = {"chord": "Cmaj7", "roman": "IV", "quality": "maj7"}

        expected = [sub1, sub2, sub1, sub2]
        assert result == expected

    def test_empty_degrees_to_borrow(self):
        """
        Vérifie que la progression de base est retournée si la liste de degrés est vide.
        """
        base_prog = ["C", "G", "Am"]
        expected_result = [
            {
                "chord": "C",
                "quality": None,
                "roman": None,
            },
            {
                "chord": "G",
                "quality": None,
                "roman": None,
            },
            {
                "chord": "Am",
                "quality": None,
                "roman": None,
            },
        ]
        degrees = []
        result = get_substitutions(base_prog, 0, degrees)

        assert result == expected_result

    def test_all_none_degrees(self):
        """
        Vérifie le comportement si tous les degrés sont None.
        """
        base_prog = [{}, {}]
        degrees = [None, None]
        result = get_substitutions(base_prog, 0, degrees)

        na_chord = {"chord": "N/A", "roman": None, "quality": None}
        expected = [na_chord, na_chord]
        assert result == expected
