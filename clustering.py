import numpy as np
import pandas as pd
from scipy.sparse.csgraph import connected_components
from scipy.spatial.distance import cdist
from sklearn.cluster import DBSCAN, MiniBatchKMeans, KMeans, SpectralClustering

import sklearn.utils
from sklearn.preprocessing import StandardScaler
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import random


def select_and_applyclustering(ais_Historical_df, id_clusteringType, llon, ulon, llat, ulat, paramater1, parameter2):

    global db 
    global labels 
    my_map = Basemap(projection='merc',
        resolution = 'h', area_thresh = 10.0, # l -> low
        llcrnrlon=llon, llcrnrlat=llat, #min longitude (llcrnrlon) and latitude (llcrnrlat)
        urcrnrlon=ulon, urcrnrlat=ulat) #max longitude (urcrnrlon) and latitude (urcrnrlat)

    cluster_df = ais_Historical_df.copy()
    cluster_df = cluster_df[["MMSI", "LAT", "LON", "SOG", "GridCell"]] 
    cluster_df = cluster_df.reset_index(drop=True) 

    xs,ys = my_map(np.asarray(cluster_df.LON), np.asarray(cluster_df.LAT))
    
    cluster_df['xm'] = xs.tolist() # add column xm
    cluster_df['ym'] = ys.tolist()
     
    match id_clusteringType:
        case 1:
            print("case 1")
            
        case 2:  # DBSCAN (LAT, LON)
            print("case 2")
            cluster_df_aux = cluster_df[["xm", "ym"]]
            cluster_df_aux = StandardScaler().fit_transform(cluster_df_aux)
            db = DBSCAN(eps = paramater1, min_samples = parameter2).fit(cluster_df_aux)
            labels = db.labels_

        case 3:  # DBSCAN (LAT, LON, SPEED)
            print("case 3")
            cluster_df_aux = cluster_df[["xm", "ym", "SOG"]]
            cluster_df_aux = StandardScaler().fit_transform(cluster_df_aux)
            db = DBSCAN(eps = paramater1, min_samples = parameter2).fit(cluster_df_aux)
            labels = db.labels_

        case 4:  # KMeans
            print("case 4")
            cluster_df_aux = cluster_df[["xm", "ym"]]
            cluster_df_aux = StandardScaler().fit_transform(cluster_df_aux) #novo 30Mai
            nr_clusters = parameter2
            clusterKmeans = KMeans(n_clusters= nr_clusters).fit_predict(cluster_df_aux)
            labels = clusterKmeans
        
        case 5:  # Spectral Clustering
            cluster_df_aux = cluster_df[["xm", "ym"]]
            cluster_df_aux = StandardScaler().fit_transform(cluster_df_aux) # novo 30Mai
            nr_clusters = parameter2
            spectral = SpectralClustering(n_clusters= nr_clusters, assign_labels='cluster_qr').fit_predict(cluster_df_aux)
            labels = spectral
        
        case 6:  # KMeans Ensemble
            print("case 6")
            cluster_df_aux = cluster_df[["xm", "ym"]]
            cluster_df_aux = StandardScaler().fit_transform(cluster_df_aux) #novo 30Mai
            Number_Kmeans = 50
            Min_Probability = 0.9# paramater1
            nr_clusters =  parameter2

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

            # Extractin the connected components
            n_clusters_ensemble, y_ensemble = connected_components( graph, directed=False, return_labels=True )
            
            print ("********* Nr of clusters final = ", n_clusters_ensemble)
            labels = y_ensemble

        case 7:  # Ensemble Clusters
            print("case 7")
            cluster_df_aux = cluster_df[["xm", "ym"]]
            cluster_df_aux = StandardScaler().fit_transform(cluster_df_aux) #novo 30Mai
            Number_Kmeans = 50
            #Min_Probability = 0.9# paramater1
            nr_clusters =  parameter2
            
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

    print (cluster_df_aux) 
    print (labels[500:560])
    cluster_df["Clus_Db"]=labels
    
    realClusterNum=len(set(labels)) - (1 if -1 in labels else 0)
    print(realClusterNum)
    clusterNum = len(set(labels))
    print(clusterNum)

    no_of_colors=realClusterNum
    color=["#"+''.join([random.choice('0123456789ABCDEF') for i in range(6)])
        for j in range(no_of_colors)]
    print(color)

    df_ClusterTable = pd.DataFrame(columns=['numCluster', 'color', 'cenx', 'ceny'], index=[0])

    for clust_number_P in set(labels):
        
        c=((['#000000']) if clust_number_P == -1 else color[clust_number_P])
        clust_set_P = cluster_df[cluster_df.Clus_Db == clust_number_P]                    
        
        if clust_number_P != -1:  
            cenx=np.mean(clust_set_P.LON) 
            ceny=np.mean(clust_set_P.LAT) 
            df_ClusterTable.loc[clust_number_P, "numCluster"] = clust_number_P
            df_ClusterTable.loc[clust_number_P, "color"] = c
            df_ClusterTable.loc[clust_number_P, "cenx"] = cenx
            df_ClusterTable.loc[clust_number_P, "ceny"] = ceny
        
    df_ClusterTable.shape
    print("********** df_ClusterTable ****** \n", df_ClusterTable)
        
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
    
    df_aux_DB_Cluster = df_Cluster.copy()  
    # df_aux_DB_Cluster = df_Cluster[["Clus_Db", "GridCell"]] 
    df_aux_DB_Cluster = df_aux_DB_Cluster[["Clus_Db", "GridCell"]] 
    df_aux_DB_Cluster.drop_duplicates(inplace=True)
    df_aux_DB_Cluster = df_aux_DB_Cluster.sort_values(by=['Clus_Db', 'GridCell'])
    df_aux_DB_Cluster = df_aux_DB_Cluster.reset_index(drop=True) 
    print("df_aux_DB_Cluster = ", df_aux_DB_Cluster)

    df_ClusterTotalMatch = df_aux_DB_Cluster.copy()
    df_ClusterTotalMatch = df_ClusterTotalMatch[["Clus_Db"]]
    df_ClusterTotalMatch.drop_duplicates(inplace=True)
    df_ClusterTotalMatch['TotalMatch'] = 0
    df_ClusterTotalMatch['perc_TotalMatch'] = 0.0
    df_ClusterTotalMatch = df_ClusterTotalMatch.sort_values(by=['Clus_Db'])
    df_ClusterTotalMatch = df_ClusterTotalMatch.reset_index(drop=True) # novo
    totalClusters = len(df_ClusterTotalMatch)
    print("total clusters = ", totalClusters)
    print("df_ClusterTotalMatch = \n", df_ClusterTotalMatch)

    for i in range(0, totalPointsTrajectory):
        
        flagMatch = False
        numberCellTraj = df_trajectory[i] 
        for j in range(0, totalClusters):
            pointsMatch = 0
            df_aux_Cluster = df_aux_DB_Cluster[df_aux_DB_Cluster.Clus_Db == df_ClusterTotalMatch["Clus_Db"][j]]
            df_aux_Cluster = df_aux_Cluster.reset_index(drop=True)
            
            for k in range(0, len(df_aux_Cluster)):
                numberCellCluster = df_aux_Cluster["GridCell"][k]
                if numberCellTraj == numberCellCluster:
                    pointsMatch = pointsMatch + 1
                    total = df_ClusterTotalMatch["TotalMatch"][j] + 1
                    df_ClusterTotalMatch.loc[j, "TotalMatch"] = total
                    flagMatch = True
                    if df_ClusterTotalMatch["Clus_Db"][j] == -1:
                        flagMatch = False
                    
                    break
        if flagMatch:
            totalPointsNotMatch = totalPointsNotMatch - 1

    for n in range(0, totalClusters):
        totalMatch = df_ClusterTotalMatch["TotalMatch"][n]
        percentageMatch = round((totalMatch/totalPointsTrajectory)*100, 2)
        df_ClusterTotalMatch.loc[n, "perc_TotalMatch"] = percentageMatch
            
    perc_pointsNotMatch = round((totalPointsNotMatch/totalPointsTrajectory)*100,2)
    
    print("perc_pointsNotMatch = ", perc_pointsNotMatch)
    print("df_ClusterTotalMatch = \n", df_ClusterTotalMatch)
    
    return perc_pointsNotMatch, df_ClusterTotalMatch