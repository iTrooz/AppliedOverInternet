import os
import json

from flask import *

app = Flask(__name__)

ITEMS = {"minecraft:dirt": 0, "minecraft:stone": 0}

def toHuman(num):
    # Inspiration: https://stackoverflow.com/a/1094933
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1000.0:
            return "%3.1f%s" % (num, unit)
        num /= 1000.0
    return "%.1f%s" % (num, 'Y')

@app.route('/textures/<name>')
def textures(name):
    name = name.removeprefix("minecraft:")
    print(f"Looking for texture for '{name}'")
    for folder in ("item", "block"):
        folder = os.path.join("minecraft-assets/assets/minecraft/textures", folder)
        try_file = os.path.join(folder, name+".png")
        if os.path.isfile(try_file):
            return send_file(try_file)
    
    print(f"Could not find texture for '{name}'")
    return send_file("missing.png"), 404

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
