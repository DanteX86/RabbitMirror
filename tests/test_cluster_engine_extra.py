import pytest

from rabbitmirror.cluster_engine import ClusterEngine
from rabbitmirror.exceptions import ClusteringError, DataValidationError


def test_invalid_parameters_raise():
    with pytest.raises(ClusteringError):
        ClusterEngine(eps=0.0)
    with pytest.raises(ClusteringError):
        ClusterEngine(min_samples=0)


def test_invalid_entries_type_raises():
    engine = ClusterEngine(eps=0.3, min_samples=2)
    with pytest.raises(DataValidationError):
        engine.cluster_videos({})  # type: ignore[arg-type]


def test_entry_not_dict_raises():
    engine = ClusterEngine()
    with pytest.raises(DataValidationError):
        engine.cluster_videos([123])  # type: ignore[list-item]


def test_missing_title_field_raises():
    engine = ClusterEngine()
    with pytest.raises(DataValidationError):
        engine.cluster_videos([{"not_title": "x"}])


def test_no_valid_titles_returns_noise_only():
    engine = ClusterEngine()
    result = engine.cluster_videos(
        [
            {"title": "   "},
            {"title": "\n\t"},
        ]
    )
    assert result["cluster_info"]["total_clusters"] == 0
    assert result["cluster_info"]["noise_points"] == 2
    assert result["metadata"]["warning"] == "No valid titles for clustering"


def test_tfidf_vectorization_failure_raises_clustering_error():
    engine = ClusterEngine()
    # Titles that are only stopwords will be removed by TfidfVectorizer(stop_words='english')
    # This triggers ValueError: empty vocabulary; perhaps the documents only contain stop words
    entries = [
        {"title": "the and is"},
        {"title": "on in at"},
        {"title": "a an the"},
    ]
    with pytest.raises(ClusteringError) as ei:
        engine.cluster_videos(entries)
    assert "TF-IDF vectorization failed" in str(ei.value)
