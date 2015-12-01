from flask import Flask, request
app = Flask("eveapiproxy")


@app.route("/")
def index():
    return ""

__all__ = [
    'app',
    'request',
]
