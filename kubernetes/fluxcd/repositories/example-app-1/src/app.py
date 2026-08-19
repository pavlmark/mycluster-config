import os
import time
import socket
import shutil
import threading
from pathlib import Path
from datetime import datetime
from functools import wraps

from flask import (
    Flask,
    request,
    redirect,
    jsonify,
    render_template_string,
    Response,
)

app = Flask(__name__)


# --------------------------------------------------
# Configuration from environment variables
# --------------------------------------------------

APP_VERSION = os.getenv("APP_VERSION", "unknown")
APP_ENV = os.getenv("APP_ENV", "dev")

DATA_DIR = Path(os.getenv("DATA_DIR", "/data"))

ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

NOTES_FILE = DATA_DIR / "notes.log"
EVENTS_FILE = DATA_DIR / "events.log"

START_TIME = time.time()

DATA_DIR.mkdir(parents=True, exist_ok=True)


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
                usage.used / usage.total * 100,
                1
            ),
        }

    except Exception as exc:
        return {
            "available": False,
            "error": str(exc),
        }


# --------------------------------------------------
# Simple authentication for /admin
# --------------------------------------------------

def check_auth(username, password):
    return (
        username == ADMIN_USER
        and password == ADMIN_PASSWORD
        and ADMIN_PASSWORD != ""
    )


def authenticate():
    return Response(
        "Authentication required",
        401,
        {
            "WWW-Authenticate":
                'Basic realm="Ops Lab Admin"'
        }
    )


def admin_required(function):
    @wraps(function)
    def decorated(*args, **kwargs):
        auth = request.authorization

        if not auth:
            return authenticate()

        if not check_auth(
            auth.username,
            auth.password
        ):
            return authenticate()

        return function(*args, **kwargs)

    return decorated


# --------------------------------------------------
# CPU load generator
# --------------------------------------------------

def burn_cpu(seconds):
    log_event(
        f"CPU load started for {seconds} seconds"
    )

    end_time = time.time() + seconds

    while time.time() < end_time:
        sum(i * i for i in range(20000))

    log_event("CPU load finished")


# --------------------------------------------------
# Public dashboard
# --------------------------------------------------

@app.route("/")
def index():

    hostname = socket.gethostname()
    uptime = int(time.time() - START_TIME)
    storage = storage_info()

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
    font-family: Arial, sans-serif;
    background: #111827;
    color: #e5e7eb;
}

.container {
    max-width: 1100px;
    margin: auto;
    padding: 30px;
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
    margin-bottom: 20px;
}

.green {
    color: #34d399;
}

.blue {
    color: #60a5fa;
}

.value {
    font-size: 25px;
    font-weight: bold;
}

.bar {
    height: 15px;
    background: #374151;
    border-radius: 8px;
    overflow: hidden;
}

.bar-value {
    height: 100%;
    background: #3b82f6;
}

code {
    color: #34d399;
}

a {
    color: #60a5fa;
}

</style>

</head>


<body>

<div class="container">

<h1>⚙️ Ops Lab Dashboard</h1>

<p>
Kubernetes • Flask • GitOps • Persistent Storage
</p>


<div class="grid">


<div class="card">

<h2>🚀 Application</h2>

<div class="value green">
Running
</div>

<p>
Version:
<code>{{ version }}</code>
</p>

<p>
Environment:
<code>{{ environment }}</code>
</p>

</div>


<div class="card">

<h2>☸ Kubernetes</h2>

<p>Current Pod:</p>

<code>{{ hostname }}</code>

<p>
Uptime:
{{ uptime }} seconds
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
    style="width: {{ storage.used_percent }}%">
</div>

</div>

<p>
Mounted at:
<code>{{ data_dir }}</code>
</p>

{% else %}

<p>Storage unavailable</p>

{% endif %}

</div>


<div class="card">

<h2>❤️ Health</h2>

<p>
<a href="/health">GET /health</a>
</p>

<p>
<a href="/ready">GET /ready</a>
</p>

<p>
<a href="/api/info">GET /api/info</a>
</p>

<p>
<a href="/admin">Admin Lab</a>
</p>

</div>


</div>


<div class="card">

<h2>📝 Persistent Notes</h2>

{% for note in notes|reverse %}

<p>
{{ note }}
</p>

{% else %}

<p>No notes yet.</p>

{% endfor %}

</div>


<div class="card">

<h2>📜 Event Log</h2>

{% for event in events|reverse %}

<p>
{{ event }}
</p>

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
    )


# --------------------------------------------------
# Admin dashboard
# --------------------------------------------------

@app.route("/admin")
@admin_required
def admin():

    html = """
<!DOCTYPE html>

<html>

<head>

<title>Ops Lab Admin</title>

<style>

body {
    font-family: Arial;
    background: #111827;
    color: white;
    max-width: 900px;
    margin: 40px auto;
}

.card {
    background: #1f2937;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
}

button {
    padding: 10px 16px;
    border: 0;
    border-radius: 5px;
    cursor: pointer;
}

.danger {
    background: #dc2626;
    color: white;
}

.warning {
    background: #d97706;
    color: white;
}

.normal {
    background: #2563eb;
    color: white;
}

textarea {
    width: 100%;
    height: 80px;
}

</style>

</head>


<body>

<h1>🧪 Incident Simulator</h1>


<div class="card">

<h2>🔥 CPU Load</h2>

<p>
Generate CPU load inside this Pod.
</p>

<form method="POST" action="/admin/cpu">

<select name="seconds">

<option value="10">10 seconds</option>
<option value="30">30 seconds</option>
<option value="45">45 seconds</option>

</select>

<button class="danger">
Generate CPU Load
</button>

</form>

</div>


<div class="card">

<h2>🐌 Slow Request</h2>

<form method="POST" action="/admin/slow">

<select name="seconds">

<option value="1">1 second</option>
<option value="3">3 seconds</option>
<option value="5">5 seconds</option>

</select>

<button class="warning">
Generate slow request
</button>

</form>

</div>


<div class="card">

<h2>💥 HTTP Error</h2>

<form method="POST" action="/admin/error">

<button class="danger">

Generate HTTP 500

</button>

</form>

</div>


<div class="card">

<h2>📝 Persistent Note</h2>

<form method="POST" action="/admin/note">

<textarea
    name="note"
    maxlength="500"
    placeholder="Write something to NFS..."
></textarea>

<br><br>

<button class="normal">

Save to NFS

</button>

</form>

</div>


<p>
<a href="/">
Back to dashboard
</a>
</p>

</body>
</html>
"""

    return render_template_string(html)


# --------------------------------------------------
# Admin actions
# --------------------------------------------------

@app.route("/admin/cpu", methods=["POST"])
@admin_required
def admin_cpu():

    seconds = int(
        request.form.get(
            "seconds",
            5
        )
    )

    seconds = max(
        1,
        min(seconds, 15)
    )

    thread = threading.Thread(
        target=burn_cpu,
        args=(seconds,),
        daemon=True,
    )

    thread.start()

    return redirect("/admin")


@app.route("/admin/slow", methods=["POST"])
@admin_required
def admin_slow():

    seconds = int(
        request.form.get(
            "seconds",
            1
        )
    )

    seconds = max(
        1,
        min(seconds, 5)
    )

    log_event(
        f"Slow request generated: {seconds}s"
    )

    time.sleep(seconds)

    return redirect("/admin")


@app.route("/admin/error", methods=["POST"])
@admin_required
def admin_error():

    log_event(
        "HTTP 500 test generated"
    )

    return jsonify({
        "error": "Intentional test error"
    }), 500


@app.route("/admin/note", methods=["POST"])
@admin_required
def admin_note():

    note = request.form.get(
        "note",
        ""
    ).strip()

    # Server-side limit too.
    note = note[:500]

    if note:

        with NOTES_FILE.open(
            "a",
            encoding="utf-8"
        ) as file:

            file.write(
                f"{timestamp()} | {note}\n"
            )

        log_event(
            "Persistent note created"
        )

    return redirect("/admin")


# --------------------------------------------------
# Health endpoints
# --------------------------------------------------

@app.route("/health")
def health():

    return jsonify({
        "status": "ok",
        "pod": socket.gethostname(),
        "version": APP_VERSION,
    })


@app.route("/ready")
def ready():

    storage = storage_info()

    if not storage["available"]:

        return jsonify({
            "status": "not-ready",
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

    return jsonify({

        "application": {
            "version": APP_VERSION,
            "environment": APP_ENV,
        },

        "kubernetes": {
            "pod": socket.gethostname(),
        },

        "storage":
            storage_info(),

        "uptime_seconds":
            int(time.time() - START_TIME),

    })


# --------------------------------------------------

if __name__ == "__main__":

    log_event(
        f"Application started "
        f"version={APP_VERSION}"
    )

    app.run(
        host="0.0.0.0",
        port=5000
    )
