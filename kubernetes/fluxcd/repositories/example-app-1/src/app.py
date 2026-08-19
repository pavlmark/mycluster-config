import os
import time
import socket
import shutil
import threading
from pathlib import Path
from datetime import datetime

from flask import (
    Flask,
    request,
    redirect,
    jsonify,
    send_from_directory,
    render_template_string,
)

app = Flask(__name__)

# --------------------------------------------------
# Configuration
# --------------------------------------------------

APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_ENV = os.getenv("APP_ENV", "dev")

DATA_DIR = Path(os.getenv("DATA_DIR", "/data"))
UPLOAD_DIR = DATA_DIR / "uploads"
NOTES_FILE = DATA_DIR / "notes.log"
EVENTS_FILE = DATA_DIR / "events.log"

START_TIME = time.time()

DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log_event(message):
    with EVENTS_FILE.open("a", encoding="utf-8") as f:
        f.write(f"{timestamp()} | {message}\n")


def get_notes():
    if not NOTES_FILE.exists():
        return []

    return NOTES_FILE.read_text(
        encoding="utf-8"
    ).splitlines()


def get_events(limit=20):
    if not EVENTS_FILE.exists():
        return []

    lines = EVENTS_FILE.read_text(
        encoding="utf-8"
    ).splitlines()

    return lines[-limit:]


def storage_info():
    try:
        usage = shutil.disk_usage(DATA_DIR)

        return {
            "available": True,
            "total_gb": round(usage.total / 1024**3, 2),
            "used_gb": round(usage.used / 1024**3, 2),
            "free_gb": round(usage.free / 1024**3, 2),
            "used_percent": round(
                usage.used / usage.total * 100, 1
            ),
        }

    except Exception as exc:
        return {
            "available": False,
            "error": str(exc),
        }


def burn_cpu(seconds):
    log_event(
        f"CPU load test started for {seconds} seconds"
    )

    end_time = time.time() + seconds

    while time.time() < end_time:
        # Some intentionally useless CPU work.
        sum(i * i for i in range(10000))

    log_event("CPU load test finished")


# --------------------------------------------------
# Main dashboard
# --------------------------------------------------

@app.route("/")
def index():
    hostname = socket.gethostname()
    uptime = int(time.time() - START_TIME)

    storage = storage_info()

    files = []

    if UPLOAD_DIR.exists():
        for file in UPLOAD_DIR.iterdir():
            if file.is_file():
                files.append({
                    "name": file.name,
                    "size_kb": round(
                        file.stat().st_size / 1024,
                        2
                    ),
                })

    html = """
<!DOCTYPE html>
<html>
<head>
    <title>Ops Lab Dashboard</title>

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1"
    >

    <style>

        body {
            margin: 0;
            font-family:
                Inter,
                Arial,
                sans-serif;

            background: #111827;
            color: #e5e7eb;
        }

        .container {
            max-width: 1200px;
            margin: auto;
            padding: 30px;
        }

        h1 {
            margin-bottom: 5px;
        }

        .subtitle {
            color: #9ca3af;
            margin-bottom: 30px;
        }

        .grid {
            display: grid;

            grid-template-columns:
                repeat(auto-fit, minmax(240px, 1fr));

            gap: 20px;
        }

        .card {
            background: #1f2937;
            border-radius: 12px;
            padding: 20px;

            box-shadow:
                0 5px 20px
                rgba(0,0,0,.25);
        }

        .card h2 {
            margin-top: 0;
            font-size: 18px;
        }

        .value {
            font-size: 28px;
            font-weight: bold;
        }

        .green {
            color: #34d399;
        }

        .yellow {
            color: #fbbf24;
        }

        .blue {
            color: #60a5fa;
        }

        input,
        textarea {

            width: 100%;
            box-sizing: border-box;

            padding: 10px;

            background: #111827;
            color: white;

            border:
                1px solid #374151;

            border-radius: 6px;

            margin-bottom: 10px;
        }

        button {
            padding: 10px 16px;

            background: #2563eb;
            color: white;

            border: none;
            border-radius: 6px;

            cursor: pointer;
        }

        button:hover {
            background: #1d4ed8;
        }

        .danger {
            background: #dc2626;
        }

        .danger:hover {
            background: #b91c1c;
        }

        .note,
        .event,
        .file {

            background: #111827;

            padding: 10px;
            margin-top: 8px;

            border-radius: 6px;

            word-break: break-word;
        }

        .bar {
            height: 15px;

            background: #374151;

            border-radius: 10px;

            overflow: hidden;
        }

        .bar-value {

            height: 100%;

            background: #3b82f6;
        }

        a {
            color: #60a5fa;
        }

        code {
            color: #34d399;
        }

    </style>
</head>

<body>

<div class="container">

<h1>⚙️ Ops Lab Dashboard</h1>

<div class="subtitle">
Kubernetes • Flask • GitOps • Persistent Storage
</div>


<div class="grid">

    <div class="card">

        <h2>🚀 Application</h2>

        <div class="value green">
            Running
        </div>

        <p>
            Version:
            <b>{{ version }}</b>
        </p>

        <p>
            Environment:
            <b>{{ environment }}</b>
        </p>

    </div>


    <div class="card">

        <h2>☸ Kubernetes Pod</h2>

        <p>
            Hostname:
        </p>

        <code>{{ hostname }}</code>

        <p>
            Uptime:
            <b>{{ uptime }} sec</b>
        </p>

    </div>


    <div class="card">

        <h2>💾 Persistent Storage</h2>

        {% if storage.available %}

        <div class="value blue">
            {{ storage.free_gb }} GB free
        </div>

        <p>
            Used:
            {{ storage.used_percent }}%
        </p>

        <div class="bar">

            <div
                class="bar-value"
                style="
                    width:
                    {{ storage.used_percent }}%
                "
            ></div>

        </div>

        <p>
            Path:
            <code>{{ data_dir }}</code>
        </p>

        {% else %}

        <div class="value yellow">
            Unavailable
        </div>

        {% endif %}

    </div>


    <div class="card">

        <h2>❤️ Health API</h2>

        <p>
            <a href="/health">
                GET /health
            </a>
        </p>

        <p>
            <a href="/ready">
                GET /ready
            </a>
        </p>

        <p>
            <a href="/api/info">
                GET /api/info
            </a>
        </p>

    </div>

</div>


<br>


<div class="grid">

<div class="card">

<h2>📝 Persistent Notes</h2>

<form method="POST" action="/notes">

<textarea
    name="note"
    placeholder="Write a persistent note..."
></textarea>

<button type="submit">
    Save note
</button>

</form>


{% for note in notes|reverse %}

<div class="note">
    {{ note }}
</div>

{% else %}

<p>No notes yet.</p>

{% endfor %}

</div>


<div class="card">

<h2>📁 NFS File Upload</h2>

<form
    method="POST"
    action="/upload"
    enctype="multipart/form-data"
>

<input
    type="file"
    name="file"
>

<button type="submit">
    Upload to persistent storage
</button>

</form>


{% for file in files %}

<div class="file">

<a href="/uploads/{{ file.name }}">
    {{ file.name }}
</a>

<br>

{{ file.size_kb }} KB

</div>

{% else %}

<p>No uploaded files.</p>

{% endfor %}

</div>


<div class="card">

<h2>🔥 Alert Testing</h2>

<p>
Generate temporary CPU load.
Later you can use this for
Prometheus/Grafana alert testing.
</p>

<form
    method="POST"
    action="/cpu-load"
>

<select name="seconds">

<option value="5">
5 seconds
</option>

<option value="10">
10 seconds
</option>

<option value="20">
20 seconds
</option>

</select>

<br><br>

<button
    class="danger"
    type="submit"
>
🔥 Generate CPU Load
</button>

</form>

</div>

</div>


<br>


<div class="card">

<h2>📜 Event Log</h2>

{% for event in events|reverse %}

<div class="event">
    {{ event }}
</div>

{% else %}

<p>No events yet.</p>

{% endfor %}

</div>


</div>

</body>
</html>
"""

    return render_template_string(
        html,

        hostname=hostname,
        uptime=uptime,

        environment=APP_ENV,
        version=APP_VERSION,

        storage=storage,
        data_dir=DATA_DIR,

        notes=get_notes(),
        events=get_events(),

        files=files,
    )


# --------------------------------------------------
# Notes
# --------------------------------------------------

@app.route("/notes", methods=["POST"])
def add_note():

    note = request.form.get(
        "note",
        ""
    ).strip()

    if note:

        with NOTES_FILE.open(
            "a",
            encoding="utf-8"
        ) as f:

            f.write(
                f"{timestamp()} | {note}\n"
            )

        log_event(
            "Persistent note created"
        )

    return redirect("/")


# --------------------------------------------------
# Uploads
# --------------------------------------------------

@app.route("/upload", methods=["POST"])
def upload():

    uploaded_file = request.files.get("file")

    if (
        uploaded_file
        and uploaded_file.filename
    ):

        destination = (
            UPLOAD_DIR
            / Path(uploaded_file.filename).name
        )

        uploaded_file.save(destination)

        log_event(
            f"File uploaded: "
            f"{destination.name}"
        )

    return redirect("/")


@app.route("/uploads/<filename>")
def uploaded_file(filename):

    return send_from_directory(
        UPLOAD_DIR,
        filename
    )


# --------------------------------------------------
# Load testing
# --------------------------------------------------

@app.route("/cpu-load", methods=["POST"])
def cpu_load():

    seconds = int(
        request.form.get(
            "seconds",
            5
        )
    )

    # Don't allow accidental endless load.
    seconds = min(
        max(seconds, 1),
        30
    )

    thread = threading.Thread(
        target=burn_cpu,
        args=(seconds,),
        daemon=True,
    )

    thread.start()

    return redirect("/")


# --------------------------------------------------
# Health endpoints
# --------------------------------------------------

@app.route("/health")
def health():

    return jsonify({
        "status": "ok",
        "pod": socket.gethostname(),
        "version": APP_VERSION,
        "environment": APP_ENV,
    })


@app.route("/ready")
def ready():

    storage = storage_info()

    if not storage["available"]:

        return jsonify({
            "status": "not ready",
            "storage": False,
        }), 503

    return jsonify({
        "status": "ready",
        "storage": True,
    })


# --------------------------------------------------
# API
# --------------------------------------------------

@app.route("/api/info")
def api_info():

    storage = storage_info()

    return jsonify({

        "application": {
            "name": "ops-lab",
            "version": APP_VERSION,
            "environment": APP_ENV,
        },

        "kubernetes": {
            "pod": socket.gethostname(),
        },

        "storage": storage,

        "uptime_seconds":
            int(time.time() - START_TIME),

    })


if __name__ == "__main__":

    log_event(
        f"Application started "
        f"version={APP_VERSION}"
    )

    app.run(
        host="0.0.0.0",
        port=5000
    )
