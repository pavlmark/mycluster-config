import os
import socket

from flask import Flask, jsonify

app = Flask(__name__)

APP_VERSION = os.getenv("APP_VERSION", "dev")
ENVIRONMENT = os.getenv("ENVIRONMENT", "local")


@app.route("/")
def home():
    return f"""
    <html>
        <head>
            <title>Pavlmark Platform, web page created by AI</title>
        </head>
        <body>
            <h1>Pavlmark DevOps/SRE Platform</h1>

            <p>This application is running inside Kubernetes.</p>

            <h2>Application information</h2>

            <ul>
                <li>Version: {APP_VERSION}</li>
                <li>Environment: {ENVIRONMENT}</li>
                <li>Pod: {socket.gethostname()}</li>
            </ul>

            <h2>Platform</h2>

            <ul>
                <li>Kubernetes</li>
                <li>Cilium</li>
                <li>Flux CD</li>
                <li>Traefik</li>
                <li>Prometheus</li>
                <li>Grafana</li>
            </ul>
        </body>
    </html>
    """


@app.route("/health")
def health():
    return jsonify(status="healthy"), 200


@app.route("/ready")
def ready():
    return jsonify(status="ready"), 200


@app.route("/version")
def version():
    return jsonify(
        version=APP_VERSION,
        environment=ENVIRONMENT,
        pod=socket.gethostname(),
    ), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
