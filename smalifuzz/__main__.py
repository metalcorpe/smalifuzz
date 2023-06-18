from pathlib import Path

from smalifuzz.helpers import fetch_apktool

from .cli import cli
from .core import generate_signature


def main():
    args = cli()
    if args.apktool == None:
        fetch_apktool()
        args.apktool = Path(".\\apktool.jar")
    result = generate_signature(args.path, args.apktool)
    print(result)