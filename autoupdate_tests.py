import unittest
from check import parse


class Bs4Test(unittest.TestCase):
    def test_parse(self):
        with open("testdata/ota_page.html", "r") as file:
            page_text = file.read()
        data = parse("walleye", page_text=page_text, porcelain=True).split("|")
        self.assertEqual(4, len(data))


if __name__ == "__main__":
    unittest.main()
