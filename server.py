from influxdb_client import Point, InfluxDBClient, WriteApi
import traceback
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timezone

from flask import *

app = Flask(__name__)

# https://stackoverflow.com/a/37331139
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 60*60*24*30 # 30 days

DATA = None
LAST_UPDATE = None

def toHuman(num):
    # Inspiration: https://stackoverflow.com/a/1094933
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1000.0:
            return ("%.2f" % num).rstrip('0').rstrip('.') + unit
        num /= 1000.0
    return ("%.2f" % num).rstrip('0').rstrip('.') + "Y"

def initDBClient() -> InfluxDBClient:
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

def sendDBStats(write_api: WriteApi, data):
    write_api.write("test", "test", [
        Point("ae2_item").tag("name", item["name"]).field("amount", item["amount"])
        for item in data["items"]])
    
    usage_points = []
    for usage_cat, usage_cat_data in data["usage"].items():
        usage_points.append(Point("ae2_usage").tag("category", usage_cat).field("total", usage_cat_data["total"]).field("used", usage_cat_data["used"]))

    write_api.write("test", "test", usage_points)


def process_ae2_json(data):
    items = data["items"]
    # sort items
    items = sorted(items, key=lambda x: int(x["amount"]), reverse=True)
    # set human amount
    for item in items:
        item["humanAmount"] = toHuman(int(item["amount"]))
    data["items"] = items
    
    if db_client:
        sendDBStats(db_client_write_api, data)

    global DATA, LAST_UPDATE
    DATA = data
    LAST_UPDATE = datetime.now(timezone.utc)

db_client = None
db_client_write_api = None
try:
    db_client = initDBClient()
    db_client_write_api = db_client.write_api()
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

# UI accessed by users
@app.route('/')
def index():
    items = DATA["items"] if DATA else None
    last_update = LAST_UPDATE.astimezone().strftime("%Y/%m/%d %X UTC%z %Z") if LAST_UPDATE else None
    return render_template("index.html", items=items, last_update=last_update)

# For debugging purposes
@app.route('/ae2', methods=["GET"])
def ae2_get():
    return jsonify(DATA["items"])

# Used by the CC:Tweaked script
@app.route('/ae2', methods=["POST"])
def ae2_post():
    if request.headers.getlist("X-Forwarded-For"): # if this is set, it comes from nginx
        return 'This endpoint is only availabl to the loca machine itself', 403

    process_ae2_json(request.json)
    return '', 200

if __name__ == '__main__':
    print("Starting web server")
    app.run(host='0.0.0.0')
