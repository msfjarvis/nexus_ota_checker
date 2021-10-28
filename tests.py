#!/usr/bin/env python

import unittest
from check import parse


class Bs4Test(unittest.TestCase):
    def test_parse(self):
        with open("testdata/ota_page.html", "r") as file:
            page_text = file.read()
        data = parse("raven", page_text=page_text, porcelain=True).split("|")
        self.assertEqual(4, len(data))
        self.assertEqual("raven", data[0])
        self.assertEqual("sd1a.210817.015.a4", data[1])
        self.assertEqual(
            "https://dl.google.com/dl/android/aosp/raven-sd1a.210817.015.a4-factory-bd6cb030.zip",
            data[2],
        )
        self.assertEqual(
            "bd6cb030402897f58b952008211640f5241699200d509926540425e00b115bc9", data[3]
        )


if __name__ == "__main__":
    unittest.main()
