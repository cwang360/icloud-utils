import sys
import os
import time
import shutil
import argparse
from pyicloud import PyiCloudService

def get_args():
    parser = argparse.ArgumentParser(description='Export and save iCloud photos in folders organized by date.')
    parser.add_argument('-username', required=True,
                        help='iCloud account email')
    parser.add_argument('-password', required=True,
                        help='iCloud account password')
    parser.add_argument('-outdir', required=True,
                        help='output directory to save folders to, will be clobbered')
    return parser.parse_args()

def login(email, password):
    api = PyiCloudService(email, password)

    if api.requires_2fa:
        print("Two-factor authentication required.")
        code = input("Enter the code you received of one of your approved devices: ")
        result = api.validate_2fa_code(code)
        print("Code validation result: %s" % result)

        if not result:
            print("Failed to verify security code")
            sys.exit(1)

        if not api.is_trusted_session:
            print("Session is not trusted. Requesting trust...")
            result = api.trust_session()
            print("Session trust result %s" % result)

            if not result:
                print("Failed to request trust. You will likely be prompted for the code again in the coming weeks")
    elif api.requires_2sa:
        import click
        print("Two-step authentication required. Your trusted devices are:")

        devices = api.trusted_devices
        for i, device in enumerate(devices):
            print(
                "  %s: %s" % (i, device.get('deviceName',
                "SMS to %s" % device.get('phoneNumber')))
            )

        device = click.prompt('Which device would you like to use?', default=0)
        device = devices[device]
        if not api.send_verification_code(device):
            print("Failed to send verification code")
            sys.exit(1)

        code = click.prompt('Please enter validation code')
        if not api.validate_verification_code(device, code):
            print("Failed to verify verification code")
            sys.exit(1)
    return api

def main():
    args = get_args()
    api = login(args.username, args.password)
    ROOT_DIR = os.path.abspath(args.outdir)
    if os.path.exists(ROOT_DIR):
        shutil.rmtree(ROOT_DIR)
    os.mkdir(ROOT_DIR)
    photos = api.photos.all
    total = photos.__len__()
    curr = 0
    for photo in api.photos.all:
        curr += 1
        print(f"{curr}/{total}", photo, photo.filename)
        year = str(photo.asset_date.year)
        date = str(photo.asset_date.date())
        if year not in os.listdir(ROOT_DIR):
            os.mkdir(os.path.join(ROOT_DIR, year))
        if date not in os.listdir(os.path.join(ROOT_DIR, year)):
            os.mkdir(os.path.join(ROOT_DIR, year, date))
        download = photo.download("original")
        photo_path = os.path.join(ROOT_DIR, year, date, photo.filename)
        with open(photo_path, 'wb') as opened_file:
            opened_file.write(download.raw.read())
        mod_date = time.mktime(photo.asset_date.timetuple())
        # Set created/modified date to asset date. Exif metadata is preserved.
        os.utime(photo_path, (mod_date, mod_date))
    print(f"Saved {curr} files to {ROOT_DIR}")

if __name__ == "__main__":
    main()