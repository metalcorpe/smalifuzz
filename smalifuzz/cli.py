import argparse
from pathlib import Path


def cli():
    parser = argparse.ArgumentParser(prog="smalifuzz")

    parser.add_argument("-p", "--path", type=Path, required=True)
    parser.add_argument("-t", "--apktool", type=Path, required=False)

    return parser.parse_args()
