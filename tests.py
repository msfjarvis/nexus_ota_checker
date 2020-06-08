import unittest
from check import parse


class Bs4Test(unittest.TestCase):
    def test_parse(self):
        with open("testdata/ota_page.html", "r") as f:
            page_text = f.read()
        data = parse("walleye", page_text=page_text, porcelain=True).split("|")
        self.assertEqual(4, len(data))
        self.assertEqual("walleye", data[0])
        self.assertEqual("qq3a.200605.001", data[1])
        self.assertEqual(
            "https://dl.google.com/dl/android/aosp/walleye-qq3a.200605.001-factory-66e8d94e.zip",
            data[2],
        )
        self.assertEqual(
            "66e8d94e168420e7cbe19f67b3a127e2ae55a61e44019ee10c9b11026edf4e93", data[3]
        )


if __name__ == "__main__":
    unittest.main()
