#import pythonCode.py
#import json
import flask
from flask import Flask, render_template

import pandas as pd

app = Flask(__name__)

@app.route("/") 
def homepage():
    valor = [[32.52188,-80.11495],[32.36890,-80.29070],[32.11337,-80.49666],[32.27142, -80.20832]]
    return render_template("mapaW3-v6-Alt4.html", valor = valor)
    #return render_template("mapaW3-v6-Alt4.html")

#@app.route("/carregaArq")
#def carregaArq():
    
#    return render_template("mapaW3-v6-Alt5.html")


if __name__ == "__main__":
    app.run(debug=True)

