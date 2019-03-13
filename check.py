#!/usr/bin/env python3

import argparse
import os
import re
import sys

import bs4
import pushbullet
import requests

ota_page_url = 'https://developers.google.com/android/images'
pushbullet_token = os.getenv('PUSHBULLET_TOKEN')


def get_latest_version_state():
    """
    Get latest version seen from state file
    """
    if os.path.isfile(state_file):
        with open(state_file) as f:
            return f.read()


def set_latest_version_state(v):
    """
    Set version in state file
    """
    if v:
        with open(state_file, 'w') as f:
            return f.write(v)
    else:
        raise ValueError('Value of v cannot be falsey')


def get_page_text(url):
    """
    Download complete HTML text for a url
    """
    r = requests.get(url, timeout=10)
    if r.ok:
        return r.text
    else:
        r.raise_for_status()


def notify(msg):
    """
    Send a message via Pushbullet
    """
    if msg:
        pb = pushbullet.PushBullet(pushbullet_token)
        pb.push_note('Nexus image update', msg)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-n', '--name', required=True, help="Device codename")
    parser.add_argument('-f', '--file', default=os.path.join(os.path.expanduser('~'), '.nexus_update_'),
                        help="File to store state in. Device codename is appended automatically.")
    args = parser.parse_args()
    state_file = args.file + args.name
    os.makedirs(os.path.dirname(state_file), exist_ok=True)

    soup = bs4.BeautifulSoup(get_page_text(ota_page_url), 'html.parser')
    latest = soup.find_all('tr', attrs={'id': re.compile('^{}.*'.format(args.name))})
    if latest and isinstance(latest, list):
        tds = latest[-1].findAll('td')
        version = tds[0].string.strip()
        link = tds[1].find('a').get('href').strip()
        chksum = tds[2].string.strip()

        current = get_latest_version_state()
        if current:
            if version != current:
                set_latest_version_state(version)
                message = '{n}: {v}\n\n{l}\n\n{c}'.format(n=args.name.title(), v=version, l=link, c=chksum)
                try:
                    notify(message)
                except Exception:
                    print('There is a new OTA, but Pushbullet failed. Here is what I know: {}'.format(message), file=sys.stderr)
                    raise
        else:
            set_latest_version_state(version)
    else:
        exit('No data found for codename {}. Perhaps a typo or the page layout changed too much?'.format(args.name))
