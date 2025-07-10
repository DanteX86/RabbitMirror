import jsonschema
import pytest

from rabbitmirror.schema_validator import SchemaValidator


class TestSchemaValidator:
    """Test class for comprehensive schema validation functionality."""

    def test_initialization(self):
        """Test schema validator initialization."""
        validator = SchemaValidator()

        assert hasattr(validator, "schemas")
        assert hasattr(validator, "logger")
        assert isinstance(validator.schemas, dict)
        assert len(validator.schemas) > 0

    def test_available_schemas(self):
        """Test that all expected schemas are available."""
        validator = SchemaValidator()
        available_schemas = validator.get_available_schemas()

        expected_schemas = [
            "watch_history",
            "cluster_analysis",
            "suppression_analysis",
            "pattern_analysis",
            "simulation_results",
        ]

        for schema in expected_schemas:
            assert schema in available_schemas

    def test_valid_watch_history_data(self):
        """Test validation of valid watch history data."""
        validator = SchemaValidator()

        valid_data = {
            "entries": [
                {
                    "timestamp": "2025-07-10T12:00:00",
                    "title": "Python Tutorial",
                    "category": "Education",
                },
                {
                    "timestamp": "2025-07-10T13:00:00",
                    "title": "React Basics",
                    "category": "Programming",
                },
            ]
        }

        # Should not raise an exception
        result = validator.validate(valid_data, "watch_history")
        assert result is True

    def test_invalid_watch_history_data(self):
        """Test validation of invalid watch history data."""
        validator = SchemaValidator()

        invalid_data = {
            "entries": [
                {
                    "timestamp": "2025-07-10T12:00:00",
                    # Missing required 'title' field
                    "category": "Education",
                }
            ]
        }

        with pytest.raises(jsonschema.exceptions.ValidationError):
            validator.validate(invalid_data, "watch_history")

    def test_validate_with_details_success(self):
        """Test detailed validation with valid data."""
        validator = SchemaValidator()

        valid_data = {
            "clusters": {
                "cluster_labels": [0, 1, 0, 1],
                "features": [[1.0, 2.0], [1.5, 1.8]],
            }
        }

        result = validator.validate_with_details(valid_data, "cluster_analysis")

        assert result["valid"] is True
        assert result["schema_type"] == "cluster_analysis"
        assert "message" in result

    def test_validate_with_details_failure(self):
        """Test detailed validation with invalid data."""
        validator = SchemaValidator()

        invalid_data = {
            "clusters": {"cluster_labels": "invalid_format"}  # Should be array
        }

        result = validator.validate_with_details(invalid_data, "cluster_analysis")

        assert result["valid"] is False
        assert "error" in result
        assert result["schema_type"] == "cluster_analysis"

    def test_nonexistent_schema(self):
        """Test validation against non-existent schema."""
        validator = SchemaValidator()

        data = {"test": "data"}

        with pytest.raises(ValueError, match="Schema not found for type"):
            validator.validate(data, "nonexistent_schema")

    def test_auto_detect_schema_success(self):
        """Test automatic schema detection with valid data."""
        validator = SchemaValidator()

        watch_history_data = {
            "entries": [{"timestamp": "2025-07-10T12:00:00", "title": "Test Video"}]
        }

        detected_schema = validator.auto_detect_schema(watch_history_data)
        assert detected_schema == "watch_history"

    def test_auto_detect_schema_failure(self):
        """Test automatic schema detection with invalid data."""
        validator = SchemaValidator()

        invalid_data = {"random_field": "random_value", "another_field": 123}

        detected_schema = validator.auto_detect_schema(invalid_data)
        assert detected_schema is None

    def test_structure_similarity_calculation(self):
        """Test structure similarity calculation."""
        validator = SchemaValidator()

        # Data that partially matches watch_history schema
        partial_data = {"entries": "wrong_type"}  # Should be array

        similarity = validator._calculate_structure_similarity(
            partial_data, "watch_history"
        )
        assert isinstance(similarity, int)
        assert 0 <= similarity <= 100

    def test_type_matching(self):
        """Test the type matching utility method."""
        validator = SchemaValidator()

        # Test various type matches
        assert validator._matches_type("test", "string") is True
        assert validator._matches_type(123, "integer") is True
        assert validator._matches_type(123.45, "number") is True
        assert validator._matches_type(True, "boolean") is True
        assert validator._matches_type([1, 2, 3], "array") is True
        assert validator._matches_type({"key": "value"}, "object") is True
        assert validator._matches_type(None, "null") is True

        # Test type mismatches
        assert validator._matches_type(123, "string") is False
        assert validator._matches_type("test", "integer") is False
        assert validator._matches_type([1, 2, 3], "object") is False

    def test_get_schema(self):
        """Test getting specific schema by type."""
        validator = SchemaValidator()

        # Test getting existing schema
        schema = validator.get_schema("watch_history")
        assert schema is not None
        assert "type" in schema
        assert schema["type"] == "object"

        # Test getting non-existent schema
        schema = validator.get_schema("nonexistent")
        assert schema is None

    def test_suppression_analysis_schema(self):
        """Test suppression analysis specific schema validation."""
        validator = SchemaValidator()

        valid_suppression_data = {
            "suppression_results": {
                "suppression_scores": [0.1, 0.5, 0.9],
                "baseline_period_days": 30,
            }
        }

        result = validator.validate(valid_suppression_data, "suppression_analysis")
        assert result is True

    def test_pattern_analysis_schema(self):
        """Test pattern analysis specific schema validation."""
        validator = SchemaValidator()

        valid_pattern_data = {
            "patterns": {
                "pattern_scores": [0.2, 0.7, 0.9],
                "detected_patterns": [
                    {
                        "pattern_type": "repetitive_viewing",
                        "confidence": 0.85,
                        "description": "User shows repetitive viewing patterns",
                    }
                ],
            }
        }

        result = validator.validate(valid_pattern_data, "pattern_analysis")
        assert result is True

    def test_simulation_results_schema(self):
        """Test simulation results specific schema validation."""
        validator = SchemaValidator()

        valid_simulation_data = {
            "simulated_entries": [
                {
                    "timestamp": "2025-07-10T12:00:00",
                    "title": "Simulated Video",
                    "confidence": 0.9,
                }
            ],
            "simulation_parameters": {"duration_days": 7, "profile_type": "regular"},
        }

        result = validator.validate(valid_simulation_data, "simulation_results")
        assert result is True

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        validator = SchemaValidator()

        # Test with empty data
        empty_data = {}

        result = validator.validate_with_details(empty_data, "watch_history")
        assert result["valid"] is False

        # Test with minimal valid data
        minimal_data = {"entries": []}
        result = validator.validate_with_details(minimal_data, "watch_history")
        assert result["valid"] is True  # Empty array is valid

        # Test auto-detection with multiple matching schemas
        multi_match_data = {
            "entries": [],
            "clusters": {"cluster_labels": []},
            "patterns": {"pattern_scores": []},
        }

        detected = validator.auto_detect_schema(multi_match_data)
        # Should detect one of the matching schemas
        assert detected in ["watch_history", "cluster_analysis", "pattern_analysis"]
