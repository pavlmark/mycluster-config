from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello Pavl! v1.0.0.4"
