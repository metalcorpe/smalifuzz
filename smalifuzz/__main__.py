from pathlib import Path

from smalifuzz.cli import cli
from smalifuzz.core import generate_signature
from smalifuzz.helpers import fetch_apktool


def main():
    args = cli()
    if args.apktool == None:
        fetch_apktool()
        args.apktool = Path(".\\apktool.jar")
    result = generate_signature(args.path, args.apktool)
    print(result)


if __name__ == "__main__":
    main()
