#import pythonCode.py
import json
import flask
from flask import Flask, Response, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS, cross_origin # permitir back receber json do front

import pandas as pd
import tkinter as tk
from tkinter import filedialog as fd

#locations_dfBuffer = ""

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
    
    global locations_dfBuffer
    locations_df = pd.read_csv(selectNameFile())
    #locations_df = pd.read_csv('F:/LatLongAOI.csv')
    locations_dfBuffer = locations_df.copy() # novo 05fev
    locations_df_json = locations_df.to_json(orient='values')
    resposta = jsonify(locations_df_json)
    resposta.headers.add("Access-Control-Allow-Origin", "*")
    return resposta

@app.route('/selectAIS_File', methods=['GET'])
def selectAIS_File():
     
    resposta = jsonify(selectNameFile())
    resposta.headers.add("Access-Control-Allow-Origin", "*")
    return resposta

@app.route('/selectDatasetFile', methods=['GET'])
def selectDatasetFile():
     
    resposta = jsonify(selectNameFile())
    resposta.headers.add("Access-Control-Allow-Origin", "*")
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

       #print ("lats e longs = ", llon)
       print ("Tam array ais antes exclusao fora do Grid = ",ais_df.shape)
       ######### filtro
       ais_df = ais_df[(ais_df['LON'] > llon)]
       ais_df = ais_df[(ais_df['LON'] < ulon)]
       ais_df = ais_df[(ais_df['LAT'] > llat)]
       ais_df = ais_df[(ais_df['LAT'] < ulat)]

       print ("Tam array ais depois exclusao fora do Grid = ",ais_df.shape)

       #### NOVO 05fev #####################################
       ais_df['insideAOI']  = False  #novo
       print ("shape depois da inclusao da coluna insideAOI ",ais_df.shape)
       
       print ("dataframe locations_dfBuffer ", locations_dfBuffer.shape)
       lat = 0
       lon = 0
       print ("print dados locations_dfBuffer ",locations_dfBuffer)
       ais_df = ais_df.reset_index(drop=True) # novo 05Fev

       for i in range(0, len(ais_df)):
            
        lat = ais_df["LAT"][i]
        lon = ais_df["LON"][i]
        b_pontoInsidAOI = isPointInPolygon(lat, lon, locations_dfBuffer)
        if b_pontoInsidAOI:
            ais_df.loc[i,"insideAOI"]  = True

       ais_df = ais_df[(ais_df['insideAOI'] == True)]
       
       print ("Tam array ais_df deletando pontos fora da AOI = ", ais_df.shape)    
       ############################################################

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

def isPointInPolygon (latitude, longitude, polygon):

    y = float(latitude)
    x = float(longitude)
    
    #print ("lats e longs = ", y, "  ", x)

    inside = False
    #print (inside)
    
    lenPoligono = len(polygon)
    j = lenPoligono - 1
    #print("antes j = ", j)
    
    
    #for (i = 0, j = polygon.length - 1; i < polygon.length; j = i++):
    for i in range(0, lenPoligono):
        #print("i = ", i, "j = ", j)
        
       # yi = float(polygon[i][0])
       # xi = float(polygon[i][1])

        #yj = float(polygon[j][0])
        #xj = float(polygon[j][1])

        yi = float(polygon["LAT"][i])
        xi = float(polygon["LONG"][i])

        yj = float(polygon["LAT"][j])
        xj = float(polygon["LONG"][j])


        #print ("xi yi xj yj = ", xi, yi, xj, yj)

        intersect = ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi)

        if (intersect):
            inside = not inside
        j = i
        #print("depois j = ", j)
    return inside


if __name__ == "__main__":
    app.run(debug=True)

