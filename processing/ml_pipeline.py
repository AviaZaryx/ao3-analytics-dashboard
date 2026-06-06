import pandas as pd
import numpy as np
import os
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

# --- CONFIGURATION ---
DATA_DIR = r"D:\Downloads\DataVisProj2\data"
MAIN_DATA_PATH = os.path.join(DATA_DIR, "cleaned_ao3_data.csv")
VECTORS_PATH = os.path.join(DATA_DIR, "embeddings.npy")
PCA_PATH = os.path.join(DATA_DIR, "pca_coords.npy")
CLUSTERS_PATH = os.path.join(DATA_DIR, "work_clusters.csv")


def step1_generate_embeddings(text_data):
    """Converts tags/fandoms into dense vector embeddings."""
    print("Loading SentenceTransformer model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    print(f"Generating embeddings for {len(text_data)} works... (This may take a while)")
    embeddings = model.encode(text_data.tolist(), show_progress_bar=True)

    np.save(VECTORS_PATH, embeddings)
    print(f"Saved vectors to {VECTORS_PATH}")
    return embeddings


def step2_run_pca(embeddings, n_components=2):
    """Reduces vector dimensions for 2D visualization."""
    print("Running PCA...")
    pca = PCA(n_components=n_components)
    pca_coords = pca.fit_transform(embeddings)

    np.save(PCA_PATH, pca_coords)
    print(f"Saved PCA coordinates to {PCA_PATH}")
    return pca_coords


def step3_run_clustering(embeddings, pca_coords, work_ids, n_clusters=8):
    """Clusters the dense embeddings and creates a final merged CSV."""
    print(f"Running KMeans clustering with k={n_clusters}...")
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
    cluster_labels = kmeans.fit_predict(pca_coords)

    df_clusters = pd.DataFrame({
        'work_id': work_ids,
        'pca_x': pca_coords[:, 0],
        'pca_y': pca_coords[:, 1],
        'cluster': cluster_labels
    })

    df_clusters.to_csv(CLUSTERS_PATH, index=False)
    print(f"Saved cluster mappings to {CLUSTERS_PATH}")


def run_pipeline():
    """Orchestrates the modular pipeline."""
    print("Loading original data...")
    df = pd.read_csv(MAIN_DATA_PATH, usecols=['work_id', 'fandom', 'additional_tags'])

    df['text_for_ml'] = df['fandom'].fillna('') + " " + df['additional_tags'].fillna('').str.replace(',', ' ')

    embeddings = step1_generate_embeddings(df['text_for_ml'])
    pca_coords = step2_run_pca(embeddings)
    step3_run_clustering(embeddings, pca_coords, df['work_id'])

    print("Pipeline Complete.")


if __name__ == "__main__":
    run_pipeline()