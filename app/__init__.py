from flask import Flask, render_template
from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)


@app.route("/")
def main():
    return f"<h1>Package Tracker</h1>"

@app.route("/new_package", methods=["GET", "POST"])
def new_package():
    return render_template('shipping_request.html')