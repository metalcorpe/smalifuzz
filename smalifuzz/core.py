import tempfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from io import TextIOWrapper
from itertools import chain
from pathlib import Path
from typing import Tuple
from xml.dom.minidom import Element, parseString

import ppdeep
from smali import ClassVisitor, SmaliReader, SVMType
from smali.visitor import VisitorBase

from smalifuzz.helpers import (Exclusions, handle_dictionary, pathGenerator,
                               unpack_apk)


def handle_android_manifest(manifest: Path):
    # Documentation on Permissions in AndroidManifest.xml
    # https://developer.android.com/guide/topics/manifest/manifest-intro#perms

    result = dict()

    data = ""  # string data from file
    with open(manifest, "r") as f:
        data = f.read()

    dom = parseString(data)  # parse file contents to xml dom
    nodes = dom.getElementsByTagName(
        "uses-permission"
    )  # xml nodes named "uses-permission"
    nodes += dom.getElementsByTagName(
        "uses-permission-sdk-23"
    )  # xml nodes named "uses-permission-sdk-23"

    permissions = []  # holder for all permissions as we gather them
    # Iterate over all the uses-permission nodes
    for node in nodes:
        permissions += [
            node.getAttribute("android:name")
        ]  # save permissionName to our list

    #########################################
    mainactivity: Element | None = None  # or whatever python null is
    activities = dom.getElementsByTagName("activity")

    for activity in activities:
        filters = activity.getElementsByTagName("intent-filter")
        for intent in filters:
            actions = intent.getElementsByTagName("action")
            for action in actions:
                if action.getAttribute("android:name") == "android.intent.action.MAIN":
                    mainactivity = activity
                    break  # end intent loop
        if mainactivity:
            break  # end activity loop

    if mainactivity is not None:
        main_activity: str = mainactivity.getAttribute("android:name")
    else:
        main_activity = ""

    result["permissions"] = permissions
    result["main_activity"] = main_activity

    return result


class NamePrinterClassVisitor(ClassVisitor):
    def __init__(
        self, dictionary: dict, debug: bool, delegate: VisitorBase = None
    ) -> None:
        self.debug = debug
        self.dictionary = dictionary
        super().__init__(delegate)

    def visit_class(self, name: str, access_flags: int) -> None:
        # The provided name is the type descriptor, so we have to
        # convert it:
        self.current_class = SVMType(name)

        if self.current_class.pretty_name.startswith(
            tuple(
                Exclusions.Smali.NameSpace.defaultNameSpace
                + Exclusions.Smali.NameSpace.extraNameSpace
            )
        ):
            self.skip = True
            raise ModuleNotFoundError("Gay")
        else:
            self.skip = False

        self.dictionary[self.current_class.pretty_name] = dict()

        if self.debug:
            print("ClassName:", self.current_class.pretty_name)

    def visit_method(
        self, name: str, access_flags: int, parameters: list, return_type: str
    ) -> None:
        if self.skip:
            return

        method_type = SVMType(name)
        self.dictionary[self.current_class.pretty_name] = {
            "params": parameters,
            "return": return_type,
        }
        if self.debug:
            finding = (
                f"{method_type.pretty_name}({''.join(parameters)}) -> {return_type}"
            )
            print(f"Class: {self.current_class.pretty_name}=> Method: {finding}")

    def visit_block(self, name):
        block_type = SVMType(name)
        if self.debug:
            finding = f"{block_type.pretty_name}"
            print(f"Class: {self.current_class.pretty_name}=> Block: {finding}")
        pass

    def visit_line(self, number):
        pass


def run(reader, path) -> Tuple[str, dict | None]:
    dictionary: dict = dict()
    dictionary[path.name] = dict()
    new_var1: TextIOWrapper = open(path)
    if ".class" in new_var1.read():
        new_var1.seek(0)
        try:
            reader.visit(
                new_var1, NamePrinterClassVisitor(dictionary[path.name], False)
            )
            return path.name, dictionary[path.name]
        except ModuleNotFoundError:
            return path.name, None
        except Exception as e:
            print(e.args, str(path))
            raise e
    else:
        print(f"no .class found in {new_var1}")
        return path.name, None


def generate_signature(
    apk: Path, apk_tool: Path | None = None, temp_dir: Path | None = None
) -> str:
    reader: SmaliReader = SmaliReader(validate=False, comments=False, errors="ignore")
    apk_path: Path = Path(apk)
    _temp_dir: str | None = str(temp_dir) if temp_dir is not None else None
    dictionary: dict = dict()

    with tempfile.TemporaryDirectory(
        suffix=None, prefix="tmp_", dir=_temp_dir, ignore_cleanup_errors=True
    ) as tmpdirname:
        print("created temporary directory", tmpdirname)

        # unpacked_folder = apk_path.with_suffix("").name
        unpacked_folder: str = tmpdirname
        unpack_apk(str(apk_path), str(apk_tool), unpacked_folder)
        manifest: Path = Path(unpacked_folder) / "AndroidManifest.xml"
        manifesto: dict = handle_android_manifest(manifest)

        pathList: chain[Path] = pathGenerator(Path(unpacked_folder))

        # create process pool
        with ProcessPoolExecutor() as exe:
            # search text files asynchronously
            futures = [exe.submit(run, reader, f) for f in pathList]
            # process results
            for future in as_completed(futures):
                # get results
                path, result = future.result()
                dictionary[path] = result
                # future.result()

    # print(dictionary)
    serialized_signatures: str = handle_dictionary(dictionary)
    serialized_permissions: str = "".join(sorted(manifesto["permissions"]))

    return serialized_signatures + serialized_permissions


if __name__ == "__main__":
    apk: Path = Path("app-release0.apk")
    s0: str = generate_signature(apk)
    h0 = ppdeep.hash(s0)
    apk: Path = Path("app-release1.apk")
    s1: str = generate_signature(apk)
    h1: str = ppdeep.hash(s1)
    apk: Path = Path("app-debug.apk")
    s2: str = generate_signature(apk)
    h2: str = ppdeep.hash(s2)
    print("FML")
    ppdeep.compare(h1, h2)
    pass
