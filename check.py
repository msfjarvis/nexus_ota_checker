#!/usr/bin/env python3

import argparse
import re
from os import makedirs, path, remove

import bs4
import requests

OTA_PAGE_URL = "https://developers.google.com/android/images"


def get_latest_version_state(state_file: str) -> str:
    """
    Get latest version seen from state file
    """
    if path.isfile(state_file):
        with open(state_file) as f:
            return f.read()


def set_latest_version_state(v: str, state_file: str):
    """
    Set version in state file
    """
    if v:
        with open(state_file, "w") as f:
            return f.write(v)
    else:
        raise ValueError("Value of v cannot be falsey")


def get_page_text(url: str) -> str:
    """
    Download complete HTML text for a url
    """
    r = requests.get(url, timeout=10)
    if r.ok:
        return r.text
    else:
        r.raise_for_status()


def parse(
    device_name: str,
    state_file: str = path.join(path.dirname(path.abspath(__file__)), ".pixel_update"),
    porcelain: bool = False,
    idx_override: int = -1,
) -> str:
    soup = bs4.BeautifulSoup(get_page_text(OTA_PAGE_URL), "html.parser")
    latest = soup.find_all("tr", attrs={"id": re.compile(f"^{device_name}.*")})
    if latest and isinstance(latest, list):
        tds = latest[idx_override].findAll("td")
        version = tds[0].string.strip()
        if "Verizon" in version:
            return parse(device_name, state_file, porcelain, -2)
        link = tds[1].find("a").get("href").strip()
        chksum = tds[2].string.strip()
        if porcelain:
            message = f"{device_name}|{link}|{chksum}"
        else:
            message = f"{device_name}: {version}\n\n{link}\n\n{chksum}"

        current = get_latest_version_state(state_file)
        if current:
            if version != current:
                set_latest_version_state(version, state_file)
        else:
            set_latest_version_state(version, state_file)
        return message
    else:
        exit(
            f"No data found for codename {device_name}. Perhaps a typo or the page layout changed too much?"
        )


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("-n", "--name", required=True, help="Device codename")
    parser.add_argument(
        "-f",
        "--file",
        default=path.join(path.dirname(path.abspath(__file__)), ".pixel_update_"),
        help="File to store state in. Device codename is appended automatically.",
    )
    parser.add_argument(
        "-p",
        "--porcelain",
        default=False,
        action="store_true",
        help="Print machine readable output for scripts to parse",
    )
    args = parser.parse_args()
    state_file = args.file + args.name
    makedirs(path.dirname(state_file), exist_ok=True)
    print(parse(device_name=args.name, state_file=state_file, porcelain=args.porcelain))


if __name__ == "__main__":
    main()
