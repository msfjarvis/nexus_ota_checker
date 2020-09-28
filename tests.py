import unittest
from check import parse


class Bs4Test(unittest.TestCase):
    def test_parse(self):
        with open("testdata/ota_page.html", "r") as file:
            page_text = file.read()
        data = parse("walleye", page_text=page_text, porcelain=True).split("|")
        self.assertEqual(4, len(data))
        self.assertEqual("walleye", data[0])
        self.assertEqual("qq3a.200705.002", data[1])
        self.assertEqual(
            "https://dl.google.com/dl/android/aosp/walleye-qq3a.200705.002-factory-c144ce29.zip",
            data[2],
        )
        self.assertEqual(
            "c144ce2919f94c4c57a5bd3bb9ae73d242fec52f170e4d1055ac17d0cc884d9e", data[3]
        )


if __name__ == "__main__":
    unittest.main()
