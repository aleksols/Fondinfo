from flask import Flask
from fondinfo import Fondinfo

info = Fondinfo()
app = Flask(__name__)
earnings = None


@app.route("/")
def index():
    global earnings
    global info
    if earnings is None:
        earnings = info.calculate_total_earning()
    return str(earnings)


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
