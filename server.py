import os

from flask import *

app = Flask(__name__)

ITEMS = {"minecraft:dirt": 0, "minecraft:stone": 0}

@app.route('/textures/<name>')
def textures(name):
    print(name)
    for folder in ("item", "block"):
        folder = os.path.join("minecraft-assets/assets/minecraft/textures", folder)
        try_file = os.path.join(folder, name+".png")
        print(try_file)
        if os.path.isfile(try_file):
            print("ok")
            return send_file(try_file)
    
    print(f"Could not find texture for '{name}'")
    return send_file("missing.png"), 404

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/ae2', methods=["GET"])
def ae2_get():
    return ITEMS

@app.route('/ae2', methods=["POST"])
def ae2_post():
    global ITEMS
    ITEMS = request.json
    return '', 200

if __name__ == '__main__':
    app.run()
