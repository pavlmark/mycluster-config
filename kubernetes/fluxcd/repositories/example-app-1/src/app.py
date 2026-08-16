from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "This page is pavlmark study project for practice DevOps/GitOps/SRE !"

