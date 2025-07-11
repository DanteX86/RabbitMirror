from typing import Any, Dict, List

from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer


class ClusterEngine:
    def __init__(self, eps: float = 0.3, min_samples: int = 5):
        self.eps = eps
        self.min_samples = min_samples
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.clustering = DBSCAN(eps=eps, min_samples=min_samples)

    def cluster_videos(self, entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Cluster videos based on their titles using DBSCAN."""
        if not entries:
            return {
                "clusters": {},
                "cluster_info": {
                    "total_clusters": 0,
                    "noise_points": 0,
                    "total_entries": 0,
                },
                "metadata": {"eps": self.eps, "min_samples": self.min_samples},
            }

        try:
            titles = [entry["title"] for entry in entries]

            # Handle case where titles might be empty or too similar
            if not titles or all(not title.strip() for title in titles):
                return {
                    "clusters": {"noise": entries},
                    "cluster_info": {
                        "total_clusters": 0,
                        "noise_points": len(entries),
                        "total_entries": len(entries),
                    },
                    "metadata": {
                        "eps": self.eps,
                        "min_samples": self.min_samples,
                        "warning": "No valid titles for clustering",
                    },
                }

            # Create TF-IDF matrix
            tfidf_matrix = self.vectorizer.fit_transform(titles)

            # Perform clustering
            labels = self.clustering.fit_predict(tfidf_matrix.toarray())

            # Group entries by cluster
            clusters = {}
            noise_count = 0

            for label, entry in zip(labels, entries):
                if label >= 0:
                    label_key = f"cluster_{label}"
                else:
                    label_key = "noise"
                    noise_count += 1

                if label_key not in clusters:
                    clusters[label_key] = []
                clusters[label_key].append(entry)

            # Calculate cluster statistics
            total_clusters = len([k for k in clusters if k != "noise"])

            return {
                "clusters": clusters,
                "cluster_info": {
                    "total_clusters": total_clusters,
                    "noise_points": noise_count,
                    "total_entries": len(entries),
                    "cluster_sizes": {k: len(v) for k, v in clusters.items()},
                },
                "metadata": {
                    "eps": self.eps,
                    "min_samples": self.min_samples,
                    "vectorizer_vocabulary_size": (
                        len(self.vectorizer.vocabulary_)
                        if hasattr(self.vectorizer, "vocabulary_")
                        else 0
                    ),
                },
            }

        except Exception as e:
            # Handle various clustering errors gracefully
            return {
                "error": str(e),
                "clusters": {"noise": entries},
                "cluster_info": {
                    "total_clusters": 0,
                    "noise_points": len(entries),
                    "total_entries": len(entries),
                },
                "metadata": {
                    "eps": self.eps,
                    "min_samples": self.min_samples,
                    "error_type": type(e).__name__,
                },
            }
