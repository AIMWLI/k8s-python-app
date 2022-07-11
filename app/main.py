from flask import Flask, jsonify, request
from app.config import Config
from app.cache import TTLCache

app = Flask(__name__)
cfg = Config()
cache = TTLCache(ttl=30)


@app.route("/")
def hello():
    return "Hello from Python!"


@app.route("/health")
def health():
    return jsonify({"status": "ok", "host": cfg.HOST, "port": cfg.PORT})


@app.route("/echo", methods=["POST"])
def echo():
    data = request.get_json(force=True)
    return jsonify({"echo": data})


@app.route("/config")
def get_config():
    return jsonify({"debug": cfg.DEBUG, "host": cfg.HOST, "port": cfg.PORT})


if __name__ == "__main__":
    app.run(host=cfg.HOST, port=cfg.PORT)
