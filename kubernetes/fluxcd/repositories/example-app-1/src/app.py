from flask import Flask, request, redirect, render_template_string
from pathlib import Path
from datetime import datetime
import socket

app = Flask(__name__)

DATA_DIR = Path("/data")
NOTES_FILE = DATA_DIR / "notes.log"

DATA_DIR.mkdir(parents=True, exist_ok=True)


@app.route("/")
def index():
    hostname = socket.gethostname()

    if NOTES_FILE.exists():
        notes = NOTES_FILE.read_text().splitlines()
    else:
        notes = []

    html = """
    <!doctype html>
    <html>
    <head>
        <title>Pavel Kubernetes Lab</title>
        <style>
            body {
                font-family: Arial;
                max-width: 900px;
                margin: 40px auto;
            }

            textarea {
                width: 100%;
                height: 100px;
            }

            .note {
                background: #f3f3f3;
                padding: 10px;
                margin: 8px 0;
            }

            .info {
                background: #eef;
                padding: 10px;
                margin-bottom: 20px;
            }
        </style>
    </head>

    <body>

        <h1>Kubernetes Lab</h1>

        <div class="info">
            <b>Pod:</b> {{ hostname }}<br>
            <b>Persistent storage:</b> /data<br>
            <b>Notes stored:</b> {{ notes|length }}
        </div>

        <h2>Add note</h2>

        <form method="POST" action="/note">
            <textarea name="note"
                      placeholder="Write something..."></textarea>
            <br>
            <button type="submit">Save to NFS</button>
        </form>

        <h2>Persistent notes</h2>

        {% for note in notes|reverse %}
            <div class="note">{{ note }}</div>
        {% else %}
            <p>No notes yet.</p>
        {% endfor %}

    </body>
    </html>
    """

    return render_template_string(
        html,
        hostname=hostname,
        notes=notes
    )


@app.route("/note", methods=["POST"])
def add_note():
    note = request.form.get("note", "").strip()

    if note:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with NOTES_FILE.open("a") as f:
            f.write(f"{timestamp} | {note}\n")

    return redirect("/")


@app.route("/health")
def health():
    return {
        "status": "ok",
        "pod": socket.gethostname(),
        "storage": str(DATA_DIR),
        "storage_available": DATA_DIR.exists()
    }, 200


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
