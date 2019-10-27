from flask import Flask
from fondinfo import Fondinfo

info = Fondinfo()
info.add_fund("Storebrand Indeks - Alle Markeder", 8.054933, 20000,
              "https://bors.e24.no/#!/instrument/SP-IDXAM.OSE")
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
    app.run(debug=True)
