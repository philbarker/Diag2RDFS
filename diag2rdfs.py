#!/usr/bin/env python
from Diag2RDFS import Diag2RDFSConverter
from parseArguments import parse_arguments
from pprint import PrettyPrinter

if __name__ == "__main__":
    args = parse_arguments()
    c = Diag2RDFSConverter()
    pp = PrettyPrinter()
    c.convertDiag2RDFS(args.diagFileName)
    c.writeSchema()
