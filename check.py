#!/usr/bin/env python

import argparse
import re
import sys
from os import makedirs, path

from typing import Optional
import bs4
import requests

OTA_PAGE_URL = "https://developers.google.com/android/images"


def get_latest_version_state(state_file: Optional[str]) -> Optional[str]:
    """
    Get latest version seen from state file
    """
    if not state_file:
        return None
    if path.isfile(state_file):
        with open(state_file) as file:
            return file.read()
    return None


def set_latest_version_state(version: str, state_file: Optional[str]) -> Optional[int]:
    """
    Set version in state file
    """
    if not state_file:
        return 0
    if version:
        with open(state_file, "w") as file:
            return file.write(version)
    raise ValueError("Value of version cannot be falsey")


def get_page_text(url: str) -> Optional[str]:
    """
    Download complete HTML text for a url
    """
    cookies = {"devsite_wall_acks": "nexus-image-tos"}
    request = requests.get(url, timeout=10, cookies=cookies)
    if request.ok:
        return request.text
    request.raise_for_status()


def parse(
    device_name: str,
    page_text: str = "",
    state_file: Optional[str] = None,
    porcelain: bool = False,
    idx_override: int = -1,
) -> Optional[str]:
    if page_text == "":
        page_text = get_page_text(OTA_PAGE_URL)
    soup = bs4.BeautifulSoup(page_text, "html.parser")
    latest = soup.find_all("tr", attrs={"id": re.compile(f"^{device_name}.*")})
    if latest and isinstance(latest, list):
        tds = latest[idx_override].findAll("td")
        version = tds[0].string.strip()
        link = tds[2].find("a").get("href").strip()
        chksum = tds[3].string.strip()
        release_tag = re.compile(".*-(.*)-factory.*").search(link).group(1)
        if release_tag.count(".") >= 3:
            # As time progresses, the number of country/carrier specific bullshit is on the rise
            # What was one extra variant from Verizon now has 3 more. Hence, we simply keep decrementing
            # until we find a suitable version.
            new_idx = idx_override - 1
            return parse(device_name, page_text, state_file, porcelain, new_idx)
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
        sys.exit(
            f"No data found for codename {device_name}. Perhaps a typo or the page layout changed too much?"
        )
        return None


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
