import unittest
from check import parse


class Bs4Test(unittest.TestCase):
    def test_parse(self):
        with open("testdata/ota_page.html", "r") as f:
            page_text = f.read()
        data = parse("walleye", page_text=page_text, porcelain=True).split("|")
        self.assertEqual(4, len(data))
        self.assertEqual("walleye", data[0])
        self.assertEqual("qq2a.200501.001.b3", data[1])
        self.assertEqual(
            "https://dl.google.com/dl/android/aosp/walleye-qq2a.200501.001.b3-factory-4dee41ec.zip",
            data[2],
        )
        self.assertEqual(
            "4dee41ec5c26276680723fd0c1d04460f5e8b30265360e824c6d6f29e4e1eb40", data[3]
        )


if __name__ == "__main__":
    unittest.main()
