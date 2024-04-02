import os
import json
from pathlib import Path

from flask import *

app = Flask(__name__)

# https://stackoverflow.com/a/37331139
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 60*60*24*30 # 30 days

ITEMS = {"minecraft:dirt": 0, "minecraft:stone": 0}

def toHuman(num):
    # Inspiration: https://stackoverflow.com/a/1094933
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1000.0:
            return ("%.2f" % num).rstrip('0').rstrip('.') + unit
        num /= 1000.0
    return ("%.2f" % num).rstrip('0').rstrip('.') + "Y"

@app.route('/textures/<name>')
def textures(name):
    namespace, name = name.split(":")
    if namespace == "minecraft":
        for folder in ("item", "block"):
            folder = os.path.join("minecraft-assets/assets/minecraft/textures", folder)
            try_file = os.path.join(folder, name+".png")
            if os.path.isfile(try_file):
                return send_file(try_file)
    else:
        # Loop all mods
        for mod in os.listdir("mods_textures"):
            path = os.path.join("mods_textures", mod, namespace)
            if not os.path.isdir(path): # Ensure good namespace
                continue
            
            for filepath in Path(path).rglob("*.png"): # Loop recursively because sometimes mods have sub-folders
                if os.path.basename(filepath) == name+".png": # check for good name
                    return send_file(filepath, cache_timeout=0)


    
    print(f"Could not find texture for '{name}'")
    return send_file("missing.png"), 202

@app.route('/')
def index():
    return render_template("index.html", items=ITEMS)

@app.route('/ae2', methods=["GET"])
def ae2_get():
    return jsonify(ITEMS)

@app.route('/', methods=["POST"]) # temporary until I fix the ComputerCraft code
@app.route('/ae2', methods=["POST"])
def ae2_post():
    global ITEMS

    # BEGIN HACK
    # TODO fix content type in ComputerCraft code ?
    data = request.form.to_dict() # transform to dict
    data = next(iter(data)) # get first key
    data = json.loads(data) # parse JSON
    # END HACK

    # sort items
    data = sorted(data, key=lambda x: int(x["value"]), reverse=True) # TODO: fix ComputerCraft code to say "amount" instead of "value"

    # set human amount
    for item in data:
        item["humanAmount"] = toHuman(int(item["value"]))

    ITEMS = data
    return '', 200

if __name__ == '__main__':
    app.run()
