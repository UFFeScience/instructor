import json

import flask
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/") 
def homepage():
    return render_template("mapaW3-v6-Alt4.html")

if __name__ == "__main__":
    app.run(debug=True)

    #servidor do heroku
    