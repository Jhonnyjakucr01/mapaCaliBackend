import os
os.environ['MPLCONFIGDIR'] = os.getcwd()

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import sys
import json
import io
import base64

from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, silhouette_samples
from sklearn.preprocessing import StandardScaler

os.environ["MPLCONFIGDIR"] = os.getcwd()

def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def procesar_comunas(file_path):
    df = pd.read_excel(file_path)

    features_buenas = ['centro comerciales', 'colegios', 'hospitales', 'hoteles', 'universidades',
                       'bancos', 'estrato', 'estaciones mio', 'humedales', 'parques', 'cais']
    features_malas = ['foto multa', 'robos 2019', 'homicidios 2017', 'homicidios 2018',
                      'homicidios 2019', 'homicidios 2020', 'homicidios 2022',
                      'homicidios 2023', 'homicidios 2024']
    all_features = features_buenas + features_malas

    X = df[all_features]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Método del Codo
    inertia = []
    for k in range(1, 11):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto')
        kmeans.fit(X_scaled)
        inertia.append(kmeans.inertia_)

    fig1 = plt.figure()
    plt.plot(range(1, 11), inertia, marker='o')
    plt.title('Método del Codo')
    plt.xlabel('Número de Clusters')
    plt.ylabel('Inercia')
    elbow_plot = fig_to_base64(fig1)
    plt.close(fig1)

    # K-Means
    optimal_clusters = 3
    kmeans = KMeans(n_clusters=optimal_clusters, random_state=42, n_init='auto')
    df['Cluster'] = kmeans.fit_predict(X_scaled)

    # Silhouette
    silhouette_avg = silhouette_score(X_scaled, df['Cluster'])
    silhouette_vals = silhouette_samples(X_scaled, df['Cluster'])

    fig2 = plt.figure()
    y_lower = 10
    for i in range(optimal_clusters):
        cluster_vals = silhouette_vals[df['Cluster'] == i]
        cluster_vals.sort()
        y_upper = y_lower + len(cluster_vals)
        plt.fill_betweenx(np.arange(y_lower, y_upper), 0, cluster_vals)
        y_lower = y_upper + 10
    plt.title('Gráfico de Silueta')
    plt.xlabel('Coeficiente de Silueta')
    plt.ylabel('Clusters')
    silhouette_plot = fig_to_base64(fig2)
    plt.close(fig2)

    # Visualización con PCA
    pca = PCA(n_components=2)
    reduced_data = pca.fit_transform(X_scaled)
    df['PCA1'] = reduced_data[:, 0]
    df['PCA2'] = reduced_data[:, 1]

    fig3 = plt.figure()
    sns.scatterplot(data=df, x='PCA1', y='PCA2', hue='Cluster', palette='tab10', s=100)
    plt.title('Dispersión de Clusters (PCA)')
    cluster_plot = fig_to_base64(fig3)
    plt.close(fig3)

    # Identificación de Grupos Naturales
    grupos_naturales = df.groupby('Cluster').mean().reset_index().to_dict(orient='records')

    # Análisis de Patrones
    patrones = df.groupby('Cluster').agg(['mean', 'std']).reset_index()
    patrones.columns = ['_'.join(col).strip() for col in patrones.columns.values]
    patrones = patrones.to_dict(orient='records')

    # Segmentación
    segmentacion = df.groupby('Cluster').size().reset_index(name='count').to_dict(orient='records')


     # Calcular mejor y peor comuna con datos normalizados
    df['score'] = X_scaled[:, :len(features_buenas)].sum(axis=1) - X_scaled[:, len(features_buenas):].sum(axis=1)
    mejor_comuna = int(df.loc[df['score'].idxmax(), 'comuna'])
    peor_comuna = int(df.loc[df['score'].idxmin(), 'comuna'])

    resultado = {
        'clusters': df[['comuna', 'Cluster']].to_dict(orient='records'),
        'optimal_clusters': optimal_clusters,
        'silhouette_score': silhouette_avg,
        'best_comuna': mejor_comuna,
        'worst_comuna': peor_comuna,
        'elbow_plot': elbow_plot,
        'silhouette_plot': silhouette_plot,
        'cluster_plot': cluster_plot,
        'grupos_naturales': grupos_naturales,
        'patrones': patrones,
        'segmentacion': segmentacion
    }

    return json.dumps(resultado)

# Para ejecutar manualmente:
if __name__ == "__main__":
    import sys
    resultado_json = procesar_comunas(sys.argv[1])
    print(resultado_json)
