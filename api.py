from flask import Flask
from fondinfo import Fondinfo

info = Fondinfo()
app = Flask(__name__)
earnings = None

@app.route("/")
def index():
    if earnings = None