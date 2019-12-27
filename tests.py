import unittest
from check import parse


class Bs4Test(unittest.TestCase):
    def test_parse(self):
        with open("testdata/ota_page.html", "r") as f:
            page_text = f.read()
        data = parse("walleye", page_text=page_text, porcelain=True).split("|")
        self.assertEqual(4, len(data))
        self.assertEqual("walleye", data[0])
        self.assertEqual("qq1a.191205.008", data[1])
        self.assertEqual(
            "https://dl.google.com/dl/android/aosp/walleye-qq1a.191205.008-factory-fcc4bb81.zip",
            data[2],
        )
        self.assertEqual(
            "fcc4bb811eed22a4cecf3b3746ed5619ba2d25aca7a4fb6b427ae8011d68ce61", data[3]
        )


if __name__ == "__main__":
    unittest.main()
