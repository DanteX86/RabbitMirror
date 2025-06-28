from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
from typing import List, Dict, Any
import numpy as np

class ClusterEngine:
    def __init__(self, eps: float = 0.3, min_samples: int = 5):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.clustering = DBSCAN(eps=eps, min_samples=min_samples)

    def cluster_videos(self, entries: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Cluster videos based on their titles using DBSCAN."""
        titles = [entry['title'] for entry in entries]
        
        # Create TF-IDF matrix
        tfidf_matrix = self.vectorizer.fit_transform(titles)
        
        # Perform clustering
        labels = self.clustering.fit_predict(tfidf_matrix.toarray())
        
        # Group entries by cluster
        clusters = {}
        for label, entry in zip(labels, entries):
            label_key = f'cluster_{label}' if label >= 0 else 'noise'
            if label_key not in clusters:
                clusters[label_key] = []
            clusters[label_key].append(entry)
            
        return clusters
