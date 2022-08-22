from flask import Flask, jsonify, request
from app.config import Config

app = Flask(__name__)
cfg = Config()


@app.route("/")
def hello():
    return "Hello from Python!"


@app.route("/health")
def health():
    return jsonify({"status": "ok", "host": cfg.HOST})


if __name__ == "__main__":
    app.run(host=cfg.HOST, port=cfg.PORT)
