#import pythonCode.py
import json
import flask
from flask import Flask, render_template, request, redirect, url_for, flash

import pandas as pd

def teste():
    print ("teste do python")

app = Flask(__name__)

@app.route('/') 
def homepage():

    return render_template("mapaW3-v6-Alt4.html")

@app.route('/create_file', methods=['POST'])
def create_file():
    if request.method == 'POST':
        #print (request.form)
        with open(f"{request.form.get('name')}.txt", "w") as f:
            f.write('FILE CREATED AND SUCCESSFULL POST REQUEST!')
        return ('', 204)

@app.route('/openFileAndFilteAOI', methods=['POST'])
def openFileAndFilterAOI():
    llon = ulon = llat = ulat = 0.0

    if request.method == 'POST':
       ais_df = pd.read_csv('F:/AIS_2020_01_10.csv')
       llon = float(request.form.get('llon', type=float))
       ulon = float(request.form.get('ulon', type=float))
       llat = float(request.form.get('llat', type=float))
       ulat = float(request.form.get('ulat', type=float))
       print ("lats e longs = ", llon)
       print ("Tam array ais antes = ",ais_df.shape)
       ######### filtro
       ais_df = ais_df[(ais_df['LON'] > llon)]
       ais_df = ais_df[(ais_df['LON'] < ulon)]
       ais_df = ais_df[(ais_df['LAT'] > llat)]
       ais_df = ais_df[(ais_df['LAT'] < ulat)]
       print ("Tam array ais depois = ",ais_df.shape)
       print(ais_df.head(3))
       return (str(ulat), 204)
    


if __name__ == "__main__":
    app.run(debug=True)

