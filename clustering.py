import numpy as np
import pandas as pd
from scipy.sparse.csgraph import connected_components
from scipy.spatial.distance import cdist
from sklearn.cluster import DBSCAN, MiniBatchKMeans, KMeans, SpectralClustering, AgglomerativeClustering, Birch
from sklearn.cluster import MeanShift, OPTICS
from sklearn.mixture import GaussianMixture
import hdbscan

import sklearn.utils
from sklearn.preprocessing import StandardScaler
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import random


def select_and_applyclustering(ais_Historical_df, id_clusteringType, llon, ulon, llat, ulat, parameter1, parameter2, parameter3, flag_apply_Clustering):

    #global db 
    #global labels 
    
    #cluster_df = ais_Historical_df[['MMSI', 'LAT', 'LON', 'SOG', 'GridCell']] # 16 set
    cluster_df = ais_Historical_df[['MMSI', 'LAT', 'LON', 'SOG', 'GridCell']] # 16 set
    #np_labels = cluster_df['Clus_Db'].to_numpy()
    if flag_apply_Clustering == "1":   # false indicates that the historical file has been already clustered
        #np_labels = cluster_df['Clus_Db'].to_numpy()
        #cluster_df = cluster_df[['MMSI', 'LAT', 'LON', 'SOG', 'GridCell']] 

        my_map = Basemap(projection='merc',
            resolution = 'h', area_thresh = 10.0, # l -> low
            llcrnrlon=llon, llcrnrlat=llat, #min longitude (llcrnrlon) and latitude (llcrnrlat)
            urcrnrlon=ulon, urcrnrlat=ulat) #max longitude (urcrnrlon) and latitude (urcrnrlat)
            
       
        #cluster_df = ais_Historical_df[['MMSI', 'LAT', 'LON', 'SOG', 'GridCell']] # 09 ago # removed 16set
        
        cluster_df = cluster_df.reset_index(drop=True) ### 09 ago
        
        #######################
        cluster_df['xm']= 0
        cluster_df['ym']= 0
        print("cluster_df = \n", cluster_df)
        print("tamanho cluster_df = ", len(cluster_df))


        np_cluster_df = cluster_df[["LON","LAT"]].to_numpy()

        index = 0
        for i in np_cluster_df:
            xs,ys = my_map(i[0], i[1])
            cluster_df.loc[index, "xm"] = xs
            cluster_df.loc[index, "ym"] = ys
            index = index + 1
            #df_ClusterTable.loc[clust_number_P, 'ceny'] = ceny
        print("passou pelo for range")
        ########################

        #######
        #xs,ys = my_map(np.asarray(cluster_df.LON), np.asarray(cluster_df.LAT))
        
        #cluster_df['xm'] = xs.tolist() # add column xm
        #cluster_df['ym'] = ys.tolist()
        ######

        cluster_df_tmp = cluster_df[['xm', 'ym']] # novo 24Jun
        cluster_df_tmp = cluster_df_tmp.reset_index(drop=True)

        print("cluster_df_tmp = \n", cluster_df_tmp)

        cluster_df_tmp2 = StandardScaler().fit_transform(cluster_df_tmp.to_numpy()) # novo 24Jun
        
        print("passou pelo StandardScaler")
        print("cluster_df_aux = \n", cluster_df_tmp2)

        cluster_df_aux = pd.DataFrame(cluster_df_tmp2, columns = ['xm','ym'])

        print("antes do match")

        match int(id_clusteringType):
            # Automatic Mode - under development 
            # first part: DBSCAN
            # second part: Ensemble
            case 1: 
                #first part - DBSCAN
                parameter1 = 0.04
                parameter2 = 18
                db = DBSCAN(eps = float(parameter1), min_samples = int(parameter2)).fit(cluster_df_aux)
                labels = db.labels_
                # second part - under development
            
            # Agglomerative Clustering
            # main parameters: 1 - estimate of the number of clusters
            case 2:  
                #print("case 2")
                AC = AgglomerativeClustering(n_clusters=int(parameter1))
                #yhat = AC.fit_predict(cluster_df_aux)
                #clusters = unique(yhat)
                labels = AC.fit_predict(cluster_df_aux)
                #print ("AC clusters = ", labels)
            

            # BIRCH
            # main parameters: 1- threshold; 2 - n_clusters 
            case 3:  
                #print("case 3")
                B = Birch(threshold=float(parameter1), n_clusters=int(parameter2))
                B.fit(cluster_df_aux)
                labels = B.predict(cluster_df_aux)
                
            # DBSCAN (LAT, LON)
            # main parameters: 1 - eps; 2 - min_samples
            case 4: 
                print("dentro do DBSCAN")
                db = DBSCAN(eps = float(parameter1), min_samples = int(parameter2)).fit(cluster_df_aux)
                labels = db.labels_

            # DBSCAN (LAT, LON, SPEED)
            # main parameters: 1 - eps; 2 - min_samples
            case 5:  
                db = DBSCAN(eps = float(parameter1), min_samples = int(parameter2)).fit(cluster_df_aux)
                labels = db.labels_

            # HDBSCAN
            # main parameters: ???
            #HDBSCAN(algorithm='best', alpha=1.0, approx_min_span_tree=True,
            #         gen_min_span_tree=False, leaf_size=40, memory=Memory(cachedir=None),
            #         metric='euclidean', min_cluster_size=5, min_samples=None, p=None)
            case 6:  
                #print("case 6")
                HDB = hdbscan.HDBSCAN(cluster_selection_epsilon = float(parameter1), min_samples=int(parameter2), min_cluster_size=int(parameter3))
                HDB.fit(cluster_df_aux)
                labels = HDB.labels_

            # KMeans
            # main parameters: 1- n_clusters 
            case 7: 
                nr_clusters = int(parameter1)
                clusterKmeans = KMeans(n_clusters= nr_clusters).fit_predict(cluster_df_aux)
                labels = clusterKmeans

            # Mean Shift
            # main parameters: 1 - bandwidth
            case 8:  
                #print("case 8")
                MS = MeanShift()
                labels = MS.fit_predict(cluster_df_aux)

            # Mini-Batch K-Means
            # main parameters: 1 - n_clusters 
            case 9:  
                #print("case 9")
                MBK = MiniBatchKMeans(n_clusters=int(parameter1))
                MBK.fit(cluster_df_aux)
                labels = MBK.predict(cluster_df_aux)

            # Mixture of Gaussians
            # main parameters: 1 - n_clusters
            case 10: 
                #print("case 10")
                GM = GaussianMixture(n_components=int(parameter1))
                GM.fit(cluster_df_aux)
                labels = GM.predict(cluster_df_aux)

            # OPTICS
            # main parameters: 1 - eps; 2 - min_samples
            case 11:  
                #print("case 11")
                O = OPTICS(eps=float(parameter1), min_samples=int(parameter2))
                labels = O.fit_predict(cluster_df_aux)
            
            # Spectral Clustering
            # main parameters: 1 - n_clusters
            case 12:  
                nr_clusters = int(parameter1)
                try:
                    spectral = SpectralClustering(n_clusters= nr_clusters, assign_labels='cluster_qr').fit_predict(cluster_df_aux)
                    labels = spectral
                except:
                    stuff = 0 #print("Error execution Spectral Clustering")
            
            # KMeans Ensemble
            # main parameters: 1 - Number_Kmeans; 2 - Min_Probability; 3 - n_clusters
            case 13:  
                Number_Kmeans = int(parameter1)
                Min_Probability = float(parameter2)
                nr_clusters =  int(parameter3)

                # Generating base models
                clustering_models = Number_Kmeans*[
                    # Note: Do not set a random_state, as the variability is crucial
                    # This is a extreme simple K-Means
                    MiniBatchKMeans(n_clusters=nr_clusters, batch_size=64, n_init=1, max_iter=20)
                ]

                clt_sim_matrix = ClusterSimilarityMatrix()
                for model in clustering_models:
                    clt_sim_matrix.fit( model.fit_predict(cluster_df_aux))  # X=X_vectors) ) 

                sim_matrix = clt_sim_matrix.similarity
                norm_sim_matrix = sim_matrix/sim_matrix.diagonal()

                # Transforming the probabilities into graph edges
                # similar to DBSCAN
                graph = (norm_sim_matrix>Min_Probability).astype(int)

                # Extract the connected components
                n_clusters_ensemble, y_ensemble = connected_components( graph, directed=False, return_labels=True )
                
                #print ("********* Nr of clusters final = ", n_clusters_ensemble)
                labels = y_ensemble

            # Ensemble Clusters
            # main parameters: 1 - Number_Kmeans; 2 - n_clusters
            case 14:  
                Number_Kmeans = int(parameter1)
                #Min_Probability = 0.9# paramater1
                nr_clusters =  int(parameter2)
                
                clustering_models = Number_Kmeans*[
                # Note: Do not set a random_state, as the variability is crucial
                    MiniBatchKMeans(n_clusters=16, batch_size=64, n_init=1, max_iter=20)
                ]
                aggregator_clt = SpectralClustering(n_clusters=8, affinity="precomputed")

                ens_clt=EnsembleClustering(clustering_models, aggregator_clt)
                ensemble = ens_clt.fit_predict(cluster_df_aux)
                labels = ensemble


            case _:
                print("Case valor default")
                return  

        #print (cluster_df_aux) 
        print ("labels = \n", labels[3620:3760])
        cluster_df["Clus_Db"]=labels
    # end of if
    else:
        cluster_df = ais_Historical_df[['MMSI', 'LAT', 'LON', 'SOG', 'GridCell','xm','ym','Clus_Db']] # 16 set

    np_labels = cluster_df["Clus_Db"].to_numpy()
    print ("np_labels = \n", np_labels[3620:3760])
    ##############
    
    realClusterNum=len(set(np_labels)) - (1 if -1 in np_labels else 0)
    #print(realClusterNum)
    clusterNum = len(set(np_labels))
    #print(clusterNum)

    no_of_colors=realClusterNum
    color=["#"+''.join([random.choice('0123456789ABCDEF') for i in range(6)])
        for j in range(no_of_colors)]
    #print(color)

    df_ClusterTable = pd.DataFrame(columns=['numCluster', 'color', 'cenx', 'ceny'], index=[0])

    print("antes do for clust_number_P")

    for clust_number_P in set(np_labels):
        
        c=((['#000000']) if clust_number_P == -1 else color[clust_number_P])
        clust_set_P = cluster_df[cluster_df.Clus_Db == clust_number_P]                    
        #print("dentro do for clust_number_P")
        if clust_number_P != -1:  
            cenx=np.mean(clust_set_P.LON) 
            ceny=np.mean(clust_set_P.LAT) 
            df_ClusterTable.loc[clust_number_P, 'numCluster'] = clust_number_P
            df_ClusterTable.loc[clust_number_P, 'color'] = c
            df_ClusterTable.loc[clust_number_P, 'cenx'] = cenx
            df_ClusterTable.loc[clust_number_P, 'ceny'] = ceny
        
    df_ClusterTable.shape
    #print("********** df_ClusterTable ****** \n", df_ClusterTable)
    ################
    cluster_df.to_csv("d:cluster_df.csv", index=False) # 

    ###############
        
    return cluster_df, df_ClusterTable

# original class Code available at https://github.com/jaumpedro214/posts.git
class ClusterSimilarityMatrix():
    
    def __init__(self) -> None:
        self._is_fitted = False

    def fit(self, y_clusters):
        if not self._is_fitted:
            self._is_fitted = True
            self.similarity = self.to_binary_matrix(y_clusters)
            return self

        self.similarity += self.to_binary_matrix(y_clusters)

    def to_binary_matrix(self, y_clusters):
        y_reshaped = np.expand_dims(y_clusters, axis=-1)
        return (cdist(y_reshaped, y_reshaped, 'cityblock')==0).astype(int)

# original class Code available at https://github.com/jaumpedro214/posts.git
class EnsembleClustering():
    def __init__(self, base_estimators, aggregator, distances=False):
        self.base_estimators = base_estimators
        self.aggregator = aggregator
        self.distances = distances

    def fit(self, X):
        X_ = X.copy()

        clt_sim_matrix = ClusterSimilarityMatrix()
        for model in self.base_estimators:
            clt_sim_matrix.fit(model.fit_predict(X=X_))
        
        sim_matrix = clt_sim_matrix.similarity
        self.cluster_matrix = sim_matrix/sim_matrix.diagonal()

        if self.distances:
            self.cluster_matrix = np.abs(np.log(self.cluster_matrix + 1e-8)) # Avoid log(0)

    def fit_predict(self, X):
        self.fit(X)
        y = self.aggregator.fit_predict(self.cluster_matrix)
        return y

def calcPercentageCellsMatch(df_Cluster, df_trajectory):
    flagMatch = False
    totalMatchAllClusters = 0
    pointsMatch = 0
    totalPointsTrajectory = len(df_trajectory)
    totalPointsNotMatch = totalPointsTrajectory; # initial value
    print("totalPointsTrajectory = ", totalPointsTrajectory)
    
    #df_tmp_DB_Cluster = df_Cluster.copy()  #########
    df_aux_DB_Cluster = df_Cluster[["Clus_Db", "GridCell"]] 
    #df_aux_DB_Cluster = df_tmp_DB_Cluster.loc[:,['Clus_Db', 'GridCell']].copy() ### 09 ago
    df_aux_DB_Cluster.drop_duplicates(inplace=True)
    df_aux_DB_Cluster = df_aux_DB_Cluster.sort_values(by=['Clus_Db', 'GridCell'])
    df_aux_DB_Cluster = df_aux_DB_Cluster.reset_index(drop=True) 
    print("df_aux_DB_Cluster = ", df_aux_DB_Cluster)

    df_tmp_ClusterTotalMatch = df_aux_DB_Cluster.copy() #############
    df_ClusterTotalMatch = df_tmp_ClusterTotalMatch.loc[:,['Clus_Db']].copy()  ## 09 ago
    df_ClusterTotalMatch.drop_duplicates(inplace=True)
    df_ClusterTotalMatch['TotalMatch'] = 0
    df_ClusterTotalMatch['perc_TotalMatch'] = 0.0
    df_ClusterTotalMatch = df_ClusterTotalMatch.sort_values(by=['Clus_Db'])
    df_ClusterTotalMatch = df_ClusterTotalMatch.reset_index(drop=True) # novo
    totalClusters = len(df_ClusterTotalMatch)
    #print("total clusters = ", totalClusters)
    #print("df_ClusterTotalMatch = \n", df_ClusterTotalMatch)

    for i in range(0, totalPointsTrajectory):
        
        flagMatch = False
        numberCellTraj = df_trajectory[i] 
        for j in range(0, totalClusters):
            pointsMatch = 0
            df_aux_Cluster = df_aux_DB_Cluster[df_aux_DB_Cluster.Clus_Db == df_ClusterTotalMatch["Clus_Db"][j]]
            df_aux_Cluster = df_aux_Cluster.reset_index(drop=True)
            
            for k in range(0, len(df_aux_Cluster)):
                numberCellCluster = df_aux_Cluster['GridCell'][k]
                if numberCellTraj == numberCellCluster:
                    pointsMatch = pointsMatch + 1
                    total = df_ClusterTotalMatch['TotalMatch'][j] + 1
                    df_ClusterTotalMatch.loc[j, 'TotalMatch'] = total
                    flagMatch = True
                    if df_ClusterTotalMatch['Clus_Db'][j] == -1:
                        flagMatch = False
                    
                    break
        if flagMatch:
            totalPointsNotMatch = totalPointsNotMatch - 1

    for n in range(0, totalClusters):
        totalMatch = df_ClusterTotalMatch['TotalMatch'][n]
        percentageMatch = round((totalMatch/totalPointsTrajectory)*100, 2)
        df_ClusterTotalMatch.loc[n, 'perc_TotalMatch'] = percentageMatch
            
    perc_pointsNotMatch = round((totalPointsNotMatch/totalPointsTrajectory)*100,2)
    #print("perc_pointsNotMatch = ", perc_pointsNotMatch)
    #print("df_ClusterTotalMatch = \n", df_ClusterTotalMatch)
    
    return perc_pointsNotMatch, df_ClusterTotalMatch