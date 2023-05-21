import hashlib
import json
import os
import queue
import sys
import time
import requests
import io
import threading

from os import path
from pathlib import Path


# dev constants
instance_folder = Path("./instance/")


def init():
    with open("modrinth.index.json") as jsonfile:
        x = json.load(jsonfile)
    return x


def download():
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

    while True:
        args = url_queue.get()
        print(f"Downloading: {args[0]}")
        os.makedirs(args[0].parent, exist_ok=True)

        response = requests.get(args[1])
        # Check if the request was successful
        if response.status_code == 200:
            file_bytes = io.BytesIO(response.content)
        else:
            print(
                f"Failed to download file from {args[1]}. Error {response.status_code}"
            )
            raise RuntimeError()

        sha512 = hashlib.sha512(file_bytes.getvalue()).hexdigest()
        if sha512 == args[2]:
            with open(args[0], "wb") as f:
                f.write(file_bytes.getbuffer())
        else:
            raise RuntimeError(f"File: {args[1]} failed hash check")

        url_queue.task_done()


if __name__ == "__main__":
    t1 = time.time()

    url_queue = queue.Queue()
    x = init()
    for key in x["files"]:
        _path = key["path"]
        # i am so sorry for the mess below
        target = Path(path.join(instance_folder, _path))
        url_queue.put((target, key["downloads"][0], key["hashes"]["sha512"]))

    # 5 is the most threads we'll spawn.
    max_concurr = 5 if 5 <= url_queue._qsiz() else url_queue._qsiz()
    threads = []
    for i in range(max_concurr):
        t = threading.Thread(target=download)
        threads.append(t)
        t.start()

    url_queue.join()
    t2 = time.time()
    print(f"Finished in: {t2-t1}")
    sys.exit()
