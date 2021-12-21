from argparse import ArgumentParser

# defaults
diagFileName = ""


def parse_arguments():
    parser = ArgumentParser(
        prog="diag2rdfs.py",
        description="Convert csv data exported for Lucid class diagram to an RDFSchema.",
    )
    parser.add_argument(
        "diagFileName",
        type=str,
        metavar="<fileName.csv>",
        help="Name CSV file of diagram data exported from Lucid.",
    )
    return parser.parse_args()
