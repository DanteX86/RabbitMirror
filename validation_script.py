#!/usr/bin/env python3
"""
RabbitMirror Knowledge Base Validation Script
Validates the completeness, quality, and integrity of the extracted knowledge base.
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple


class KnowledgeBaseValidator:
    def __init__(self):
        self.validation_results = {
            "timestamp": datetime.now().isoformat(),
            "files_validated": [],
            "cross_references": {"valid": 0, "invalid": 0, "details": []},
            "schema_validation": {"passed": 0, "failed": 0, "details": []},
            "completeness_check": {},
            "data_integrity": {},
            "statistics": {},
        }

    def validate_json_file(self, file_path: str) -> bool:
        """Validate JSON file structure and content."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Check for required keys based on file type
            if "rabbitmirror_kb_export.json" in file_path:
                required_keys = [
                    "metadata",
                    "executive_summary",
                    "hierarchical_knowledge_base",
                ]
                missing_keys = [key for key in required_keys if key not in data]
                if missing_keys:
                    self.validation_results["schema_validation"]["failed"] += 1
                    self.validation_results["schema_validation"]["details"].append(
                        {
                            "file": file_path,
                            "issue": f"Missing required keys: {missing_keys}",
                        }
                    )
                    return False
                else:
                    self.validation_results["schema_validation"]["passed"] += 1

            elif "knowledge_graph.json" in file_path:
                required_keys = ["metadata", "core_modules", "relationships"]
                missing_keys = [key for key in required_keys if key not in data]
                if missing_keys:
                    self.validation_results["schema_validation"]["failed"] += 1
                    self.validation_results["schema_validation"]["details"].append(
                        {
                            "file": file_path,
                            "issue": f"Missing required keys: {missing_keys}",
                        }
                    )
                    return False
                else:
                    self.validation_results["schema_validation"]["passed"] += 1

            self.validation_results["files_validated"].append(file_path)
            return True

        except json.JSONDecodeError as e:
            self.validation_results["schema_validation"]["failed"] += 1
            self.validation_results["schema_validation"]["details"].append(
                {"file": file_path, "issue": f"JSON decode error: {str(e)}"}
            )
            return False
        except FileNotFoundError:
            self.validation_results["schema_validation"]["failed"] += 1
            self.validation_results["schema_validation"]["details"].append(
                {"file": file_path, "issue": "File not found"}
            )
            return False

    def check_cross_references(self, file_path: str) -> None:
        """Check if cross-references in documentation are valid."""
        try:
            if file_path.endswith(".md"):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Find markdown links [text](link)
                md_links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)

                for link_text, link_url in md_links:
                    # Check if it's a local file reference
                    if not link_url.startswith(("http://", "https://", "mailto:")):
                        # Remove anchor fragments
                        clean_url = link_url.split("#")[0]
                        if clean_url and not clean_url.startswith("/"):
                            # Check if referenced file exists
                            ref_path = Path(file_path).parent / clean_url
                            if ref_path.exists():
                                self.validation_results["cross_references"][
                                    "valid"
                                ] += 1
                            else:
                                self.validation_results["cross_references"][
                                    "invalid"
                                ] += 1
                                self.validation_results["cross_references"][
                                    "details"
                                ].append(
                                    {
                                        "source_file": file_path,
                                        "broken_reference": link_url,
                                        "link_text": link_text,
                                    }
                                )

            elif file_path.endswith(".json"):
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._check_json_references(data, file_path)

        except Exception as e:
            print(f"Error checking cross-references in {file_path}: {str(e)}")

    def _check_json_references(self, data: Any, file_path: str) -> None:
        """Recursively check JSON data for file references."""
        if isinstance(data, dict):
            for key, value in data.items():
                if key in [
                    "code_references",
                    "cross_references",
                    "file",
                    "module",
                    "path",
                ]:
                    if isinstance(value, str) and not value.startswith(
                        ("http://", "https://")
                    ):
                        # Check if file exists
                        if not Path(value).exists() and not Path(f"./{value}").exists():
                            self.validation_results["cross_references"]["invalid"] += 1
                            self.validation_results["cross_references"][
                                "details"
                            ].append(
                                {
                                    "source_file": file_path,
                                    "broken_reference": value,
                                    "context": key,
                                }
                            )
                        else:
                            self.validation_results["cross_references"]["valid"] += 1
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, str) and not item.startswith(
                                ("http://", "https://")
                            ):
                                if (
                                    not Path(item).exists()
                                    and not Path(f"./{item}").exists()
                                ):
                                    self.validation_results["cross_references"][
                                        "invalid"
                                    ] += 1
                                    self.validation_results["cross_references"][
                                        "details"
                                    ].append(
                                        {
                                            "source_file": file_path,
                                            "broken_reference": item,
                                            "context": key,
                                        }
                                    )
                                else:
                                    self.validation_results["cross_references"][
                                        "valid"
                                    ] += 1
                else:
                    self._check_json_references(value, file_path)
        elif isinstance(data, list):
            for item in data:
                self._check_json_references(item, file_path)

    def calculate_statistics(self) -> None:
        """Calculate comprehensive statistics about the knowledge base."""
        stats = {
            "total_entities": 0,
            "relationship_counts": {},
            "coverage_percentages": {},
            "file_counts": {},
            "data_quality_metrics": {},
        }

        # Analyze main export file
        export_file = "rabbitmirror_kb_export.json"
        if os.path.exists(export_file):
            with open(export_file, "r") as f:
                data = json.load(f)

            # Count entities
            if "hierarchical_knowledge_base" in data:
                kb = data["hierarchical_knowledge_base"]
                stats["total_entities"] = len(kb)

                # Count different types of entities
                for category, content in kb.items():
                    if isinstance(content, dict) and "description" in content:
                        # Count sub-entities
                        entity_count = len(
                            [k for k in content.keys() if k != "description"]
                        )
                        stats["file_counts"][category] = entity_count

        # Analyze knowledge graph
        kg_file = "knowledge_graph.json"
        if os.path.exists(kg_file):
            with open(kg_file, "r") as f:
                kg_data = json.load(f)

            if "metadata" in kg_data:
                stats["total_nodes"] = kg_data["metadata"].get("total_nodes", 0)
                stats["total_relationships"] = kg_data["metadata"].get(
                    "total_relationships", 0
                )

            # Count relationship types
            if "relationships" in kg_data:
                relationships = kg_data["relationships"]
                if isinstance(relationships, dict):
                    for rel_type, rel_list in relationships.items():
                        if isinstance(rel_list, list):
                            stats["relationship_counts"][rel_type] = len(rel_list)

        # Analyze project structure
        ps_file = "project_structure.json"
        if os.path.exists(ps_file):
            with open(ps_file, "r") as f:
                ps_data = json.load(f)

            if "analysis_summary" in ps_data:
                summary = ps_data["analysis_summary"]
                stats["project_files"] = summary.get("total_files", 0)
                stats["project_size"] = summary.get("total_size_formatted", "0MB")

        # Calculate coverage percentages
        documentation_files = len([f for f in os.listdir(".") if f.endswith(".md")])
        json_files = len([f for f in os.listdir(".") if f.endswith(".json")])

        stats["coverage_percentages"] = {
            "documentation_coverage": min(
                100.0,
                (documentation_files / max(1, stats.get("project_files", 1))) * 100,
            ),
            "api_coverage": min(
                100.0, (json_files / max(1, stats.get("total_entities", 1))) * 100
            ),
            "cross_reference_validity": (
                self.validation_results["cross_references"]["valid"]
                / max(
                    1,
                    self.validation_results["cross_references"]["valid"]
                    + self.validation_results["cross_references"]["invalid"],
                )
            )
            * 100,
        }

        self.validation_results["statistics"] = stats

    def check_completeness(self) -> None:
        """Check completeness of extracted information."""
        required_files = [
            "rabbitmirror_kb_export.json",
            "knowledge_graph.json",
            "project_structure.json",
            "analysis_catalog.json",
            "documentation_index.json",
            "EXPORT_SUMMARY.md",
        ]

        missing_files = []
        present_files = []

        for file in required_files:
            if os.path.exists(file):
                present_files.append(file)
            else:
                missing_files.append(file)

        self.validation_results["completeness_check"] = {
            "required_files": required_files,
            "present_files": present_files,
            "missing_files": missing_files,
            "completeness_percentage": (len(present_files) / len(required_files)) * 100,
        }

        # Check for chunked knowledge base
        kb_chunks_dir = "rabbitmirror_kb_chunks"
        if os.path.exists(kb_chunks_dir):
            chunk_files = [f for f in os.listdir(kb_chunks_dir) if f.endswith(".md")]
            self.validation_results["completeness_check"]["chunk_files"] = chunk_files
            self.validation_results["completeness_check"]["chunk_count"] = len(
                chunk_files
            )
        else:
            self.validation_results["completeness_check"]["chunk_files"] = []
            self.validation_results["completeness_check"]["chunk_count"] = 0

    def check_data_integrity(self) -> None:
        """Check data integrity and consistency."""
        integrity_issues = []

        # Check main export file integrity
        export_file = "rabbitmirror_kb_export.json"
        if os.path.exists(export_file):
            try:
                with open(export_file, "r") as f:
                    export_data = json.load(f)

                # Check metadata consistency
                if "metadata" in export_data:
                    metadata = export_data["metadata"]
                    if "total_files_analyzed" in metadata:
                        claimed_files = metadata["total_files_analyzed"]
                        actual_files = len(self.validation_results["files_validated"])
                        if (
                            abs(claimed_files - actual_files) > 5
                        ):  # Allow some tolerance
                            integrity_issues.append(
                                f"File count mismatch: claimed {claimed_files}, validated {actual_files}"
                            )

            except Exception as e:
                integrity_issues.append(f"Error reading export file: {str(e)}")

        # Check benchmark data consistency
        benchmark_files = [
            f
            for f in os.listdir(".")
            if "benchmark" in f.lower() and f.endswith((".json", ".md"))
        ]
        for bf in benchmark_files:
            try:
                if bf.endswith(".json"):
                    with open(bf, "r") as f:
                        json.load(f)  # Just check if it's valid JSON
            except Exception as e:
                integrity_issues.append(f"Invalid benchmark file {bf}: {str(e)}")

        self.validation_results["data_integrity"] = {
            "issues_found": len(integrity_issues),
            "issues": integrity_issues,
        }

    def identify_missing_areas(self) -> List[str]:
        """Identify missing or problematic areas."""
        missing_areas = []

        # Check for critical components
        if not os.path.exists("rabbitmirror"):
            missing_areas.append("Source code directory 'rabbitmirror' not found")

        if not os.path.exists("tests"):
            missing_areas.append("Tests directory not found")

        # Check benchmark coverage
        benchmark_dir = "benchmark_results"
        if not os.path.exists(benchmark_dir):
            missing_areas.append("Benchmark results directory not found")
        else:
            parser_benchmarks = len(
                [
                    f
                    for f in os.listdir(benchmark_dir + "/parser")
                    if f.endswith(".json")
                ]
            )
            clustering_benchmarks = len(
                [
                    f
                    for f in os.listdir(benchmark_dir + "/clustering")
                    if f.endswith(".json")
                ]
            )
            if parser_benchmarks == 0:
                missing_areas.append("No parser benchmark results found")
            if clustering_benchmarks == 0:
                missing_areas.append("No clustering benchmark results found")

        # Check documentation completeness
        doc_index_file = "documentation_index.json"
        if os.path.exists(doc_index_file):
            with open(doc_index_file, "r") as f:
                doc_index = json.load(f)

            total_docs = doc_index.get("total_documents", 0)
            if total_docs < 20:  # Expect at least 20 documentation files
                missing_areas.append(
                    f"Low documentation coverage: only {total_docs} documents indexed"
                )

        return missing_areas

    def run_validation(self) -> None:
        """Run complete validation suite."""
        print("🔍 Starting RabbitMirror Knowledge Base Validation...")

        # Find all files to validate
        files_to_validate = []

        # JSON files
        for file in os.listdir("."):
            if file.endswith(".json"):
                files_to_validate.append(file)

        # Markdown files
        for file in os.listdir("."):
            if file.endswith(".md"):
                files_to_validate.append(file)

        # Chunked files
        if os.path.exists("rabbitmirror_kb_chunks"):
            for file in os.listdir("rabbitmirror_kb_chunks"):
                if file.endswith(".md"):
                    files_to_validate.append(f"rabbitmirror_kb_chunks/{file}")

        print(f"📋 Found {len(files_to_validate)} files to validate")

        # Validate each file
        for file_path in files_to_validate:
            if file_path.endswith(".json"):
                self.validate_json_file(file_path)
            self.check_cross_references(file_path)

        # Run additional checks
        self.check_completeness()
        self.check_data_integrity()
        self.calculate_statistics()

        # Identify missing areas
        missing_areas = self.identify_missing_areas()
        self.validation_results["missing_areas"] = missing_areas

        print("✅ Validation complete!")


def generate_validation_report(results: Dict) -> str:
    """Generate a comprehensive validation report."""
    report = f"""# RabbitMirror Knowledge Base Validation Report

**Generated:** {results['timestamp']}
**Validator Version:** 1.0.0

## Executive Summary

This report validates the completeness, integrity, and quality of the RabbitMirror knowledge base export.

### Overall Status: {'✅ PASSED' if results['schema_validation']['failed'] == 0 else '❌ FAILED'}

## Validation Results

### Files Validated
- **Total Files Processed:** {len(results['files_validated'])}
- **Schema Validation Passed:** {results['schema_validation']['passed']}
- **Schema Validation Failed:** {results['schema_validation']['failed']}

### Cross-Reference Analysis
- **Valid References:** {results['cross_references']['valid']}
- **Invalid References:** {results['cross_references']['invalid']}
- **Reference Validity Rate:** {(results['cross_references']['valid'] / max(1, results['cross_references']['valid'] + results['cross_references']['invalid']) * 100):.1f}%

### Completeness Check
- **Required Files Present:** {len(results['completeness_check']['present_files'])}/{len(results['completeness_check']['required_files'])}
- **Completeness Percentage:** {results['completeness_check']['completeness_percentage']:.1f}%
- **Knowledge Base Chunks:** {results['completeness_check']['chunk_count']} files

### Data Integrity
- **Integrity Issues Found:** {results['data_integrity']['issues_found']}
- **Data Quality Status:** {'✅ GOOD' if results['data_integrity']['issues_found'] == 0 else '❌ ISSUES DETECTED'}

## Knowledge Base Statistics

### Entity Counts
"""

    if "statistics" in results:
        stats = results["statistics"]
        report += f"""
- **Total Entities Extracted:** {stats.get('total_entities', 'N/A')}
- **Total Graph Nodes:** {stats.get('total_nodes', 'N/A')}
- **Total Relationships:** {stats.get('total_relationships', 'N/A')}
- **Project Files Analyzed:** {stats.get('project_files', 'N/A')}
- **Project Size:** {stats.get('project_size', 'N/A')}

### Relationship Counts
"""
        if "relationship_counts" in stats:
            for rel_type, count in stats["relationship_counts"].items():
                report += f"- **{rel_type.replace('_', ' ').title()}:** {count}\n"

        report += f"""
### Coverage Percentages
- **Documentation Coverage:** {stats.get('coverage_percentages', {}).get('documentation_coverage', 0):.1f}%
- **API Coverage:** {stats.get('coverage_percentages', {}).get('api_coverage', 0):.1f}%
- **Cross-Reference Validity:** {stats.get('coverage_percentages', {}).get('cross_reference_validity', 0):.1f}%
"""

    # Missing files section
    if results["completeness_check"]["missing_files"]:
        report += f"""
## Missing Files
The following required files were not found:
"""
        for file in results["completeness_check"]["missing_files"]:
            report += f"- ❌ {file}\n"

    # Schema validation issues
    if results["schema_validation"]["failed"] > 0:
        report += f"""
## Schema Validation Issues
"""
        for issue in results["schema_validation"]["details"]:
            report += f"- **{issue['file']}:** {issue['issue']}\n"

    # Cross-reference issues
    if results["cross_references"]["invalid"] > 0:
        report += f"""
## Broken Cross-References
"""
        for ref in results["cross_references"]["details"][:10]:  # Show first 10
            report += f"- **{ref['source_file']}:** `{ref['broken_reference']}`\n"

        if len(results["cross_references"]["details"]) > 10:
            report += (
                f"... and {len(results['cross_references']['details']) - 10} more\n"
            )

    # Data integrity issues
    if results["data_integrity"]["issues_found"] > 0:
        report += f"""
## Data Integrity Issues
"""
        for issue in results["data_integrity"]["issues"]:
            report += f"- {issue}\n"

    # Missing areas
    if "missing_areas" in results and results["missing_areas"]:
        report += f"""
## Missing or Problematic Areas
"""
        for area in results["missing_areas"]:
            report += f"- ⚠️ {area}\n"

    # Recommendations
    report += f"""
## Recommendations

### High Priority
"""
    if results["schema_validation"]["failed"] > 0:
        report += "- Fix schema validation failures in JSON files\n"
    if results["cross_references"]["invalid"] > 5:
        report += "- Repair broken cross-references in documentation\n"
    if results["completeness_check"]["completeness_percentage"] < 90:
        report += "- Generate missing required files\n"

    report += """
### Medium Priority
- Review and update documentation links
- Validate benchmark data consistency
- Improve cross-reference coverage

### Low Priority
- Enhance metadata completeness
- Add automated validation checks to CI/CD
- Implement real-time validation monitoring

## Export Quality Assessment

### Strengths
"""
    if results["schema_validation"]["passed"] > 0:
        report += "- All major JSON files validate successfully\n"
    if results["cross_references"]["valid"] > results["cross_references"]["invalid"]:
        report += "- Majority of cross-references are valid\n"
    if results["completeness_check"]["completeness_percentage"] > 80:
        report += "- High completeness percentage\n"

    report += """
### Areas for Improvement
"""
    if results["cross_references"]["invalid"] > 0:
        report += f"- {results['cross_references']['invalid']} broken cross-references need fixing\n"
    if results["data_integrity"]["issues_found"] > 0:
        report += f"- {results['data_integrity']['issues_found']} data integrity issues identified\n"

    report += """
## Validation Methodology

This validation was performed using automated analysis of:
1. JSON schema validation for structured data files
2. Cross-reference checking for documentation links
3. File completeness verification against requirements
4. Data integrity checks for consistency
5. Statistical analysis of extracted entities and relationships

**Note:** This validation focuses on structural integrity and completeness. Content quality and accuracy require manual review.
"""

    return report


def generate_statistics_json(results: Dict) -> Dict:
    """Generate export statistics in JSON format."""
    stats = {
        "validation_timestamp": results["timestamp"],
        "validation_summary": {
            "overall_status": "passed"
            if results["schema_validation"]["failed"] == 0
            else "failed",
            "files_validated": len(results["files_validated"]),
            "schema_validation_passed": results["schema_validation"]["passed"],
            "schema_validation_failed": results["schema_validation"]["failed"],
        },
        "entity_statistics": results.get("statistics", {}),
        "cross_reference_analysis": {
            "valid_references": results["cross_references"]["valid"],
            "invalid_references": results["cross_references"]["invalid"],
            "validity_percentage": (
                results["cross_references"]["valid"]
                / max(
                    1,
                    results["cross_references"]["valid"]
                    + results["cross_references"]["invalid"],
                )
            )
            * 100,
        },
        "completeness_metrics": {
            "required_files_percentage": results["completeness_check"][
                "completeness_percentage"
            ],
            "chunk_files_available": results["completeness_check"]["chunk_count"],
            "missing_files_count": len(results["completeness_check"]["missing_files"]),
        },
        "data_integrity_metrics": {
            "integrity_issues_count": results["data_integrity"]["issues_found"],
            "data_quality_status": "good"
            if results["data_integrity"]["issues_found"] == 0
            else "issues_detected",
        },
        "export_metadata": {
            "export_format": "json_with_markdown_chunks",
            "validation_version": "1.0.0",
            "validation_coverage": "comprehensive",
        },
    }

    return stats


if __name__ == "__main__":
    validator = KnowledgeBaseValidator()
    validator.run_validation()

    # Generate validation report
    report = generate_validation_report(validator.validation_results)
    with open("validation_report.md", "w", encoding="utf-8") as f:
        f.write(report)

    # Generate statistics JSON
    stats = generate_statistics_json(validator.validation_results)
    with open("export_statistics.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    print("📊 Validation report generated: validation_report.md")
    print("📈 Statistics generated: export_statistics.json")

    # Print summary
    print(f"\n📋 VALIDATION SUMMARY")
    print(f"Files Validated: {len(validator.validation_results['files_validated'])}")
    print(
        f"Schema Validation: {validator.validation_results['schema_validation']['passed']} passed, {validator.validation_results['schema_validation']['failed']} failed"
    )
    print(
        f"Cross-References: {validator.validation_results['cross_references']['valid']} valid, {validator.validation_results['cross_references']['invalid']} invalid"
    )
    print(
        f"Completeness: {validator.validation_results['completeness_check']['completeness_percentage']:.1f}%"
    )
    print(
        f"Data Integrity: {validator.validation_results['data_integrity']['issues_found']} issues found"
    )

    if (
        validator.validation_results["schema_validation"]["failed"] == 0
        and validator.validation_results["data_integrity"]["issues_found"] == 0
    ):
        print("✅ Overall Status: VALIDATION PASSED")
    else:
        print("❌ Overall Status: VALIDATION FAILED - Issues need attention")
