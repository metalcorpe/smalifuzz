import os
import re
import subprocess
import sys
from itertools import chain
from pathlib import Path

import requests


class Exclusions:
    class Smali:
        class NameSpace:
            defaultNameSpace = [
                "java",
                "javax",
                "kotlin",
                "android",
            ]
            extraNameSpace = [
                "kotlinx",
                "androidx",
                "org.intellij",
                "org.jetbrains",
            ]


def removeLevel(d, level):
    if type(d) != type({}):
        return d

    if level == 0:
        removed = {}
        for k, v in d.items():
            if type(v) != type({}):
                continue
            for kk, vv in v.items():
                removed[kk] = vv
        return removed

    removed = {}
    for k, v in d.items():
        removed[k] = removeLevel(v, level - 1)
    return removed


def recursive_dict_access(some_dict: dict):
    # print (f'recursive_dict_access called on {some_dict["name"]}')
    for key, value in some_dict.items():
        # if value is an empty list
        # if isinstance(value, list) and not value:
        if isinstance(value, list):
            some_dict[key].sort()
            # print(f'key: {key} from dict {some_dict["name"]}')
        # if value is a dictionary
        elif isinstance(value, dict):
            value = dict(sorted(value.items()))
            some_dict[key] = recursive_dict_access(value)

    return some_dict


def dictionary_serializer(some_dict: dict) -> str:
    serialized = ""
    for key, value in some_dict.items():
        if isinstance(value, list) and key == "params":
            serialized += "".join(value)
        elif isinstance(value, dict):
            serialized += key
            serialized += dictionary_serializer(value)
        elif isinstance(value, str) and key == "return":
            serialized += value

    return serialized


def path_filter(x: Path):
    if os.path.isdir(x):
        pattern = r"^smali(?:_classes\d)?$"
        compiled = re.compile(pattern)
        if compiled.match(x.name):
            return True
    return False


def list_dir_with_pwd(dir: Path):
    return [dir / x for x in os.listdir(dir)]


def pathGenerator(folder: Path):
    dirList = filter(path_filter, list_dir_with_pwd(folder))

    subFolders = [x.rglob("**/*.smali") for x in dirList]

    pathIterator = chain(*subFolders)

    return pathIterator


def unpack_apk(apk_path: str, apk_tool: str, output: str) -> None:
    try:
        result = subprocess.run(
            ["java", "-jar", apk_tool, "d", "-f", "-c", apk_path, "-o", output],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        result.check_returncode()
    except subprocess.CalledProcessError as e:
        print("[-] The APK can't be decoded")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        print(f"e: {e}")
        sys.exit()


def fetch_apktool() -> Path:
    apktool_file_name = "apktool.jar"
    apktool_path = Path() / apktool_file_name
    if not apktool_path.exists():
        url = "https://github.com/iBotPeaches/Apktool/releases/download/v2.7.0/apktool_2.7.0.jar"
        # 2. download the data behind the URL
        response = requests.get(url, allow_redirects=True)
        # 3. Open the response into a new file called instagram.ico

        open(apktool_file_name, "wb").write(response.content)
        # get the current working directory
        apktool_path = Path().absolute() / apktool_file_name

    return apktool_path
