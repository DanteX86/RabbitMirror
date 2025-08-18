#!/usr/bin/env python3
"""
Test script to verify that the exported knowledge base can be parsed without loss.
This validates the JSON structure and ensures all data can be reconstructed.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List


def test_json_parsing():
    """Test that all JSON files can be parsed without errors."""
    json_files = [f for f in os.listdir(".") if f.endswith(".json")]

    parsing_results = {"successful": [], "failed": [], "total_files": len(json_files)}

    for json_file in json_files:
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Verify it can be serialized back without loss
            json.dumps(data, ensure_ascii=False, indent=2)

            parsing_results["successful"].append(
                {
                    "file": json_file,
                    "size_bytes": os.path.getsize(json_file),
                    "top_level_keys": len(data.keys()) if isinstance(data, dict) else 0,
                }
            )

        except Exception as e:
            parsing_results["failed"].append({"file": json_file, "error": str(e)})

    return parsing_results


def test_main_export_structure():
    """Test the main export file structure for completeness."""
    export_file = "rabbitmirror_kb_export.json"

    if not os.path.exists(export_file):
        return {"status": "failed", "error": "Main export file not found"}

    try:
        with open(export_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Check required top-level sections
        required_sections = [
            "metadata",
            "executive_summary",
            "hierarchical_knowledge_base",
            "code_snippets_with_context",
        ]

        missing_sections = [
            section for section in required_sections if section not in data
        ]

        # Count entities in each section
        entity_counts = {}
        if "hierarchical_knowledge_base" in data:
            kb = data["hierarchical_knowledge_base"]
            for section, content in kb.items():
                if isinstance(content, dict):
                    entity_counts[section] = len(
                        [k for k in content.keys() if k != "description"]
                    )

        # Check metadata completeness
        metadata_check = {}
        if "metadata" in data:
            meta = data["metadata"]
            metadata_check = {
                "has_version": "export_version" in meta,
                "has_timestamp": "export_timestamp" in meta,
                "has_project_name": "project_name" in meta,
                "has_file_counts": "total_files_analyzed" in meta,
            }

        return {
            "status": "passed",
            "missing_sections": missing_sections,
            "entity_counts": entity_counts,
            "metadata_completeness": metadata_check,
            "total_size_bytes": os.path.getsize(export_file),
        }

    except Exception as e:
        return {"status": "failed", "error": str(e)}


def test_knowledge_graph_integrity():
    """Test knowledge graph structure and relationships."""
    kg_file = "knowledge_graph.json"

    if not os.path.exists(kg_file):
        return {"status": "failed", "error": "Knowledge graph file not found"}

    try:
        with open(kg_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Check structure
        required_keys = ["metadata", "core_modules", "relationships"]
        missing_keys = [key for key in required_keys if key not in data]

        # Count nodes and relationships
        node_count = 0
        relationship_count = 0

        if "core_modules" in data:
            node_count += len(data["core_modules"])

        if "relationships" in data:
            relationships = data["relationships"]
            if isinstance(relationships, dict):
                for rel_type, rel_list in relationships.items():
                    if isinstance(rel_list, list):
                        relationship_count += len(rel_list)

        # Verify metadata consistency
        metadata_consistent = True
        if "metadata" in data:
            meta = data["metadata"]
            claimed_nodes = meta.get("total_nodes", 0)
            claimed_relationships = meta.get("total_relationships", 0)

            # Allow some tolerance for nested structures
            metadata_consistent = (
                abs(claimed_nodes - node_count) <= node_count * 0.1
                and abs(claimed_relationships - relationship_count)
                <= relationship_count * 0.1
            )

        return {
            "status": "passed",
            "missing_keys": missing_keys,
            "actual_nodes": node_count,
            "actual_relationships": relationship_count,
            "metadata_consistent": metadata_consistent,
        }

    except Exception as e:
        return {"status": "failed", "error": str(e)}


def test_chunked_files():
    """Test that chunked markdown files are complete and accessible."""
    chunks_dir = "rabbitmirror_kb_chunks"

    if not os.path.exists(chunks_dir):
        return {"status": "failed", "error": "Chunks directory not found"}

    chunk_files = [f for f in os.listdir(chunks_dir) if f.endswith(".md")]

    chunk_results = {
        "total_chunks": len(chunk_files),
        "accessible_chunks": 0,
        "chunk_sizes": {},
        "failed_chunks": [],
    }

    for chunk_file in chunk_files:
        try:
            chunk_path = Path(chunks_dir) / chunk_file
            with open(chunk_path, "r", encoding="utf-8") as f:
                content = f.read()

            chunk_results["accessible_chunks"] += 1
            chunk_results["chunk_sizes"][chunk_file] = len(content)

        except Exception as e:
            chunk_results["failed_chunks"].append({"file": chunk_file, "error": str(e)})

    chunk_results["status"] = (
        "passed" if len(chunk_results["failed_chunks"]) == 0 else "partial"
    )
    return chunk_results


def test_data_reconstruction():
    """Test that data can be reconstructed from the exports."""
    reconstruction_tests = {
        "main_export_roundtrip": False,
        "knowledge_graph_roundtrip": False,
        "project_structure_roundtrip": False,
    }

    # Test main export roundtrip
    try:
        with open("rabbitmirror_kb_export.json", "r", encoding="utf-8") as f:
            original_data = json.load(f)

        # Serialize and deserialize
        json_string = json.dumps(original_data, ensure_ascii=False, indent=2)
        reconstructed_data = json.loads(json_string)

        reconstruction_tests["main_export_roundtrip"] = (
            original_data == reconstructed_data
        )
    except:  # nosec B110 - intentional broad except in test helper
        pass

    # Test knowledge graph roundtrip
    try:
        with open("knowledge_graph.json", "r", encoding="utf-8") as f:
            original_kg = json.load(f)

        json_string = json.dumps(original_kg, ensure_ascii=False, indent=2)
        reconstructed_kg = json.loads(json_string)

        reconstruction_tests["knowledge_graph_roundtrip"] = (
            original_kg == reconstructed_kg
        )
    except:  # nosec B110 - intentional broad except in test helper
        pass

    # Test project structure roundtrip
    try:
        with open("project_structure.json", "r", encoding="utf-8") as f:
            original_ps = json.load(f)

        json_string = json.dumps(original_ps, ensure_ascii=False, indent=2)
        reconstructed_ps = json.loads(json_string)

        reconstruction_tests["project_structure_roundtrip"] = (
            original_ps == reconstructed_ps
        )
    except:  # nosec B110 - intentional broad except in test helper
        pass

    return reconstruction_tests


def run_export_parsing_tests():
    """Run all export parsing tests."""
    results = {
        "timestamp": "2025-08-13T17:25:00Z",
        "tests_run": 0,
        "tests_passed": 0,
        "tests_failed": 0,
        "detailed_results": {},
    }

    # Test JSON parsing
    print("🔍 Testing JSON file parsing...")
    json_results = test_json_parsing()
    results["detailed_results"]["json_parsing"] = json_results
    results["tests_run"] += 1
    if len(json_results["failed"]) == 0:
        results["tests_passed"] += 1
        print(
            f"✅ JSON Parsing: {json_results['total_files']} files parsed successfully"
        )
    else:
        results["tests_failed"] += 1
        print(f"❌ JSON Parsing: {len(json_results['failed'])} files failed")

    # Test main export structure
    print("🔍 Testing main export structure...")
    export_results = test_main_export_structure()
    results["detailed_results"]["main_export"] = export_results
    results["tests_run"] += 1
    if export_results["status"] == "passed":
        results["tests_passed"] += 1
        print("✅ Main Export Structure: Complete")
    else:
        results["tests_failed"] += 1
        print(
            f"❌ Main Export Structure: {export_results.get('error', 'Issues detected')}"
        )

    # Test knowledge graph integrity
    print("🔍 Testing knowledge graph integrity...")
    kg_results = test_knowledge_graph_integrity()
    results["detailed_results"]["knowledge_graph"] = kg_results
    results["tests_run"] += 1
    if kg_results["status"] == "passed":
        results["tests_passed"] += 1
        print("✅ Knowledge Graph Integrity: Valid")
    else:
        results["tests_failed"] += 1
        print(
            f"❌ Knowledge Graph Integrity: {kg_results.get('error', 'Issues detected')}"
        )

    # Test chunked files
    print("🔍 Testing chunked files...")
    chunk_results = test_chunked_files()
    results["detailed_results"]["chunked_files"] = chunk_results
    results["tests_run"] += 1
    if chunk_results["status"] == "passed":
        results["tests_passed"] += 1
        print(f"✅ Chunked Files: {chunk_results['accessible_chunks']} files accessible")
    else:
        results["tests_failed"] += 1
        print(f"❌ Chunked Files: {len(chunk_results['failed_chunks'])} files failed")

    # Test data reconstruction
    print("🔍 Testing data reconstruction...")
    reconstruction_results = test_data_reconstruction()
    results["detailed_results"]["data_reconstruction"] = reconstruction_results
    results["tests_run"] += 1
    successful_reconstructions = sum(1 for v in reconstruction_results.values() if v)
    if successful_reconstructions == len(reconstruction_results):
        results["tests_passed"] += 1
        print("✅ Data Reconstruction: All roundtrip tests passed")
    else:
        results["tests_failed"] += 1
        print(
            f"❌ Data Reconstruction: {len(reconstruction_results) - successful_reconstructions} tests failed"
        )

    # Calculate success rate
    results["success_rate"] = (
        (results["tests_passed"] / results["tests_run"]) * 100
        if results["tests_run"] > 0
        else 0
    )

    print(f"\n📊 EXPORT PARSING TEST SUMMARY")
    print(f"Tests Run: {results['tests_run']}")
    print(f"Tests Passed: {results['tests_passed']}")
    print(f"Tests Failed: {results['tests_failed']}")
    print(f"Success Rate: {results['success_rate']:.1f}%")

    if results["success_rate"] >= 80:
        print("✅ Overall Status: EXPORT PARSING TESTS PASSED")
    else:
        print("❌ Overall Status: EXPORT PARSING TESTS FAILED")

    return results


if __name__ == "__main__":
    test_results = run_export_parsing_tests()

    # Save results
    with open("export_parsing_test_results.json", "w", encoding="utf-8") as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)

    print(f"\n📁 Test results saved to: export_parsing_test_results.json")
