#import pythonCode.py
import json
import flask
from flask import Flask, Response, render_template, request, redirect, url_for, jsonify,send_from_directory,send_file
from flask_cors import CORS, cross_origin # permitir back receber json do front

import pandas as pd
import tkinter as tk
from tkinter import filedialog as fd
import os
import shutil
import io




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

@app.route('/openFileAndFilterAOI', methods=['POST'])
def openFileAndFilterAOI():
    #global locations_dfBuffer
    llon = ulon = llat = ulat = 0.0

    if request.method == 'POST':
       
       dados = request.get_json()
       ais_df = pd.read_csv(dados[4]); #novo
       locations_dfBuffer = pd.read_csv(io.StringIO(dados[5]), sep=",")  #novo 23fev
       
       print ("print dados locations_dfBuffer inicio da funcao",locations_dfBuffer)
       print("variável do post = ", dados)
       
       ais_df.dropna(subset=['LAT', 'LON', 'MMSI'], inplace=True) #novo
       
       llat = float(dados[0])
       ulat = float(dados[1])
       llon = float(dados[2])
       ulon = float(dados[3])

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
       ais_df['TrajID'] = ""  #novo 

       vSpeed = 0
       vCourse = 0

       #########
       ais_df.to_csv("d:ais_orig.csv", index=False)
       MMSI_previous = ais_df["MMSI"][0]
       id_TrajID = 1 
       
       for i in range(0, len(ais_df)):
            
            vSpeed  = ais_df["SOG"][i]
            vCourse = ais_df["COG"][i]
            ########
            MMSI_actual = ais_df['MMSI'][i]
            #if vSpeed < 1:
            #    index_Traj = index_Traj + 1
                        
            if MMSI_previous != MMSI_actual:
                MMSI_previous = MMSI_actual
                id_TrajID = id_TrajID + 1

            speed, course = geracaoBINs(vSpeed, vCourse)
            ais_df.loc[i,"speedBIN"]  = speed
            ais_df.loc[i,"courseBIN"] = course
            ais_df.loc[i,"TrajID"] = id_TrajID
            
       ais_df.to_csv("d:ais_trajID.csv", index=False)

       print ("Tam array ais depois = ",ais_df.shape)
       print(ais_df.head(10))
       #ais_df_em_json = [x.to_json() for x in ais_df]
       #resposta = jsonify(ais_df_em_json)
       ais_df_json = ais_df.to_json(orient='values')
       resposta = jsonify(ais_df_json, id_TrajID)
       resposta.headers.add("Access-Control-Allow-Origin", "*")
       return resposta #("", 204)
    

def selectNameDir():
    root = tk.Tk()
    root.geometry("500x400") # not working
    root.wm_attributes('-topmost', 1)   
    root.lift()     # to work with others OS which are not windows
    root.withdraw()
   
    dirPath = fd.askdirectory(parent=root, title='Select a directory')
    #dirPath = fd.askopenfilename(parent=root, title='Select a file', filetypes=[("CSV files", ".csv")])
    print(dirPath)
    root.destroy()
 
    return dirPath

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

@app.route('/checkLoginName', methods=['POST'])
def checkLoginName():
        
    global fileNameExpert
    global loginName
    
    loginName = request.get_json()
    print("linha 152 loginName = ", loginName)
    fileNameExpert = "none"
    expertsID_df = pd.read_csv("static/expertFiles/expertsID.csv")
    print("arq expertsID = ", expertsID_df.head(5))
    for i in range(0, len(expertsID_df)):
        nameLoginFileCSV = expertsID_df["name"][i]
        if loginName == nameLoginFileCSV:
            print ("linha 160 nome = ", nameLoginFileCSV)
            fileNameExpert = expertsID_df["filename"][i]
                
    print("filename = ", fileNameExpert)
    resposta = jsonify(fileNameExpert)
    #resposta = fileNameExpert
    resposta.headers.add("Access-Control-Allow-Origin", "*")
    return resposta

@app.route('/loadExpertFile', methods=['GET'])
def loadExpertFile():
    global expert_df
    global expert_full_df
    expertCSV_File = "static/expertFiles/" + fileNameExpert
    expert_df = pd.read_csv(expertCSV_File)
    expert_full_df = pd.read_csv("static/expertFiles/" + "expert_full.csv") # novo 22fev
    print(expertCSV_File)
    print(expert_df)
    resposta = jsonify(expertCSV_File)
    resposta.headers.add("Access-Control-Allow-Origin", "*")
    return resposta

@app.route('/downloadClassification',  methods=["GET"])
def downloadClassification():
    
    #arquivos = []
    #for nome_do_arquivo in os.listdir(strDirectory):
     #   endereco_do_arquivo = os.path.join(strDirectory, nome_do_arquivo)

      #  if(os.path.isfile(endereco_do_arquivo)):
       #     arquivos.append(nome_do_arquivo)

    #print("lista de arquivos = ", arquivos)
    strDirName = selectNameDir()
    src1 = 'static/expertFiles/' + fileNameExpert
    src2 = 'static/expertFiles/' + 'expert_full.csv'
    destination1 = strDirName + '/' + fileNameExpert
    destination2 = strDirName + '/' + 'expert_full.csv'

    shutil.copyfile(src1, destination1)
    shutil.copyfile(src2, destination2)
    
    resposta = jsonify(src1)# response useless
    resposta.headers.add("Access-Control-Allow-Origin", "*")
    return resposta

@app.route('/saveClassification', methods=['POST'])
def saveClassification():
    expertID = loginName
    dados = request.get_json()
    trajetoriaID = dados[0]
    clusteringSelection = dados[1]
    normal = dados[2]
    confiabilitySelection = dados[3]
    data = dados[4]
    hora = dados[5]
    expertCSV_File = "static/expertFiles/" + fileNameExpert
    expertCSC_FullFile = "static/expertFiles/" + "expert_full.csv"
  
    index = len(expert_df)
    index_full = len(expert_full_df)
    print("tamanho expert_df = ", index)

    expert_df.loc[index,"Trajetoria"]  = trajetoriaID
    expert_full_df.loc[index_full,"Trajetoria"]  = trajetoriaID

    expert_df.loc[index,"Expert"]  = expertID
    expert_full_df.loc[index_full,"Expert"]  = expertID

    expert_df.loc[index,"Clustering"]  = clusteringSelection
    expert_full_df.loc[index_full,"Clustering"]  = clusteringSelection

    expert_df.loc[index,"Normal"]  = normal
    expert_full_df.loc[index_full,"Normal"]  = normal

    expert_df.loc[index,"Conf"]  = confiabilitySelection
    expert_full_df.loc[index_full,"Conf"]  = confiabilitySelection

    expert_df.loc[index,"Date"]  = data
    expert_full_df.loc[index_full,"Date"]  = data

    expert_df.loc[index,"Time"]  = hora
    expert_full_df.loc[index_full,"Time"]  = hora

    print("expert_df = ", expert_df)
    expert_df.to_csv(expertCSV_File, index=False)
    expert_full_df.to_csv(expertCSC_FullFile, index=False)
    
    resposta = jsonify(expertCSV_File)
    resposta.headers.add("Access-Control-Allow-Origin", "*")
    return resposta


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

