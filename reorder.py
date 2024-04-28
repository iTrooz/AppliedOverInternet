import os
import json
import sys
from shutil import copyfile


if len(sys.argv) != 2:
    print(f"Syntax: {sys.argv[0]} <minecraft folder>")
    sys.exit(1)

INPUT_DIR = sys.argv[1]
OUTPUT_DIR = "textures"

with open(os.path.join(INPUT_DIR, "icon-exports-metadata.json"), "r") as f:
    metadata = json.loads(f.read())["meta"]

EXPORT_DIR_NAME = "icon-exports-x32" # TODO is it always that name ?

for item_meta in metadata:
    path = os.path.join(INPUT_DIR, EXPORT_DIR_NAME, item_meta["image_file"])
    if os.path.isfile(path):
        namespace, name = item_meta["id"].split(":")
        os.makedirs(os.path.join(OUTPUT_DIR, namespace), exist_ok=True)
        copyfile(path, os.path.join(OUTPUT_DIR, namespace, name+".png"))
