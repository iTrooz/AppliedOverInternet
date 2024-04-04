from influxdb_client import Point, InfluxDBClient
import traceback
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

def initDBClient():
    from dotenv import load_dotenv
    load_dotenv()

    if not os.getenv("DB_HOST"):
        raise Exception("DB_HOST not set in .env")
    
    db_client = InfluxDBClient(
        url=os.getenv("DB_HOST"),
        token=os.getenv("DB_TOKEN"),
        org="test")
    if not db_client.ping():
        raise Exception("Connection failed for unknown reason")
    return db_client

def sendDBStats(db_client: InfluxDBClient, data):
    write_api = db_client.write_api()

    write_api.write("test", "test", [
        Point("ae2_item").tag("name", item["name"]).field("amount", item["amount"])
        for item in data])


def process_ae2_json(data):
    global ITEMS

    # sort items
    data = sorted(data, key=lambda x: int(x["amount"]), reverse=True)

    # set human amount
    for item in data:
        item["humanAmount"] = toHuman(int(item["amount"]))
    
    if db_client:
        sendDBStats(db_client, data)

    ITEMS = data

db_client = None
try:
    db_client = initDBClient()
    print("DB client connnected successfully")
except Exception as e:
    print(f"Failed to init DB client:")
    print(traceback.format_exc())
    print("data will not be sent to DB, you will not be able to use Grafana")

if app.debug:
    with open("example_data.json", "r") as file:
        process_ae2_json(json.loads(file.read()))

@app.route('/textures/<fullname>')
def textures(fullname):
    namespace, name = fullname.split(":")
    texture_file = os.path.join("textures", namespace, name+".png")
    if os.path.isfile(texture_file):
        return send_file(texture_file)

    print(f"Could not find texture for '{fullname}' ({texture_file} not found)")
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

    process_ae2_json(data)

    return '', 200

if __name__ == '__main__':
    print("Starting web server")
    app.run(host='0.0.0.0')
