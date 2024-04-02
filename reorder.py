import os
from shutil import copyfile

INPUT_DIR = "input"
OUTPUT_DIR = "output"

for in_file in os.listdir("input"):
    i = in_file.find("__{")
    if i == -1:
        out_path = in_file
    else:
        _, ext = os.path.splitext(in_file)
        out_path = in_file[:i] + ext
    
    i = in_file.find("__")
    out_path = out_path[:i] + "/" + out_path[i+2:]

    out_path = os.path.join(OUTPUT_DIR, out_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    copyfile(os.path.join(INPUT_DIR, in_file), out_path)