import os
import zipfile
import re

for filename in os.listdir('mods_jars'):
    print(f"Processing {filename}")
    z = zipfile.ZipFile(os.path.join("mods_jars", filename))

    for info in z.infolist():
        # Ignore folders
        if info.filename[-1] == "/":
            continue

        # Verify this is an asset we want
        match = re.match("^assets/([^/]*)/textures/(block|item)/", info.filename)
        if not match:
            continue
        namespace, category = match.groups()
    
        # rewrite filename because we don't want the original structure
        orig_filename = info.filename
        info.filename = info.filename.removeprefix(f"assets/{namespace}/textures/{category}/")

        # extract it
        z.extract(info, path=os.path.join("mods_textures", filename.removesuffix(".jar"), namespace, category))
