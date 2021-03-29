"""Super short utility script to keep only the files from node_modules
that are used by the app.
"""

import re
import subprocess

import os

if __name__ == "__main__":
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

    tree = os.walk("node_modules")

    for dirpath, dirname, filename in tree:
        for f in filename:
            full_path = os.path.join(dirpath, f)

            if full_path not in matches:
                os.remove(full_path)
            
        




