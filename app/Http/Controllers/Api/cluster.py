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

    # Score personalizado
    df['score'] = X_scaled[:, :len(features_buenas)].sum(axis=1) - X_scaled[:, len(features_buenas):].sum(axis=1)
    mejor_idx = df['score'].idxmax()
    peor_idx = df['score'].idxmin()
    mejor_comuna = int(df.loc[mejor_idx, 'comuna'])
    peor_comuna = int(df.loc[peor_idx, 'comuna'])

    # PCA para visualización
    pca = PCA(n_components=2)
    reduced_data = pca.fit_transform(X_scaled)
    df['PCA1'] = reduced_data[:, 0]
    df['PCA2'] = reduced_data[:, 1]

    fig3 = plt.figure()
    ax = sns.scatterplot(data=df, x='PCA1', y='PCA2', hue='Cluster', palette='tab10', s=100)
    plt.title('Dispersión de Clusters (PCA)')

    # Anotación de mejor y peor comuna
    ax.scatter(df.loc[mejor_idx, 'PCA1'], df.loc[mejor_idx, 'PCA2'], color='green', edgecolor='black', s=200, label='Mejor Comuna', zorder=5)
    ax.text(df.loc[mejor_idx, 'PCA1'], df.loc[mejor_idx, 'PCA2'], f"Mejor ({mejor_comuna})", fontsize=9, ha='right')

    ax.scatter(df.loc[peor_idx, 'PCA1'], df.loc[peor_idx, 'PCA2'], color='red', edgecolor='black', s=200, label='Peor Comuna', zorder=5)
    ax.text(df.loc[peor_idx, 'PCA1'], df.loc[peor_idx, 'PCA2'], f"Peor ({peor_comuna})", fontsize=9, ha='left')

    plt.legend()
    cluster_plot = fig_to_base64(fig3)
    plt.close(fig3)

    # Gráfico adicional: Score por comuna
    df_scores = df[['comuna', 'score']].sort_values(by='score', ascending=False)
    fig4 = plt.figure(figsize=(12, 6))
    ax4 = sns.barplot(data=df_scores, x='comuna', y='score', palette='coolwarm')
    plt.title('Score por Comuna (Mejor a Peor)', fontsize=14)
    plt.xlabel('Comuna', fontsize=12)
    plt.ylabel('Score', fontsize=12)
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.tight_layout()
    score_plot = fig_to_base64(fig4)
    plt.close(fig4)



    # Identificación de Grupos Naturales
    grupos_naturales = df.groupby('Cluster').mean().reset_index().to_dict(orient='records')

    # Análisis de Patrones
    patrones = df.groupby('Cluster').agg(['mean', 'std']).reset_index()
    patrones.columns = ['_'.join(col).strip() for col in patrones.columns.values]
    patrones = patrones.to_dict(orient='records')

    # Segmentación
    segmentacion = df.groupby('Cluster').size().reset_index(name='count').to_dict(orient='records')

    resultado = {
        'clusters': df[['comuna', 'Cluster']].to_dict(orient='records'),
        'optimal_clusters': optimal_clusters,
        'silhouette_score': silhouette_avg,
        'best_comuna': mejor_comuna,
        'worst_comuna': peor_comuna,
        'elbow_plot': elbow_plot,
        'silhouette_plot': silhouette_plot,
        'cluster_plot': cluster_plot,
        'score_plot': score_plot,
        'grupos_naturales': grupos_naturales,
        'patrones': patrones,
        'segmentacion': segmentacion
    }

    return json.dumps(resultado)

if __name__ == "__main__":
    resultado_json = procesar_comunas(sys.argv[1])
    print(resultado_json)
