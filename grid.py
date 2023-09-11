import json
import flask
from flask import Flask, Response, render_template, request, redirect, url_for, jsonify,send_from_directory,send_file
from flask_cors import CORS, cross_origin 

import pandas as pd
#import tkinter as tk
#from tkinter import filedialog as fd
import os
import shutil
import io
import numpy as np
import sys ########

import clustering as clt

app = Flask(__name__)
CORS(app) # novo 09Jul23

global_Historical_AIS_df = pd.DataFrame()#""
global_df_Cluster = pd.DataFrame() #""
global_fileNameExpert = ""  ##### 22 jul
global_loginName = ""    ########
global_expert_df = ""   #####
global_expert_full_df = ""  ######

@app.route('/') 
def homepage():
    #print(sys.path) #
    return render_template("mapaW3-v6-Alt4.html")

@app.route('/success', methods = ['POST'])  
def success():  
    if request.method == 'POST':  
        f = request.files['historical_file']
       # f.save(f.filename)  
        return ""

@app.route('/loadFileAOI', methods=['GET'])
def loadFileAOI():
    
    nameFile = selectNameFile()
    if nameFile == "" :
        resposta = jsonify("")
        resposta.headers.add("Access-Control-Allow-Origin", "*")
        return resposta
    
    locations_df = pd.read_csv(nameFile)    
    locations_dfBuffer = locations_df.copy() 
    #print("Loaded locations from file = ", locations_df) ## novo 11jul23
    locations_df_json = locations_df.to_json(orient='values')
    
    resposta = jsonify(locations_df_json)
    #print("Locations from variavel jsonify = ", resposta) ## novo 11jul
    resposta.headers.add("Access-Control-Allow-Origin", "*")
    return resposta

@app.route('/selectAIS_File', methods=['GET'])
def selectAIS_File():
     
    resposta = jsonify(selectNameFile())
    resposta.headers.add("Access-Control-Allow-Origin", "*")
    return resposta
##################
@app.route('/selectAIS_File2', methods=['POST'])
def selectAIS_File2():
     
    #f = request.files['historical_file']
    f = request.files.getlist('historical_file')

    #dados = request.get_json()
    files = [request.files.get(x) for x in request.files]
    dados0 = request.form.get('latInfGrid')
    dados1 = request.form.get('latSupGrid')

    #dados0 = request.form.getlist('latInfGrid')
    #dados1 = request.form.getlist('latSupGrid')

    dados2 = request.form.get('polygon_CSV')
    #dados2 = request.form.getlist('polygon_CSV')
    dados3 = request.form.get('alturaCelula')

    for fileAIS in files:
        ais_df = pd.read_csv(fileAIS) #novo
        ais_df.shape
        #ais_df2 = pd.read_csv(f[1]); #novo
        print("filename = ", fileAIS.filename)
    #ais_df.shape
        print ("Tam array ais = ",ais_df.shape)
        ais_df.to_csv("d:testeRequest.csv", index=False) # 

    #for i in range(0, len(dados)):
    arr = pd.read_csv(io.StringIO(dados2), sep=",")
    
    print(" latInfGrid = "  , dados0)
    print(" latSupGrid = "  , dados1)
    print(" polygon_CSV = " , dados2)
    print(" alturaCelula = ", dados3)
        
    print("soma = ", float(dados0) + float(dados1))

    print("array polygon = \n", arr)
    #print("soma = ", float(dados0[0]) + float(dados1[0]))
    
    #print ("Tam array ais 2= ",ais_df2.shape)

    #resposta = jsonify(f.filename)
    #resposta.headers.add("Access-Control-Allow-Origin", "*")
    #print("filename = ", f.filename)
    return "" #resposta

############

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
    #global global_Historical_AIS_data
    #global global_Historical_AIS_df
    
    if request.method == 'POST':
       
       dadosAIS = request.form.get('ais_Historical_AOI_ArrayFiltered') 
       dados = pd.read_csv(io.StringIO(dadosAIS), sep=",") 
       #global_Historical_AIS_df, id_TrajID = openFileAndFilterAOI(dadosAIS) # id_TrajId not used
       #global_Historical_AIS_df['NumCluster'] = 999 

       ais_df_gridCells = gridCellsData_for_RoseWind(dados); #global_Historical_AIS_df)
       print("back end - ais_df_gridCells = \n", ais_df_gridCells)
       
       ais_df_gridCells_json = ais_df_gridCells.to_json(orient='values')
       #global_Historical_AIS_df_json = global_Historical_AIS_df.to_json(orient='values')
       resposta = jsonify(ais_df_gridCells_json)
       #resposta = jsonify(global_Historical_AIS_df_json, ais_df_gridCells_json) 
       resposta.headers.add("Access-Control-Allow-Origin", "*")

       return resposta #("", 204)
    
@app.route('/applyClustering', methods=['POST'])
def applyClustering():
    global global_Historical_AIS_df ##### jul23 #alt 06 ago
    global global_df_Cluster

    if request.method == 'POST':
       
       #data = request.get_json()
       
       id_clustering = request.form.get('idClustering') #data[0]
       llat = request.form.get('latInfGrid')   #data[1]
       ulat = request.form.get('latSupGrid')   #data[2] 
       llon = request.form.get('lonInfGrid')    #data[3]
       ulon = request.form.get('lonSupGrid')    #data[4]
       
       parameter1 = request.form.get('param1')    #data[5] 
       parameter2 = request.form.get('param2')    #data[6]
       parameter3 = request.form.get('param3')    #data[7]

       ais_Historical_AOI_ArrayFiltered = request.form.get('ais_Historical_AOI_ArrayFiltered') 
       array_ais_Historical = pd.read_csv(io.StringIO(ais_Historical_AOI_ArrayFiltered), sep=",")  #novo 09set
       #print("array_ais_historical =\n", array_ais_Historical)

       ais_clustered_df, clusterTable_df = clt.select_and_applyclustering(array_ais_Historical, id_clustering, 
                                                                    llon, ulon, llat, ulat, parameter1, parameter2, parameter3)
       
       #global_df_Cluster = ais_clustered_df.copy() 
       #global_df_Cluster = ais_clustered_df ###

       #global_df_Cluster = global_df_Cluster.reset_index(drop=True) 

       ais_clustered_df_json = ais_clustered_df.to_json(orient='values')
       clusterTable_df_json = clusterTable_df.to_json(orient='values')
       resposta = jsonify(ais_clustered_df_json, clusterTable_df_json)
       resposta.headers.add("Access-Control-Allow-Origin", "*")
       return resposta

@app.route('/calc_ClusterMatch', methods=['POST'])
def calc_ClusterMatch():

    #global global_df_Cluster
   # df_cluster = global_df_Cluster.copy()  #####

    if request.method == 'POST':
       
       dados = request.get_json()  #
       df_trajectory = dados[0]     #
       df_cluster_aux = dados[1]    #
       df_cluster = pd.read_csv(io.StringIO(df_cluster_aux), sep=",")  #novo
       
       print("df_cluster = \n", df_cluster)
       #df_trajectory  = request.get_json()
       df_trajectory = pd.Series((v[7] for v in df_trajectory)) # GridCell #indice anterior 21
       
       print("*** TRAJETORIA ARRAY *** \n", df_trajectory)
       #print("*** FIM TRAJETORIA ARRAY ***") 
       
       perc_pointsNotMatch, df_ClusterTotalMatch = clt.calcPercentageCellsMatch(df_cluster, df_trajectory)
       
       df_ClusterTotalMatch_json = df_ClusterTotalMatch.to_json(orient='values')
       
       resposta = jsonify(perc_pointsNotMatch, df_ClusterTotalMatch_json)
       resposta.headers.add("Access-Control-Allow-Origin", "*")
       return resposta

def gridCellsData_for_RoseWind(dadosAIS):
    
    ais_df_gridCells = dadosAIS[["GridCell", "courseBIN", "speedBIN"]] 
    ais_df_gridCells.head(10)
    ais_df_gridCells = ais_df_gridCells.sort_values(by=['GridCell','courseBIN', 'speedBIN'])
    
    ais_df_gridCells['Freq'] = ais_df_gridCells.groupby(['GridCell','courseBIN','speedBIN'])['speedBIN'].transform('count')
    #print ("tam ais_df_gridCells antes = ", len(ais_df_gridCells))
    ais_df_gridCells = ais_df_gridCells.drop_duplicates()
    #print ("tam ais_df_gridCells depois de eliminar duplicatas = ", len(ais_df_gridCells))
    #print (ais_df_gridCells.head(20))
    #ais_df_gridCells.to_csv("d:ais_df_gridCells.csv", index=False) #novo 09jul23

    return ais_df_gridCells

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

    #ais_df.to_csv("d:ais_orig.csv", index=False) # novo 09Jul23
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
        
    #ais_df.to_csv("d:ais_trajID.csv", index=False)
    #print ("Tam array ais = ",ais_df.shape)
    #print(ais_df.head(10))
    
    return ais_df, id_TrajID

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

@app.route('/checkLoginName', methods=['POST'])
def checkLoginName():
        
    global global_fileNameExpert
    global global_loginName
    global global_expert_df  #### 25jul
    global global_expert_full_df  ###

    data = request.get_json() # 22 jul
    global_loginName = data[0]
    expert_password = data[1] ####

    #print("global_loginName e senha = ", global_loginName, expert_password)
    global_fileNameExpert = "none"
    expertsID_df = pd.read_csv("static/expertFiles/expertsID.csv")
    #print("arq expertsID = ", expertsID_df.head(5))
    for i in range(0, len(expertsID_df)):
        nameLoginFileCSV = expertsID_df["name"][i]
        if global_loginName == nameLoginFileCSV and expert_password == expertsID_df["password"][i]:
            #print ("linha 160 nome = ", nameLoginFileCSV)
            global_fileNameExpert = expertsID_df["filename"][i]
            expertCSV_File = "static/expertFiles/" + global_fileNameExpert
            global_expert_df = pd.read_csv(expertCSV_File)### 25 jul
            global_expert_full_df = pd.read_csv("static/expertFiles/expert_full.csv") # 25 jul
            break #### 25 jul
    #print("filename = ", global_fileNameExpert)
    resposta = jsonify(global_fileNameExpert)
    resposta.headers.add("Access-Control-Allow-Origin", "*")
    return resposta

@app.route('/loadExpertFile', methods=['GET'])
def loadExpertFile():
    global global_expert_df
    global global_expert_full_df
    global global_fileNameExpert

    expertCSV_File = "static/expertFiles/" + global_fileNameExpert
    global_expert_df = pd.read_csv(expertCSV_File)
    global_expert_full_df = pd.read_csv("static/expertFiles/expert_full.csv") # novo 22fev
    
    resposta = jsonify(expertCSV_File)
    resposta.headers.add("Access-Control-Allow-Origin", "*")
    return resposta


########################## ORIGINAL VERSION - NOT USED  ####################
def ORIGINAL_openFileAndFilterAOI(dados): 
    
    llat = float(dados[0])
    ulat = float(dados[1])
    llon = float(dados[2])
    ulon = float(dados[3])

    ais_df = pd.read_csv(dados[4]); #novo
    locations_dfBuffer = pd.read_csv(io.StringIO(dados[5]), sep=",")  #novo 23fev

    largCell = float(dados[6])
    altCell  = float(dados[7])
    qtdeCel_X= float(dados[8])
    
    ais_df.dropna(subset=['LAT', 'LON', 'MMSI'], inplace=True) #novo
    
    #print ("Tam array ais antes exclusao fora do Grid = ",ais_df.shape)
    ######### filtro
    ais_df = ais_df[(ais_df['LON'] > llon)]
    ais_df = ais_df[(ais_df['LON'] < ulon)]
    ais_df = ais_df[(ais_df['LAT'] > llat)]
    ais_df = ais_df[(ais_df['LAT'] < ulat)]

    #print ("Tam array ais depois exclusao fora do Grid = ",ais_df.shape)

    ais_df = ais_df[(ais_df['LON'] <  180)]
    ais_df = ais_df[(ais_df['LON'] > -180)]
    ais_df = ais_df[(ais_df['LAT'] <  90)]
    ais_df = ais_df[(ais_df['LAT'] > -90)]

    #print ("Tam array ais depois exclusao valores fora da faixa = ",ais_df.shape)
    #### NOVO 05fev #####################################
    ais_df['insideAOI']  = False  #novo
    #print ("shape depois da inclusao da coluna insideAOI ",ais_df.shape)
    #print ("dataframe locations_dfBuffer ", locations_dfBuffer.shape)
    #lat = 0
    #lon = 0
    #print ("print dados locations_dfBuffer ",locations_dfBuffer)
    ais_df = ais_df.reset_index(drop=True) # novo 05Fev

    for i in range(0, len(ais_df)):
        
        lat = ais_df["LAT"][i]
        lon = ais_df["LON"][i]
        b_pontoInsidAOI = isPointInPolygon(lat, lon, locations_dfBuffer)
        if b_pontoInsidAOI:
            ais_df.loc[i,"insideAOI"]  = True

    ais_df = ais_df[(ais_df['insideAOI'] == True)]
    
    #print ("Tam array ais_df deletando pontos fora da AOI = ", ais_df.shape)    
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
    #ais_df.to_csv("d:ais_orig.csv", index=False) # novo 09Jul23
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
        
    #ais_df.to_csv("d:ais_trajID.csv", index=False) # novo 09Jul23
    #print ("Tam array ais depois = ",ais_df.shape)
    #print(ais_df.head(10))
    
    return ais_df, id_TrajID

########### not used in the web environment; used javascript code instead ######
def selectNameDir(): 
    dirPath = ""
    #root = tk.Tk()
    #root.geometry("500x400") # not working
    #root.wm_attributes('-topmost', 1)   
    #root.lift()     # to work with others OS which are not windows
    #root.withdraw()
   
    #try:
    #    dirPath = fd.askdirectory(parent=root, title='Select a directory')

    #except:
    #    dirPath = ""
    
    #print(dirPath)
    #root.destroy()
 
    return dirPath

########### not used in the web environment; used javascript code instead ######
def selectNameFile(): 
    filepath = ""
    #root = tk.Tk()
    #root.geometry("500x400") # not working
    #root.wm_attributes('-topmost', 1)   
    #root.lift()     # to work with others OS which are not windows
    #root.withdraw()
   
    #try:
    #    filepath = fd.askopenfilename(parent=root, title='Select a file', filetypes=[("CSV files", ".csv")])
    
    #except:
    #    filepath = ""  

    #print("filepah = ", filepath)
    #root.destroy()
 
    return filepath

######### replaced with javaScript in Front-end #######
@app.route('/downloadClassification',  methods=["GET"])
def downloadClassification():
    
    #strDirName = selectNameDir()
    #global global_expert_full_df  #####
    msg = ""
    global global_fileNameExpert
    target = 'd:'
    strDirName = "d:"
    if strDirName != "":
        src1 = 'static/expertFiles/' + global_fileNameExpert
        src2 = 'static/expertFiles/expert_full.csv'
        destination1 = strDirName + '/' + global_fileNameExpert
        destination2 = strDirName + '/' + 'expert_full.csv'
        
        #######################################################
        try:
            f = open(src1, 'r')
            file_contents = f.read()
            #print (file_contents)
            f.close()
        except:
            msg = "Error occurred while printing the file."
        
        try:
            shutil.copyfile(src1, destination1)
            shutil.copyfile(src2, destination2)
            msg = "File copied successfully."
            #print("File copied successfully.")
    
        # If source and destination are same
        except shutil.SameFileError:
            msg = "Source and destination represents the same file."
            #print("Source and destination represents the same file.")
        
        # If destination is a directory.
        except IsADirectoryError:
            msg = "Destination is a directory."
            #print("Destination is a directory.")
        
        # If there is any permission issue
        except PermissionError:
            msg = "Permission denied."
            #print("Permission denied.")
        
        # For other errors
        except:
            msg = "Error occurred while copying file."
            #print("Error occurred while copying file.")

        try:
            shutil.copy(src1, target)
            shutil.copy(src2, target)
        except IOError as e:
            msg = "Unable to copy file."
            #print("Unable to copy file. %s" % e)
        except:
            msg = "Unexpected error:"
            #print("Unexpected error:", sys.exc_info())
                
        #shutil.copyfile(src1, destination1)
        #shutil.copyfile(src2, destination2)
    resposta = jsonify(msg)# response useless
    resposta.headers.add("Access-Control-Allow-Origin", "*")
    return resposta

######### replaced with javaScript in Front-end #######
@app.route('/saveClassification', methods=['POST'])
def saveClassification():
    
    global global_expert_df ######## 22 jul
    global global_expert_full_df ###### 22 jul
    global global_fileNameExpert
    global global_loginName

    expertID = global_loginName
    dados = request.get_json()

    filename_historical_AIS = dados[0]
    filename_traj_AIS = dados[1]

    trajetoriaID = dados[2]
    clusteringSelection = dados[3]
    normal = dados[4]
    confiabilitySelection = dados[5]
    data = dados[6]
    hora = dados[7]
    expertCSV_File = "static/expertFiles/" + global_fileNameExpert
    expertCSV_FullFile = "static/expertFiles/expert_full.csv"
  
    index = len(global_expert_df)
    index_full = len(global_expert_full_df)
    
    global_expert_df.loc[index,"Filename_historical_AIS"]  = filename_historical_AIS #####
    global_expert_full_df.loc[index_full,"Filename_historical_AIS"]  = filename_historical_AIS

    global_expert_df.loc[index,"Filename_traj_AIS"]  = filename_traj_AIS #####
    global_expert_full_df.loc[index_full,"Filename_traj_AIS"]  = filename_traj_AIS
    
    global_expert_df.loc[index,"Trajetoria"]  = trajetoriaID
    global_expert_full_df.loc[index_full,"Trajetoria"]  = trajetoriaID

    global_expert_df.loc[index,"Expert"]  = expertID
    global_expert_full_df.loc[index_full,"Expert"]  = expertID

    global_expert_df.loc[index,"Clustering"]  = clusteringSelection
    global_expert_full_df.loc[index_full,"Clustering"]  = clusteringSelection

    global_expert_df.loc[index,"Normal"]  = normal
    global_expert_full_df.loc[index_full,"Normal"]  = normal

    global_expert_df.loc[index,"Conf"]  = confiabilitySelection
    global_expert_full_df.loc[index_full,"Conf"]  = confiabilitySelection

    global_expert_df.loc[index,"Date"]  = data
    global_expert_full_df.loc[index_full,"Date"]  = data

    global_expert_df.loc[index,"Time"]  = hora
    global_expert_full_df.loc[index_full,"Time"]  = hora

    #print("global_expert_df = ", global_expert_df)
    global_expert_df.to_csv(expertCSV_File, index=False) #########
    global_expert_full_df.to_csv(expertCSV_FullFile, index=False)  #######

    ######################### jul 23
    df = pd.read_csv(expertCSV_File)
    df2 = pd.read_csv(expertCSV_FullFile)
    #print("Expert file = ", df)
    #print("Expert full file = ",  df2)
    
    resposta = jsonify(expertCSV_File)
    resposta.headers.add("Access-Control-Allow-Origin", "*")
    return resposta

######### replaced with javaScript in Front-end #######
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

######### replaced with javaScript in Front-end #######
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
           #print ("Tam array ais antes exclusao fora do Grid = ",df_ais_aux.shape)
           df_ais_aux = df_ais_aux[(df_ais_aux['LON'] > llon)]
           df_ais_aux = df_ais_aux[(df_ais_aux['LON'] < ulon)]
           df_ais_aux = df_ais_aux[(df_ais_aux['LAT'] > llat)]
           df_ais_aux = df_ais_aux[(df_ais_aux['LAT'] < ulat)]
            ############
           #print ("Tam array ais depois exclusao fora do Grid = ",df_ais_aux.shape) 
           df_ais_aux = df_ais_aux[(df_ais_aux['LON'] <  180)]
           df_ais_aux = df_ais_aux[(df_ais_aux['LON'] > -180)]
           df_ais_aux = df_ais_aux[(df_ais_aux['LAT'] <  90)]
           df_ais_aux = df_ais_aux[(df_ais_aux['LAT'] > -90)]

           #print ("Tam array ais apos exclusao valores fora da faixa = ",df_ais_aux.shape)
        
           df_ais_aux = df_ais_aux.reset_index(drop=True) 

           for i in range(0, len(df_ais_aux)):
                
                lat = df_ais_aux["LAT"][i]
                lon = df_ais_aux["LON"][i]
                b_pontoInsidAOI = isPointInPolygon(lat, lon, locations_dfBuffer)
                if b_pontoInsidAOI:
                    df_ais_aux.loc[i,"insideAOI"]  = True

           df_ais_aux = df_ais_aux[(df_ais_aux['insideAOI'] == True)]
           df_ais_aux = df_ais_aux.drop(columns=['insideAOI'])
    
           #print ("Tam array df_ais_aux deletando pontos fora da AOI = ", df_ais_aux.shape)  
           #df_ais_aux.to_csv('d:\df' + n + '.csv', index=False, encoding='utf-8-sig') # novo 09Jul23
           
           df_combined_csv = pd.concat([df_combined_csv, df_ais_aux])

       saving_Path = ask_name_File_to_save()

       if saving_Path:    
            df_combined_csv.to_csv(saving_Path, index=False, encoding='utf-8-sig')
       else: # user cancel the file browser window
            stuff =1 #print("No file chosen")  

       return ("", 204)
    
############ not used in the web environment; used javascript code instead ###########
def ask_name_File_to_save():
    #root = tk.Tk()
    #root.geometry("500x400") # not working
    #root.wm_attributes('-topmost', 1)   
    #root.lift()     # to work with others OS which are not windows
    #root.withdraw()

    #get_path_and_name_file = fd.asksaveasfilename(parent=root, title='Give a name for a file to save data', initialfile = 'AOI grid .csv',
    #            defaultextension=".csv",filetypes=[("CSV files", ".csv")])

    #print("path and name of file = ", get_path_and_name_file)
    #root.destroy()
 
    return #get_path_and_name_file

############ not used in the web environment; used javascript code instead ###########
def select_Files_for_concatenation():
    #root = tk.Tk()
    #root.geometry("500x400") # not working
    #root.wm_attributes('-topmost', 1)   
    #root.lift()     # to work with others OS which are not windows
    #root.withdraw()
   
    #filepaths = fd.askopenfilenames(parent=root, title='Select one or more files to concatenate', filetypes=[("CSV files", ".csv")])
    #print(filepaths)
    #root.destroy()
 
    return #filepaths

######### only for test purposes ##############
@app.route('/create_file', methods=['POST']) # Not used
def create_file():
    if request.method == 'POST':
        
        with open(f"{request.form.get('name')}.txt", "w") as f:
            f.write('FILE CREATED AND SUCCESSFULL POST REQUEST!')
        return ('', 204)


if __name__ == "__main__":
    app.run(debug=True)

