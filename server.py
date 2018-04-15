import lights
from flask import Flask, request
app = Flask(__name__)

@app.route("/")
def handler():
    channel = request.args.get('channel', type=int)
    level   = request.args.get('level', type=float)
    rate    = request.args.get('rate', type=float)
    lights.set(
            channel=channel,
            level=level,
            rate=rate)
    return "Done"
