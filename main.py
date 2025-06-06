from modal_substitution.generator import create_modal_substitution_table

if __name__ == "__main__":
    # Ionian: i - ii° - III - v
    diatonic_progression = ["Cm", "D°", "Eb", "Gm"]
    create_modal_substitution_table(diatonic_progression)

    # Not diatonic: no major mode can be determined from these chords
    # No substitution table can be created
    diatonic_progression = ["Cm", "Dm#", "D", "A#"]
    create_modal_substitution_table(diatonic_progression, tonic="A#")

    # # Lydian: II - I - V - vi
    diatonic_progression = ["D7", "C", "G", "Am"]
    create_modal_substitution_table(diatonic_progression, tonic="C")
