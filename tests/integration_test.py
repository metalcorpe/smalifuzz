# -*- coding: utf-8 -*-

import random
import string
import tempfile
import unittest
from pathlib import Path

import ppdeep

from smalifuzz.core import unpack_apk
from smalifuzz.helpers import fetch_apktool

# from .context import smalifuzz


class IntegrationTestSuite(unittest.TestCase):
    """Advanced test cases."""

    def test_ppdeep_comparison_success(self):
        letters = string.ascii_lowercase
        random_string = "".join(random.choice(letters) for i in range(512))
        h1 = ppdeep.hash(random_string)
        h2 = ppdeep.hash(random_string)
        percent = ppdeep.compare(h1, h2)
        self.assertEqual(percent, 100, f"Not 100% match. Match is {percent}%")

    def test_ppdeep_comparison_fail(self):
        letters = string.ascii_lowercase
        random_string0 = "".join(random.choice(letters) for i in range(512))
        random_string1 = "".join(random.choice(letters) for i in range(512))
        h1 = ppdeep.hash(random_string0)
        h2 = ppdeep.hash(random_string1)
        percent = ppdeep.compare(h1, h2)
        self.assertLess(percent, 100, f"Match is {percent}%")

    def test_apktool_unpack_success(self):
        apktool_path = fetch_apktool()
        apk_path = Path("tests") / "test_vectors" / "app-release0.apk"
        with tempfile.TemporaryDirectory(
            suffix=None, prefix="tmp_", dir=".", ignore_cleanup_errors=False
        ) as tmpdirname:
            unpack_apk(str(apk_path), str(apktool_path), tmpdirname)
            self.assertTrue(Path(tmpdirname).exists())
            self.assertTrue((Path(tmpdirname) / "smali").exists())


# if __name__ == '__main__':
#     unittest.main()
