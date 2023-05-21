import hashlib
import sys
import json
import subprocess
import os
import requests
import io
import time

from os import path
from pathlib import Path


# dev constants
instance_folder = Path("./instance/")
_json = "demo.json"
# _json = "modrinth.index.json"


def init():
    with open(_json) as jsonfile:
        x = json.load(jsonfile)
    return x


def download(url, path, hash):
    """
    Downloads a file from a given URL and saves it to a specified path if the SHA1 hash matches the expected hash.

    Args:
        url (str): The URL of the file to be downloaded.
        path (str): The file path where the downloaded file will be saved.
        hash (str): The SHA1 hash value of the expected file.

    Raises:
        RuntimeError: If the download fails or if the downloaded file fails the hash check.

    Returns:
        None
    """
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        file_bytes = io.BytesIO(response.content)
    else:
        print(f"Failed to download file from {url}. Error {response.status_code}")
        raise RuntimeError()

    sha512 = hashlib.sha512(file_bytes.getvalue()).hexdigest()
    if sha512 == hash:
        with open(path, "wb") as f:
            f.write(file_bytes.getbuffer())

    else:
        raise RuntimeError(f"File: {url} failed hash check")


if __name__ == "__main__":
    t1 = time.time()
    x = init()
    for key in x["files"]:
        _path = key["path"]
        # i am so sorry for the mess below
        target = Path(path.join(instance_folder, _path))
        os.makedirs(target.parent, exist_ok=True)

        download(key["downloads"][0], target, key["hashes"]["sha512"])
        print(f"Downloading: {_path}")
    t2 = time.time()
    print(f"Finished in: {t2-t1}")
