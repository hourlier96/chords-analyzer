from modal_substitution.generator import (
    create_modal_harmonization_table,
    create_modal_substitution_table,
)
from secondary_dominant_substitution.generator import create_secondary_dominant_table
from tritone_substitution.generator import create_tritone_substitution_table

if __name__ == "__main__":

    prog = ["Am", "B", "C", "D"]

    create_modal_substitution_table(prog)

    create_modal_harmonization_table(prog)

    create_tritone_substitution_table(prog)

    create_secondary_dominant_table(prog)
