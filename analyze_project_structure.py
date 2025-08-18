#!/usr/bin/env python3
"""
RabbitMirror Project Structure Analyzer
=======================================
Analyzes the entire RabbitMirror project directory to create:
1. Hierarchical JSON structure mapping all directories and files
2. File type categorization (Python modules, tests, docs, configs, data files)
3. Directory sizes and file counts for each component
4. Visual tree representation of the project structure

Outputs:
- project_structure.json
- project_tree.txt
"""

import hashlib
import json
import mimetypes
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple


class ProjectAnalyzer:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.file_categories = {
            "python_modules": [".py"],
            "tests": [],  # Will be determined by path patterns
            "documentation": [".md", ".rst", ".txt", ".doc", ".docx"],
            "configuration": [
                ".ini",
                ".cfg",
                ".conf",
                ".yaml",
                ".yml",
                ".json",
                ".toml",
            ],
            "web_files": [".html", ".css", ".js", ".jsx", ".ts", ".tsx"],
            "data_files": [".csv", ".json", ".xml", ".db", ".sqlite", ".sqlite3"],
            "images": [".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico"],
            "templates": [".jinja", ".jinja2", ".j2"],
            "shell_scripts": [".sh", ".bash", ".zsh", ".fish"],
            "requirements": [
                "requirements.txt",
                "requirements-dev.txt",
                "Pipfile",
                "poetry.lock",
            ],
            "build_files": ["Makefile", "setup.py", "pyproject.toml", "setup.cfg"],
            "version_control": [],  # Git files
            "cache_files": [],  # Cache directories
            "logs": [".log"],
            "other": [],
        }

    def get_file_size(self, file_path: Path) -> int:
        """Get file size in bytes, return 0 if file doesn't exist or is inaccessible."""
        try:
            return file_path.stat().st_size
        except (OSError, FileNotFoundError):
            return 0

    def get_directory_size(self, dir_path: Path) -> Tuple[int, int]:
        """Get total size in bytes and file count for a directory recursively."""
        total_size = 0
        file_count = 0

        try:
            for entry in dir_path.rglob("*"):
                if entry.is_file():
                    total_size += self.get_file_size(entry)
                    file_count += 1
        except (OSError, PermissionError):
            pass

        return total_size, file_count

    def categorize_file(self, file_path: Path) -> str:
        """Categorize a file based on its extension and path."""
        file_name = file_path.name.lower()
        file_suffix = file_path.suffix.lower()
        path_parts = [p.lower() for p in file_path.parts]

        # Special cases based on path
        if any("test" in part for part in path_parts):
            if file_suffix == ".py":
                return "tests"

        if any(part in [".git", ".github"] for part in path_parts):
            return "version_control"

        if any(
            part in ["__pycache__", ".pytest_cache", ".mypy_cache", "node_modules"]
            for part in path_parts
        ):
            return "cache_files"

        if "log" in path_parts or "logs" in path_parts:
            return "logs"

        # Check by filename first (for special files)
        if file_name in [
            "dockerfile",
            "makefile",
            "pipfile",
            "poetry.lock",
            "setup.py",
        ]:
            return "build_files"

        if file_name.startswith("requirements"):
            return "requirements"

        # Check by extension
        for category, extensions in self.file_categories.items():
            if file_suffix in extensions:
                return category

        # Default category
        return "other"

    def analyze_directory(
        self, dir_path: Path, max_depth: int = None, current_depth: int = 0
    ) -> Dict[str, Any]:
        """Recursively analyze directory structure."""
        if max_depth is not None and current_depth > max_depth:
            return None

        result = {
            "name": dir_path.name,
            "type": "directory",
            "path": str(dir_path.relative_to(self.project_path)),
            "children": [],
            "file_count": 0,
            "directory_count": 0,
            "total_size": 0,
            "file_categories": defaultdict(int),
            "depth": current_depth,
        }

        try:
            entries = sorted(
                dir_path.iterdir(), key=lambda x: (x.is_file(), x.name.lower())
            )

            for entry in entries:
                if entry.is_file():
                    file_size = self.get_file_size(entry)
                    category = self.categorize_file(entry)

                    file_info = {
                        "name": entry.name,
                        "type": "file",
                        "path": str(entry.relative_to(self.project_path)),
                        "size": file_size,
                        "category": category,
                        "extension": entry.suffix.lower(),
                        "depth": current_depth + 1,
                    }

                    result["children"].append(file_info)
                    result["file_count"] += 1
                    result["total_size"] += file_size
                    result["file_categories"][category] += 1

                elif entry.is_dir():
                    # Skip certain directories that might be too large or irrelevant
                    skip_dirs = {
                        ".git",
                        "__pycache__",
                        ".pytest_cache",
                        ".mypy_cache",
                        "node_modules",
                        "venv",
                        ".venv",
                        "env",
                        ".env",
                    }

                    if entry.name in skip_dirs:
                        # Still count them but don't recurse deeply
                        dir_size, dir_files = self.get_directory_size(entry)
                        dir_info = {
                            "name": entry.name,
                            "type": "directory",
                            "path": str(entry.relative_to(self.project_path)),
                            "children": [],
                            "file_count": dir_files,
                            "directory_count": 0,
                            "total_size": dir_size,
                            "file_categories": {
                                "cache_files"
                                if "cache" in entry.name
                                else "other": dir_files
                            },
                            "depth": current_depth + 1,
                            "skipped": True,
                        }
                        result["children"].append(dir_info)
                        result["directory_count"] += 1
                        result["total_size"] += dir_size
                        result["file_count"] += dir_files
                    else:
                        subdir_result = self.analyze_directory(
                            entry, max_depth, current_depth + 1
                        )
                        if subdir_result:
                            result["children"].append(subdir_result)
                            result["directory_count"] += (
                                1 + subdir_result["directory_count"]
                            )
                            result["file_count"] += subdir_result["file_count"]
                            result["total_size"] += subdir_result["total_size"]

                            # Merge file categories
                            for cat, count in subdir_result["file_categories"].items():
                                result["file_categories"][cat] += count

        except (OSError, PermissionError) as e:
            result["error"] = str(e)

        return result

    def format_size(self, size_bytes: int) -> str:
        """Format size in human readable format."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f}TB"

    def generate_tree_text(
        self, node: Dict[str, Any], prefix: str = "", is_last: bool = True
    ) -> str:
        """Generate a tree-like text representation."""
        result = []

        # Current node
        connector = "└── " if is_last else "├── "
        name = node["name"]

        if node["type"] == "directory":
            size_info = (
                f" ({self.format_size(node['total_size'])}, {node['file_count']} files)"
            )
            result.append(f"{prefix}{connector}{name}/{size_info}")

            # Add children
            children = node.get("children", [])
            if children:
                new_prefix = prefix + ("    " if is_last else "│   ")
                for i, child in enumerate(children):
                    child_is_last = i == len(children) - 1
                    result.append(
                        self.generate_tree_text(child, new_prefix, child_is_last)
                    )
        else:
            size_info = f" ({self.format_size(node['size'])}) [{node['category']}]"
            result.append(f"{prefix}{connector}{name}{size_info}")

        return "\n".join(result)

    def generate_summary_stats(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics."""
        total_files = structure["file_count"]
        total_size = structure["total_size"]
        file_categories = dict(structure["file_categories"])

        # Calculate percentages
        category_percentages = {}
        for category, count in file_categories.items():
            category_percentages[category] = {
                "count": count,
                "percentage": (count / total_files * 100) if total_files > 0 else 0,
            }

        return {
            "total_files": total_files,
            "total_directories": structure["directory_count"],
            "total_size_bytes": total_size,
            "total_size_formatted": self.format_size(total_size),
            "file_categories": category_percentages,
            "analysis_timestamp": __import__("datetime").datetime.now().isoformat(),
        }

    def analyze_project(self) -> Tuple[Dict[str, Any], str]:
        """Analyze the entire project and return structure data and tree text."""
        print("Starting project analysis...")
        print(f"Project path: {self.project_path}")
        print(
            f"Total project size: {self.format_size(self.get_directory_size(self.project_path)[0])}"
        )

        # Analyze structure
        structure = self.analyze_directory(self.project_path)

        # Generate summary
        summary = self.generate_summary_stats(structure)

        # Generate tree text
        tree_text = self.generate_tree_text(structure)

        # Create final structure with metadata
        final_structure = {
            "project_name": "RabbitMirror",
            "analysis_summary": summary,
            "directory_structure": structure,
        }

        return final_structure, tree_text


def main():
    """Main function to run the analysis."""
    project_path = "/Users/romulusaugustus/Documents/RabbitMirror"

    analyzer = ProjectAnalyzer(project_path)

    print("Analyzing RabbitMirror project structure...")
    structure, tree_text = analyzer.analyze_project()

    # Save JSON structure
    json_output_path = os.path.join(project_path, "project_structure.json")
    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(structure, f, indent=2, ensure_ascii=False, default=str)

    # Save tree text
    tree_output_path = os.path.join(project_path, "project_tree.txt")
    with open(tree_output_path, "w", encoding="utf-8") as f:
        f.write("RabbitMirror Project Structure\n")
        f.write("=" * 50 + "\n\n")
        f.write(
            f"Analysis Date: {structure['analysis_summary']['analysis_timestamp']}\n"
        )
        f.write(f"Total Files: {structure['analysis_summary']['total_files']:,}\n")
        f.write(
            f"Total Directories: {structure['analysis_summary']['total_directories']:,}\n"
        )
        f.write(
            f"Total Size: {structure['analysis_summary']['total_size_formatted']}\n\n"
        )

        f.write("File Categories:\n")
        f.write("-" * 20 + "\n")
        for category, data in structure["analysis_summary"]["file_categories"].items():
            f.write(
                f"{category.replace('_', ' ').title()}: {data['count']} files ({data['percentage']:.1f}%)\n"
            )

        f.write("\n" + "=" * 50 + "\n")
        f.write("Directory Tree:\n")
        f.write("=" * 50 + "\n\n")
        f.write(tree_text)

    print(f"\nAnalysis complete!")
    print(f"JSON structure saved to: {json_output_path}")
    print(f"Tree representation saved to: {tree_output_path}")
    print(f"\nProject Summary:")
    print(f"- Total Files: {structure['analysis_summary']['total_files']:,}")
    print(
        f"- Total Directories: {structure['analysis_summary']['total_directories']:,}"
    )
    print(f"- Total Size: {structure['analysis_summary']['total_size_formatted']}")

    print(f"\nTop File Categories:")
    sorted_categories = sorted(
        structure["analysis_summary"]["file_categories"].items(),
        key=lambda x: x[1]["count"],
        reverse=True,
    )
    for category, data in sorted_categories[:10]:
        print(
            f"- {category.replace('_', ' ').title()}: {data['count']} files ({data['percentage']:.1f}%)"
        )


if __name__ == "__main__":
    main()
