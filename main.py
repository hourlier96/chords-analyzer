from modal_substitution.generator import create_modal_substitution_table

if __name__ == "__main__":
    ionian_progression = ["C", "G", "Am", "F"]
    dorian_progression = ["Cm7", "F", "Bb", "F"]
    phrygian_progression = ["Cm", "Db", "Eb", "Db"]
    lydian_progression = ["Cmaj7", "D", "G", "Am"]
    mixolydian_progression = ["C", "Bb", "F", "C"]
    aeolian_progression = ["Cm", "Ab", "Eb", "Bb"]
    locrian_progression = ["Cdim", "Db", "Ebm"]
    # create_modal_substitution_table(phrygian_progression)

    create_modal_substitution_table(lydian_progression)
