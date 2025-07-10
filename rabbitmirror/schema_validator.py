#!/usr/bin/env python3

from typing import Any, Dict, List, Optional

import jsonschema

from .symbolic_logger import SymbolicLogger


class SchemaValidator:
    """Validates JSON data against predefined schemas for RabbitMirror data types."""

    def __init__(self):
        self.schemas = self._load_schemas()
        self.logger = SymbolicLogger()

    def _load_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Load and return JSON schemas for different data types."""
        return {
            "watch_history": {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "title": "YouTube Watch History Schema",
                "type": "object",
                "properties": {
                    "entries": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["timestamp", "title"],
                            "properties": {
                                "timestamp": {
                                    "type": "string",
                                    "description": "ISO timestamp when video was watched",
                                },
                                "title": {
                                    "type": "string",
                                    "description": "Video title",
                                    "minLength": 1,
                                },
                                "category": {
                                    "type": "string",
                                    "description": "Video category",
                                },
                                "videoId": {
                                    "type": "string",
                                    "description": "YouTube video ID",
                                },
                                "channelId": {
                                    "type": "string",
                                    "description": "YouTube channel ID",
                                },
                                "channelName": {
                                    "type": "string",
                                    "description": "Channel name",
                                },
                                "duration": {
                                    "type": "number",
                                    "description": "Video duration in seconds",
                                    "minimum": 0,
                                },
                            },
                        },
                    },
                    "metadata": {
                        "type": "object",
                        "properties": {
                            "total_entries": {"type": "integer", "minimum": 0},
                            "date_range": {
                                "type": "object",
                                "properties": {
                                    "start": {"type": "string"},
                                    "end": {"type": "string"},
                                },
                            },
                            "export_timestamp": {"type": "string"},
                        },
                    },
                },
                "required": ["entries"],
            },
            "cluster_analysis": {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "title": "Cluster Analysis Results Schema",
                "type": "object",
                "properties": {
                    "clusters": {
                        "type": "object",
                        "properties": {
                            "cluster_labels": {
                                "type": "array",
                                "items": {"type": "integer", "minimum": -1},
                                "description": "Cluster labels for each data point (-1 for noise)",
                            },
                            "features": {
                                "type": "array",
                                "items": {"type": "array", "items": {"type": "number"}},
                                "description": "Feature vectors used for clustering",
                            },
                            "cluster_centers": {
                                "type": "array",
                                "items": {"type": "array", "items": {"type": "number"}},
                                "description": "Cluster center coordinates",
                            },
                            "num_clusters": {
                                "type": "integer",
                                "minimum": 0,
                                "description": "Number of clusters found",
                            },
                            "silhouette_score": {
                                "type": "number",
                                "minimum": -1,
                                "maximum": 1,
                                "description": "Silhouette analysis score",
                            },
                        },
                        "required": ["cluster_labels"],
                    },
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "eps": {"type": "number", "minimum": 0},
                            "min_samples": {"type": "integer", "minimum": 1},
                            "algorithm": {"type": "string"},
                        },
                    },
                },
                "required": ["clusters"],
            },
            "suppression_analysis": {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "title": "Suppression Analysis Results Schema",
                "type": "object",
                "properties": {
                    "suppression_results": {
                        "type": "object",
                        "properties": {
                            "suppression_scores": {
                                "type": "array",
                                "items": {"type": "number", "minimum": 0, "maximum": 1},
                                "description": "Suppression scores for content categories",
                            },
                            "baseline_period_days": {
                                "type": "integer",
                                "minimum": 1,
                                "description": "Baseline period in days",
                            },
                            "categories": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Content categories analyzed",
                            },
                            "suppression_threshold": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                                "description": "Threshold for significant suppression",
                            },
                        },
                        "required": ["suppression_scores"],
                    },
                    "analysis_metadata": {
                        "type": "object",
                        "properties": {
                            "total_entries_analyzed": {"type": "integer", "minimum": 0},
                            "analysis_timestamp": {"type": "string"},
                        },
                    },
                },
                "required": ["suppression_results"],
            },
            "pattern_analysis": {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "title": "Pattern Analysis Results Schema",
                "type": "object",
                "properties": {
                    "patterns": {
                        "type": "object",
                        "properties": {
                            "pattern_scores": {
                                "type": "array",
                                "items": {"type": "number", "minimum": 0, "maximum": 1},
                                "description": "Pattern detection confidence scores",
                            },
                            "detected_patterns": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "pattern_type": {"type": "string"},
                                        "confidence": {
                                            "type": "number",
                                            "minimum": 0,
                                            "maximum": 1,
                                        },
                                        "description": {"type": "string"},
                                        "affected_videos": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                        },
                                    },
                                    "required": ["pattern_type", "confidence"],
                                },
                            },
                            "similarity_threshold": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                            },
                        },
                        "required": ["pattern_scores"],
                    }
                },
                "required": ["patterns"],
            },
            "simulation_results": {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "title": "Profile Simulation Results Schema",
                "type": "object",
                "properties": {
                    "simulated_entries": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["timestamp", "title"],
                            "properties": {
                                "timestamp": {"type": "string"},
                                "title": {"type": "string"},
                                "category": {"type": "string"},
                                "confidence": {
                                    "type": "number",
                                    "minimum": 0,
                                    "maximum": 1,
                                },
                            },
                        },
                    },
                    "simulation_parameters": {
                        "type": "object",
                        "properties": {
                            "duration_days": {"type": "integer", "minimum": 1},
                            "profile_type": {"type": "string"},
                            "seed": {"type": "integer"},
                            "intensity": {"type": "number", "minimum": 0},
                        },
                    },
                },
                "required": ["simulated_entries"],
            },
        }

    def validate(self, data: Dict[str, Any], schema_type: str) -> bool:
        """Validate data against a specific schema type. Raise exception if invalid."""
        schema = self.schemas.get(schema_type)
        if not schema:
            raise ValueError(f"Schema not found for type: {schema_type}")

        jsonschema.validate(instance=data, schema=schema)
        self.logger.log_event(
            "validation_success",
            {"schema_type": schema_type, "data_size": len(str(data))},
        )
        return True

    def validate_with_details(
        self, data: Dict[str, Any], schema_type: str
    ) -> Dict[str, Any]:
        """Validate data and return detailed results including errors."""
        schema = self.schemas.get(schema_type)
        if not schema:
            return {
                "valid": False,
                "error": f"Schema not found for type: {schema_type}",
                "available_schemas": list(self.schemas.keys()),
            }

        try:
            jsonschema.validate(instance=data, schema=schema)
            return {
                "valid": True,
                "schema_type": schema_type,
                "message": "Data is valid",
            }
        except jsonschema.exceptions.ValidationError as e:
            return {
                "valid": False,
                "error": e.message,
                "path": list(e.absolute_path),
                "failed_value": e.instance,
                "schema_type": schema_type,
            }

    def get_available_schemas(self) -> List[str]:
        """Return list of available schema types."""
        return list(self.schemas.keys())

    def get_schema(self, schema_type: str) -> Optional[Dict[str, Any]]:
        """Get a specific schema by type."""
        return self.schemas.get(schema_type)

    def auto_detect_schema(self, data: Dict[str, Any]) -> Optional[str]:
        """Attempt to automatically detect the most appropriate schema for the data."""
        schema_scores = {}

        for schema_type in self.schemas.keys():
            try:
                self.validate(data, schema_type)
                schema_scores[schema_type] = 100  # Perfect match
            except (jsonschema.exceptions.ValidationError, ValueError):
                # Calculate partial match score based on structure
                score = self._calculate_structure_similarity(data, schema_type)
                if score > 0:
                    schema_scores[schema_type] = score

        if not schema_scores:
            return None

        # Return the schema with the highest score
        best_schema = max(schema_scores, key=schema_scores.get)
        return best_schema if schema_scores[best_schema] > 50 else None

    def _calculate_structure_similarity(
        self, data: Dict[str, Any], schema_type: str
    ) -> int:
        """Calculate how similar the data structure is to a given schema (0-100)."""
        schema = self.schemas.get(schema_type)
        if not schema:
            return 0

        score = 0
        max_score = 0

        # Check if required top-level properties exist
        required_props = schema.get("required", [])
        for prop in required_props:
            max_score += 20
            if prop in data:
                score += 20

        # Check if top-level properties match expected types
        properties = schema.get("properties", {})
        for prop, prop_schema in properties.items():
            max_score += 10
            if prop in data:
                expected_type = prop_schema.get("type")
                actual_value = data[prop]

                if self._matches_type(actual_value, expected_type):
                    score += 10
                else:
                    score += 5  # Partial credit for having the property

        return int((score / max_score * 100)) if max_score > 0 else 0

    def _matches_type(self, value: Any, expected_type: str) -> bool:
        """Check if a value matches the expected JSON schema type."""
        if expected_type == "string":
            return isinstance(value, str)
        elif expected_type == "number":
            return isinstance(value, (int, float))
        elif expected_type == "integer":
            return isinstance(value, int)
        elif expected_type == "boolean":
            return isinstance(value, bool)
        elif expected_type == "array":
            return isinstance(value, list)
        elif expected_type == "object":
            return isinstance(value, dict)
        elif expected_type == "null":
            return value is None
        return False
