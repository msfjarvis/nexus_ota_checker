#!/usr/bin/env python3

import argparse
import re
from os import makedirs, path

import bs4
import requests
from typing import Optional

OTA_PAGE_URL = "https://developers.google.com/android/images"


def get_latest_version_state(state_file: Optional[str]) -> Optional[str]:
    """
    Get latest version seen from state file
    """
    if not state_file:
        return None
    if path.isfile(state_file):
        with open(state_file) as f:
            return f.read()
    return None


def set_latest_version_state(v: str, state_file: Optional[str]) -> int:
    """
    Set version in state file
    """
    if not state_file:
        return 0
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
    page_text: str = "",
    state_file: Optional[str] = None,
    porcelain: bool = False,
    idx_override: int = -1,
) -> str:
    if page_text == "":
        page_text = get_page_text(OTA_PAGE_URL)
    soup = bs4.BeautifulSoup(page_text, "html.parser")
    latest = soup.find_all("tr", attrs={"id": re.compile(f"^{device_name}.*")})
    if latest and isinstance(latest, list):
        tds = latest[idx_override].findAll("td")
        version = tds[0].string.strip()
        if "Verizon" in version:
            return parse(device_name, state_file, porcelain, -2)
        link = tds[1].find("a").get("href").strip()
        chksum = tds[2].string.strip()
        release_tag = re.compile(".*-(.*)-factory.*").search(link).group(1)
        if porcelain:
            message = f"{device_name}|{release_tag}|{link}|{chksum}"
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
