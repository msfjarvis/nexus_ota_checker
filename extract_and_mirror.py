import argparse
import hashlib
import re
from os import listdir, path, makedirs, rename, remove, removedirs
from shutil import move, rmtree
from zipfile import PyZipFile

from pySmartDL import SmartDL

from check import parse

ALL_DEVICES = ['sailfish', 'marlin', 'taimen', 'walleye', 'crosshatch', 'blueline', 'sargo', 'bonito']


def sha256_hash(file_path: str) -> str:
    if not path.isfile(file_path):
        raise Exception(f"{file_path} is not a file!")
    hash_256 = hashlib.sha256()
    with open(file_path, "rb") as full_file:
        for chunk in iter(lambda: full_file.read(2 ** 20), b""):
            hash_256.update(chunk)
    return hash_256.hexdigest()


class OtaPackage:
    def __init__(self, codename: str, url: str, checksum: str, release_tag: str):
        self.codename = codename
        self.package_url = url
        self.checksum = checksum
        self.release_tag = release_tag
        self.dest_dir = path.join(path.dirname(path.abspath(__file__)), self.codename)
        self.dest = path.join(self.dest_dir, self.package_url.split('/')[-1])

    def download(self):
        if not path.exists(self.dest_dir):
            makedirs(self.dest_dir)
        elif path.exists(self.dest):
            checksum = sha256_hash(self.dest)
            if checksum == self.checksum:
                print("Package already exists!")
                return
        downloader = SmartDL(self.package_url, self.dest)
        downloader.start()

    @staticmethod
    def __report_extract(filename: str):
        print(f"Extracting {filename}...")

    def extract_files(self):
        print("Beginning extraction...")
        if path.exists(self.get_output_dir()):
            removedirs(self.get_output_dir())
        zf = PyZipFile(self.dest)
        for file in zf.filelist:
            filename: str = file.filename
            if filename.endswith('img'):  # bootloader/radio, directly extract and copy
                self.__report_extract(filename)
                zf.extract(filename)
            elif filename.endswith('zip'):  # the meaty potatoes of everything
                zf.extract(filename)
                img_zf = PyZipFile(filename)
                images_to_extract = ('boot.img', 'dtbo.img', 'modem.img', 'vbmeta.img', 'vendor.img')
                for img in img_zf.filelist:
                    if img.filename in images_to_extract:
                        self.__report_extract(img.filename)
                        img_zf.extract(img.filename)
                        rename(img.filename, path.join(f"{self.codename}-{self.release_tag}", img.filename))
                remove(filename)

    def cleanup(self):
        rmtree(self.dest_dir)

    def get_output_dir(self):
        return path.join(path.dirname(path.abspath(__file__)), f"{self.codename}-{self.release_tag}")


def process_packages(args: argparse.Namespace):
    devices = []
    regexp = re.compile('[A-Z0-9.]+\d{6}.\d{3}')
    if not args.name:
        devices = ALL_DEVICES
    else:
        devices.append(args.name)
    makedirs(args.output, exist_ok=True)
    for device in devices:
        raw_data = parse(device, porcelain=True).split("|")
        device_name = raw_data[0]
        # This is rather terrible but I'm gonna go with it since atleast some regex is involved
        release_tag = regexp.search(raw_data[1]).group(0).lower()
        package_url = raw_data[2]
        checksum = raw_data[3]
        otapackage = OtaPackage(device_name, package_url, checksum, release_tag)
        otapackage.download()
        otapackage.extract_files()
        final_dir = path.join(args.output, otapackage.get_output_dir().split("/")[-1])
        for directory in listdir(args.output):
            if directory.startswith(device):
                rmtree(path.join(args.output, directory))
        move(otapackage.get_output_dir(), final_dir)
        if args.clean:
            otapackage.cleanup()


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-n', '--name', required=False, help="Device codename")
    parser.add_argument('-o', '--output', required=True, help="Output directory for extracted images")
    parser.add_argument('-c', '--clean', action="store_true", help="Remove downloaded images once done")
    process_packages(parser.parse_args())


if __name__ == '__main__':
    main()
