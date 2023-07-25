from argparse import Namespace
from pathlib import Path

import ppdeep

from smalifuzz.cli import cli
from smalifuzz.core import generate_signature
from smalifuzz.helpers import fetch_apktool


def main():
    args:Namespace = cli()
    if args.apktool == None:
        fetch_apktool()
        apktoolPath = Path(".\\apktool.jar")
    else:
        apktoolPath = Path(args.apktool)
    apk: Path = Path(args.path)
    result = generate_signature(apk, apktoolPath)
    hash = ppdeep.hash(result)
    print(hash)


if __name__ == "__main__":
    main()
