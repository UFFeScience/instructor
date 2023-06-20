import json
import flask
from flask import Flask, Response, render_template, request, redirect, url_for, jsonify,send_from_directory,send_file
from flask_cors import CORS, cross_origin 

import pandas as pd
import tkinter as tk
from tkinter import filedialog as fd
import os
import shutil
import io
import numpy as np

import clustering as clt

app = Flask(__name__)

@app.route('/') 
def homepage():

    return render_template("mapaW3-v6-Alt4.html")

@app.route('/create_file', methods=['POST']) # Not used
def create_file():
    if request.method == 'POST':
        
        with open(f"{request.form.get('name')}.txt", "w") as f:
            f.write('FILE CREATED AND SUCCESSFULL POST REQUEST!')
        return ('', 204)

@app.route('/loadFileAOI', methods=['GET'])
def loadFileAOI():
    
    nameFile = selectNameFile()
    if nameFile == "" :
        resposta = jsonify("")
        resposta.headers.add("Access-Control-Allow-Origin", "*")
        return resposta
    
    locations_df = pd.read_csv(nameFile)    
    locations_dfBuffer = locations_df.copy() 
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

# Identificacao posicao do navio no Grid - gridNavio
def GridNavio2(latNavio,lonNavio, latInfAOI, lonInfAOI, larguraCelula, alturaCelula, qtdeCelulasX): 

    distLat = float(latNavio) - float(latInfAOI)
    distLon = float(lonNavio) - float(lonInfAOI)
    posXGridNavio = int(distLon / larguraCelula) + 1
    posYGridNavio = int(distLat / alturaCelula) + 1
    gridNavio = posXGridNavio + (posYGridNavio - 1) * qtdeCelulasX
    return int(gridNavio) #, posXGridNavio, posYGridNavio

@app.route('/openTrajectoryFileAndFilterAOI', methods=['POST'])
def openTrajectoryFileAndFilterAOI():
    
    if request.method == 'POST':
       
       dadosAIS = request.get_json()

       ais_df, id_TrajID = openFileAndFilterAOI(dadosAIS)
       ais_df_json = ais_df.to_json(orient='values')

       resposta = jsonify(ais_df_json, id_TrajID)
       resposta.headers.add("Access-Control-Allow-Origin", "*")
       return resposta #("", 204)

@app.route('/openHistoricalFileAndFilterAOI', methods=['POST'])
def openHistoricalFileAndFilterAOI():
    global global_Historical_AIS_df
    
    if request.method == 'POST':
       
       dadosAIS = request.get_json()

       global_Historical_AIS_df, id_TrajID = openFileAndFilterAOI(dadosAIS) # id_TrajId not used
       global_Historical_AIS_df['NumCluster'] = 999 
       ais_df_gridCells = gridCellsData_for_RoseWind(global_Historical_AIS_df)
       
       ais_df_gridCells_json = ais_df_gridCells.to_json(orient='values')
       global_Historical_AIS_df_json = global_Historical_AIS_df.to_json(orient='values')
       resposta = jsonify(global_Historical_AIS_df_json, id_TrajID, ais_df_gridCells_json)
       resposta = jsonify(global_Historical_AIS_df_json, ais_df_gridCells_json) 
       resposta.headers.add("Access-Control-Allow-Origin", "*")

       return resposta #("", 204)
    
@app.route('/applyClustering', methods=['POST'])
def applyClustering():
    global global_df_Cluster

    if request.method == 'POST':
       
       data = request.get_json()
       
       id_clustering = data[0]
       llat= data[1]
       ulat= data[2] 
       llon= data[3]
       ulon= data[4]
       parameter1 = float(data[5]) # eps
       parameter2 = int(data[6]) #minPts

       ais_clustered_df, clusterTable_df = clt.select_and_applyclustering(global_Historical_AIS_df, id_clustering, 
                                                                    llon, ulon, llat, ulat, parameter1, parameter2)
       
       global_df_Cluster = ais_clustered_df.copy() 
       global_df_Cluster = global_df_Cluster.reset_index(drop=True) 

       ais_clustered_df_json = ais_clustered_df.to_json(orient='values')
       clusterTable_df_json = clusterTable_df.to_json(orient='values')
       resposta = jsonify(ais_clustered_df_json, clusterTable_df_json)
       resposta.headers.add("Access-Control-Allow-Origin", "*")
       return resposta

@app.route('/calc_ClusterMatch', methods=['POST'])
def calc_ClusterMatch():

    if request.method == 'POST':
       df_trajectory  = request.get_json()
       df_trajectory = pd.Series((v[21] for v in df_trajectory))
       
       print("*** INICIO TRAJETORIA ARRAY *** \n", df_trajectory)
       print("*** FIM TRAJETORIA ARRAY ***") 

       print("##### global_df_Cluster #### \n", global_df_Cluster) 

       perc_pointsNotMatch, df_ClusterTotalMatch = clt.calcPercentageCellsMatch(global_df_Cluster, df_trajectory)
       
       df_ClusterTotalMatch_json = df_ClusterTotalMatch.to_json(orient='values')
       
       resposta = jsonify(perc_pointsNotMatch, df_ClusterTotalMatch_json)
       resposta.headers.add("Access-Control-Allow-Origin", "*")
       return resposta

def gridCellsData_for_RoseWind(dadosAIS):
    
    ais_df_gridCells = dadosAIS[["GridCell", "courseBIN", "speedBIN"]] 
    ais_df_gridCells.head(10)
    ais_df_gridCells = ais_df_gridCells.sort_values(by=['GridCell','courseBIN', 'speedBIN'])
    
    ais_df_gridCells['Freq'] = ais_df_gridCells.groupby(['GridCell','courseBIN','speedBIN'])['speedBIN'].transform('count')
    print ("tam ais_df_gridCells antes = ", len(ais_df_gridCells))
    ais_df_gridCells = ais_df_gridCells.drop_duplicates()
    print ("tam ais_df_gridCells depois de eliminar duplicatas = ", len(ais_df_gridCells))
    print (ais_df_gridCells.head(20))
    ais_df_gridCells.to_csv("d:ais_df_gridCells.csv", index=False)

    return ais_df_gridCells

def ORIGINAL_openFileAndFilterAOI(dados): # ORIGINAL VERSION - NOT USED
    
    llat = float(dados[0])
    ulat = float(dados[1])
    llon = float(dados[2])
    ulon = float(dados[3])

    ais_df = pd.read_csv(dados[4]); #novo
    locations_dfBuffer = pd.read_csv(io.StringIO(dados[5]), sep=",")  #novo 23fev

    largCell = float(dados[6])
    altCell  = float(dados[7])
    qtdeCel_X= float(dados[8])
    
    print ("print dados locations_dfBuffer inicio da funcao",locations_dfBuffer)
    print("variável do post = ", dados)
    
    ais_df.dropna(subset=['LAT', 'LON', 'MMSI'], inplace=True) #novo
    
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
    #print ("dataframe locations_dfBuffer ", locations_dfBuffer.shape)
    #lat = 0
    #lon = 0
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
    ais_df['GridCell'] = ""  #novo 28fev

    vSpeed = 0
    vCourse = 0

    #########
    ais_df.to_csv("d:ais_orig.csv", index=False)
    MMSI_previous = ais_df["MMSI"][0]
    id_TrajID = 1 
    
    for i in range(0, len(ais_df)):
        
        lat = ais_df["LAT"][i]
        lon = ais_df["LON"][i]
        vSpeed  = ais_df["SOG"][i]
        vCourse = ais_df["COG"][i]

        ########
        MMSI_actual = ais_df['MMSI'][i]
        #if vSpeed < 1:
        #    index_Traj = index_Traj + 1
                    
        if MMSI_previous != MMSI_actual:
            MMSI_previous = MMSI_actual
            id_TrajID = id_TrajID + 1

        gridCell = GridNavio2(lat,lon, llat, llon, largCell, altCell, qtdeCel_X)
        speed, course = geracaoBINs(vSpeed, vCourse)
        ais_df.loc[i,"speedBIN"]  = speed
        ais_df.loc[i,"courseBIN"] = course
        ais_df.loc[i,"TrajID"] = id_TrajID
        ais_df.loc[i,"GridCell"] = gridCell
        
    ais_df.to_csv("d:ais_trajID.csv", index=False)

    print ("Tam array ais depois = ",ais_df.shape)
    print(ais_df.head(10))
    
    return ais_df, id_TrajID

def openFileAndFilterAOI(dados): # NEW VERSION
    
    llat = float(dados[0])
    llon = float(dados[2])
    ais_df = pd.read_csv(dados[4]); #novo
    largCell = float(dados[6])
    altCell  = float(dados[7])
    qtdeCel_X= float(dados[8])
        
    ais_df.dropna(subset=['LAT', 'LON', 'MMSI'], inplace=True) 
    
    ais_df['insideAOI']  = True  
    ais_df = ais_df.sort_values(by=['MMSI', 'BaseDateTime'])
    ais_df = ais_df.reset_index(drop=True) 
    ais_df['speedBIN']  = ""  
    ais_df['courseBIN'] = ""  
    ais_df['TrajID'] = ""  
    ais_df['GridCell'] = ""  

    vSpeed = 0
    vCourse = 0

    ais_df.to_csv("d:ais_orig.csv", index=False)
    MMSI_previous = ais_df["MMSI"][0]
    id_TrajID = 1 
    
    for i in range(0, len(ais_df)):
        
        lat = ais_df["LAT"][i]
        lon = ais_df["LON"][i]
        vSpeed  = ais_df["SOG"][i]
        vCourse = ais_df["COG"][i]

        MMSI_actual = ais_df['MMSI'][i]
                            
        if MMSI_previous != MMSI_actual:
            MMSI_previous = MMSI_actual
            id_TrajID = id_TrajID + 1

        gridCell = GridNavio2(lat,lon, llat, llon, largCell, altCell, qtdeCel_X)
        speed, course = geracaoBINs(vSpeed, vCourse)
        ais_df.loc[i,"speedBIN"]  = speed
        ais_df.loc[i,"courseBIN"] = course
        ais_df.loc[i,"TrajID"] = id_TrajID
        ais_df.loc[i,"GridCell"] = gridCell
        
    ais_df.to_csv("d:ais_trajID.csv", index=False)

    print ("Tam array ais = ",ais_df.shape)
    print(ais_df.head(10))
    
    return ais_df, id_TrajID

def selectNameDir():
    dirPath = ""
    root = tk.Tk()
    root.geometry("500x400") # not working
    root.wm_attributes('-topmost', 1)   
    root.lift()     # to work with others OS which are not windows
    root.withdraw()
   
    try:
        dirPath = fd.askdirectory(parent=root, title='Select a directory')

    except:
        dirPath = ""
    
    print(dirPath)
    root.destroy()
 
    return dirPath

def selectNameFile():
    filepath = ""
    root = tk.Tk()
    root.geometry("500x400") # not working
    root.wm_attributes('-topmost', 1)   
    root.lift()     # to work with others OS which are not windows
    root.withdraw()
   
    try:
        filepath = fd.askopenfilename(parent=root, title='Select a file', filetypes=[("CSV files", ".csv")])
    
    except:
        filepath = ""  

    print("filepah = ", filepath)
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
    
    strDirName = selectNameDir()
    if strDirName != "":
        src1 = 'static/expertFiles/' + fileNameExpert
        src2 = 'static/expertFiles/' + 'expert_full.csv'
        destination1 = strDirName + '/' + fileNameExpert
        destination2 = strDirName + '/' + 'expert_full.csv'

        shutil.copyfile(src1, destination1)
        shutil.copyfile(src2, destination2)
    resposta = jsonify(strDirName)# response useless
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
    vCourse = ['0N','1NE', '1NE', '2E','2E', '3SE', '3SE', '4S', '4S', '5SW', '5SW', '6W', '6W','7NW','7NW', '0N']
    #if course < 0: # novo 23Mar
    #    course = course + 360  #for negative values
    
    course_Positive = (course + 360) % 360  # convert to positive values if necessary

    index = int(course_Positive // 22.5) # each cardinal and colateral point has a segment of 45 degrees (2 x 22.5)
    
    courseBIN = vCourse[index]
    
    if speed   <= 3:
        speedBIN = 3 #"0-3"
    elif speed <= 7:
        speedBIN = 7 #"3-7"
    elif speed <= 11:
        speedBIN = 11 #"7-11"
    elif speed <= 15:
        speedBIN = 15 #"11-15"
    elif speed <= 20:
        speedBIN = 20 #"15-20"
    else: 
        speedBIN = 99 #"20+"

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
    
    for i in range(0, lenPoligono):
       
        yi = float(polygon["LAT"][i])
        xi = float(polygon["LONG"][i])

        yj = float(polygon["LAT"][j])
        xj = float(polygon["LONG"][j])

        intersect = ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi)

        if (intersect):
            inside = not inside
        j = i
        
    return inside

@app.route('/concat_AIS_Files', methods=['POST'])
def concat_AIS_Files():
    
    if request.method == 'POST':
       
       name_combined_File = 'combined_csv.csv'
       dados = request.get_json()
       llat = float(dados[0])
       ulat = float(dados[1])
       llon = float(dados[2])
       ulon = float(dados[3])
       locations_dfBuffer = pd.read_csv(io.StringIO(dados[4]), sep=",") 

       fileNames = select_Files_for_concatenation()

       if not fileNames:
           return ("", 204)
                  
       ######### filtro
       df_combined_csv = pd.read_csv('static/auxilary_Directory/df_ais_parcial.csv')

       k = 0
       for f in fileNames:
           k = k + 1
           n = str(k)
           df_ais_aux = pd.read_csv(f)
           df_ais_aux['insideAOI']  = False  
           print ("Tam array ais antes exclusao fora do Grid = ",df_ais_aux.shape)
           df_ais_aux = df_ais_aux[(df_ais_aux['LON'] > llon)]
           df_ais_aux = df_ais_aux[(df_ais_aux['LON'] < ulon)]
           df_ais_aux = df_ais_aux[(df_ais_aux['LAT'] > llat)]
           df_ais_aux = df_ais_aux[(df_ais_aux['LAT'] < ulat)]
           
           df_ais_aux = df_ais_aux.reset_index(drop=True) 

           for i in range(0, len(df_ais_aux)):
                
                lat = df_ais_aux["LAT"][i]
                lon = df_ais_aux["LON"][i]
                b_pontoInsidAOI = isPointInPolygon(lat, lon, locations_dfBuffer)
                if b_pontoInsidAOI:
                    df_ais_aux.loc[i,"insideAOI"]  = True

           df_ais_aux = df_ais_aux[(df_ais_aux['insideAOI'] == True)]
           df_ais_aux = df_ais_aux.drop(columns=['insideAOI'])
    
           print ("Tam array df_ais_aux deletando pontos fora da AOI = ", df_ais_aux.shape)  
                      
           df_ais_aux.to_csv('d:\df' + n + '.csv', index=False, encoding='utf-8-sig')
           
           df_combined_csv = pd.concat([df_combined_csv, df_ais_aux])

       saving_Path = ask_name_File_to_save()

       if saving_Path:    
            df_combined_csv.to_csv(saving_Path, index=False, encoding='utf-8-sig')
       else: # user cancel the file browser window
            print("No file chosen")  

       return ("", 204)
    

def ask_name_File_to_save():
    root = tk.Tk()
    root.geometry("500x400") # not working
    root.wm_attributes('-topmost', 1)   
    root.lift()     # to work with others OS which are not windows
    root.withdraw()

    get_path_and_name_file = fd.asksaveasfilename(parent=root, title='Give a name for a file to save data', initialfile = 'AOI grid .csv',
                defaultextension=".csv",filetypes=[("CSV files", ".csv")])

    print("path and name of file = ", get_path_and_name_file)
    root.destroy()
 
    return get_path_and_name_file


def select_Files_for_concatenation():
    root = tk.Tk()
    root.geometry("500x400") # not working
    root.wm_attributes('-topmost', 1)   
    root.lift()     # to work with others OS which are not windows
    root.withdraw()
   
    filepaths = fd.askopenfilenames(parent=root, title='Select one or more files to concatenate', filetypes=[("CSV files", ".csv")])
    print(filepaths)
    root.destroy()
 
    return filepaths



if __name__ == "__main__":
    app.run(debug=True)

