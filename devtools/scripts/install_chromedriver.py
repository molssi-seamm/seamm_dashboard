#!/usr/bin/env python
# -*- coding: utf-8 -*-

from packaging.version import parse as parse_version
from packaging.utils import canonicalize_version
import requests
import subprocess
import sys


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


def chrome_version():
    """Return the version of Chrome installed."""
    if sys.platform == "linux" or sys.platform == "linux2":
        # linux
        exe = 'google-chrome'
    elif sys.platform == "darwin":
        # OS X
        exe = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    elif sys.platform == "win32":
        # Windows...
        raise NotImplementedError('Not yet supported on Windows')
    else:
        raise NotImplementedError(
            'Not yet supported on {}'.format(sys.platform)
        )

    result = subprocess.run(
        [exe, '--version'], check=True, shell=False, capture_output=True,
        text=True
    )
    return result.stdout.split()[2]


if __name__ == "__main__":
    # Version of Chrome installed
    version_string = chrome_version()
    version = parse_version(version_string)
    print('Chrome version = {}'.format(version))

    # Version of the Chrome driver installed, if any
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", 'chromedriver-binary'],
            check=True,
            capture_output=True,
            text=True
        )

        current_version = parse_version(
            result.stdout.splitlines()[1].split()[1]
        )
        is_installed = True
        print('Current version of chromedriver = {}'.format(current_version))
    except Exception as e:
        print(e)
        is_installed = False

    # Query the Web for the needed version
    request = '.'.join(version.base_version.split('.')[0:1])
    url = (
        'https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{}'.format(
            request
        )
    )
    response = requests.get(url)
    if response.status_code != 200:
        raise RuntimeError(
            'Error getting chrome driver version {}'.format(
                response.status_code
            )
        )
    needed_version = parse_version(response.text)

    if is_installed and (
        canonicalize_version(str(needed_version)) ==
        canonicalize_version(str(current_version))
    ):
        print('The version currently installed is correct.')
    else:
        # Remove the current version
        subprocess.check_call(
            [
                sys.executable, "-m", "pip", "uninstall", "-y",
                "chromedriver-binary"
            ]
        )
        is_installed = False

    if not is_installed:
        # Remove the current version
        subprocess.check_call(
            [
                sys.executable, "-m", "pip", "install",
                "chromedriver-binary=={}".format(needed_version)
            ]
        )
        print(
            'Installed version {} of chromedriver-binary'.format(
                needed_version
            )
        )
