"""Super short utility script to keep only the files from node_modules
that are used by the app.
"""

import re
import subprocess

import os
import shutil

if __name__ == "__main__":

    # manual addition of files which are needed but not picked up by the regex below.
    needed_but_unlisted = [
        os.path.join(
            "node_modules", "jstree", "dist", "themes", "default", "throbber.gif"
        ),
        os.path.join("node_modules", "jstree", "dist", "themes", "default", "32px.png"),
    ]

    full_path = os.path.abspath(os.path.join("..", "templates/"))

    bashCommand = f"grep -r {full_path} -e node_modules"

    with open("files.out", "w+") as f:
        process = subprocess.Popen(bashCommand.split(), stdout=f)
        output, error = process.communicate()

    with open("files.out", "r") as f:
        data = f.read()

    # Use regex to get files that are used in templates.
    pattern = re.compile("(node_modules/.+(?:css|js))")

    matches = pattern.findall(data)

    matches = list(set(matches))

    matches.extend(needed_but_unlisted)

    # assert False, matches

    tree = os.walk("node_modules")

    for dirpath, dirname, filename in tree:
        for f in filename:
            full_path = os.path.join(dirpath, f)

            if full_path not in matches:
                os.remove(full_path)

    # Second pass to delete empty folders
    tree = os.walk("node_modules", topdown=False)
    for dirpath, dirname, filename in tree:
        for name in dirname:
            folder_path = os.path.join(dirpath, name)

            if not os.listdir(folder_path):
                shutil.rmtree(folder_path)

    os.remove("files.out")
