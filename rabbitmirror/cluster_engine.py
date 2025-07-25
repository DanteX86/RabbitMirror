from typing import Any, Dict, List

from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer

from .error_recovery import RetryConfig, monitor_errors, robust_operation
from .exceptions import ClusteringError, DataValidationError


class ClusterEngine:
    def __init__(self, eps: float = 0.3, min_samples: int = 5):
        if eps <= 0:
            raise ClusteringError(
                "eps parameter must be positive",
                algorithm="DBSCAN",
                error_code="INVALID_EPS_PARAMETER",
            )
        if min_samples < 1:
            raise ClusteringError(
                "min_samples parameter must be at least 1",
                algorithm="DBSCAN",
                error_code="INVALID_MIN_SAMPLES_PARAMETER",
            )

        self.eps = eps
        self.min_samples = min_samples
        self.retry_config = RetryConfig(
            max_attempts=3,
            base_delay=1.0,
            retryable_exceptions=[ValueError, RuntimeError],
        )

        try:
            self.vectorizer = TfidfVectorizer(stop_words="english")
            self.clustering = DBSCAN(eps=eps, min_samples=min_samples)
        except Exception as e:
            raise ClusteringError(
                f"Failed to initialize clustering components: {str(e)}",
                algorithm="DBSCAN",
                error_code="CLUSTERING_INIT_FAILED",
            ) from e

    @robust_operation(
        retry_config=RetryConfig(max_attempts=3, base_delay=1.0),
        timeout_seconds=120.0,
    )
    @monitor_errors
    def cluster_videos(self, entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Cluster videos based on their titles using DBSCAN.

        Args:
            entries: List of video entries with 'title' field

        Returns:
            Dict containing clustering results

        Raises:
            DataValidationError: If entries data is invalid
            ClusteringError: If clustering operation fails
        """
        if not isinstance(entries, list):
            raise DataValidationError(
                "entries must be a list", error_code="INVALID_ENTRIES_TYPE"
            )

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

        # Validate entries have required fields
        for i, entry in enumerate(entries):
            if not isinstance(entry, dict):
                raise DataValidationError(
                    f"Entry {i} is not a dictionary", error_code="INVALID_ENTRY_TYPE"
                )
            if "title" not in entry:
                raise DataValidationError(
                    f"Entry {i} missing required 'title' field",
                    error_code="MISSING_TITLE_FIELD",
                )

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
            try:
                tfidf_matrix = self.vectorizer.fit_transform(titles)
            except ValueError as e:
                raise ClusteringError(
                    f"TF-IDF vectorization failed: {str(e)}",
                    algorithm="TF-IDF",
                    error_code="TFIDF_VECTORIZATION_FAILED",
                ) from e

            # Perform clustering
            try:
                labels = self.clustering.fit_predict(tfidf_matrix.toarray())
            except Exception as e:
                raise ClusteringError(
                    f"DBSCAN clustering failed: {str(e)}",
                    algorithm="DBSCAN",
                    error_code="DBSCAN_CLUSTERING_FAILED",
                ) from e

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

        except ClusteringError:
            # Re-raise clustering errors as-is
            raise
        except Exception as e:
            # Handle unexpected errors
            raise ClusteringError(
                f"Unexpected clustering error: {str(e)}",
                algorithm="DBSCAN",
                error_code="CLUSTERING_UNEXPECTED_ERROR",
            ) from e
