#import pythonCode.py
import json
import flask
from flask import Flask, Response, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS # permitir back receber json do front

import pandas as pd
import tkinter as tk
from tkinter import filedialog as fd

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

@app.route('/loadFileAOI', methods=['GET'])
def loadFileAOI():
    
    locations_df = pd.read_csv(selectNameFile())
    #locations_df = pd.read_csv('F:/LatLongAOI.csv')
    locations_df_json = locations_df.to_json(orient='values')
    resposta = jsonify(locations_df_json)
    resposta.headers.add("Access-Control-Allow-Origin", "*")
    return resposta

@app.route('/selectAIS_File', methods=['GET'])
def selectAIS_File():
     
    resposta = jsonify(selectNameFile())
    #resposta.headers.add("Access-Control-Allow-Origin", "*")
    return resposta

@app.route('/openFileAndFilteAOI', methods=['POST'])
def openFileAndFilterAOI():
    llon = ulon = llat = ulat = 0.0

    if request.method == 'POST':
       
       #ais_df = pd.read_csv('F:/AIS_2020_01_10.csv')
       dados = request.get_json()
       
       ais_df = pd.read_csv(dados[4]); #novo
             
       print("variável do post = ", dados)
       ais_df.dropna(subset=['LAT', 'LON', 'MMSI'], inplace=True) #novo
       
       llat = float(dados[0])
       ulat = float(dados[1])
       llon = float(dados[2])
       ulon = float(dados[3])

       print ("lats e longs = ", llon)
       print ("Tam array ais antes = ",ais_df.shape)
       ######### filtro
       ais_df = ais_df[(ais_df['LON'] > llon)]
       ais_df = ais_df[(ais_df['LON'] < ulon)]
       ais_df = ais_df[(ais_df['LAT'] > llat)]
       ais_df = ais_df[(ais_df['LAT'] < ulat)]

       ais_df = ais_df.sort_values(by=['MMSI', 'BaseDateTime'])#NOVO
       ais_df = ais_df.reset_index(drop=True) # novo
       ais_df['speedBIN']  = ""  #novo
       ais_df['courseBIN'] = ""  #novo
    # novo 12Jan
       vSpeed = 0
       vCourse = 0

       for i in range(0, len(ais_df)):
        #for i in range(0, 10):
        vSpeed  = ais_df["SOG"][i]
        vCourse = ais_df["COG"][i]
        speed, course = geracaoBINs(vSpeed, vCourse)
        ais_df.loc[i,"speedBIN"]  = speed
        ais_df.loc[i,"courseBIN"] = course
        #ais_df["speedBIN"][i]  = speed
        #ais_df["courseBIN"][i] = course
    # fim novo 12 Jan

       print ("Tam array ais depois = ",ais_df.shape)
       print(ais_df.head(10))
       #ais_df_em_json = [x.to_json() for x in ais_df]
       #resposta = jsonify(ais_df_em_json)
       ais_df_json = ais_df.to_json(orient='values')
       resposta = jsonify(ais_df_json)
       resposta.headers.add("Access-Control-Allow-Origin", "*")
       return resposta #("", 204)
    
def selectNameFile():
    root = tk.Tk()
    root.geometry("500x400") # not working
    root.wm_attributes('-topmost', 1)   
    root.lift()     # to work with others OS which are not windows
    root.withdraw()
   
    filepath = fd.askopenfilename(parent=root, title='Select a file', filetypes=[("CSV files", ".csv")])
    print(filepath)
    root.destroy()
 
    return filepath

def geracaoBINs(speed, course):
    speedBIN = ""
    vCourse = ['N','NE', 'NE', 'E','E', 'SE', 'SE', 'S', 'S', 'SW', 'SW', 'W', 'W','NW','NW', 'N']
    index = int(course // 22.5) # each cardinal and colateral point has a segment of 45 degrees (2 x 22.5)
    
    courseBIN = vCourse[index]
    
    if speed   <= 3:
        speedBIN = "0-3"
    elif speed <= 7:
        speedBIN = "3-7"
    elif speed <= 11:
        speedBIN = "7-11"
    elif speed <= 15:
        speedBIN = "11-15"
    elif speed <= 20:
        speedBIN = "15-20"
    else: 
        speedBIN = "20+"

    return speedBIN, courseBIN

if __name__ == "__main__":
    app.run(debug=True)

