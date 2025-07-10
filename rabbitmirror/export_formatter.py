import json
from pathlib import Path
from typing import Any, Dict, List, Union

import pandas as pd
import yaml


class ExportFormatter:
    def __init__(self, output_dir: str = "exports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _load_data(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Load data from a file based on its extension.

        Args:
            file_path: Path to the file to load

        Returns:
            Dict containing the loaded data

        Raises:
            ValueError: If the file format is not supported
            FileNotFoundError: If the file doesn't exist
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Determine the file format from extension
        file_format = file_path.suffix.lower()

        try:
            if file_format == ".json":
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)

            elif file_format in [".yaml", ".yml"]:
                with open(file_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f)

            elif file_format == ".csv":
                df = pd.read_csv(file_path)
                return df.to_dict(orient="dict")

            elif file_format in [".xlsx", ".xls"]:
                df = pd.read_excel(file_path)
                return df.to_dict(orient="dict")

            else:
                raise ValueError(
                    f"Unsupported file format: {file_format}. "
                    "Supported formats: .json, .yaml, .yml, .csv, .xlsx, .xls"
                )

        except Exception as e:
            raise ValueError(f"Error loading {file_path}: {str(e)}")

    def export_data(
        self, data: Dict[str, Any], export_format: str, filename: str
    ) -> str:
        """Export data in the specified format."""
        exporters = {
            "json": self._export_json,
            "yaml": self._export_yaml,
            "csv": self._export_csv,
            "excel": self._export_excel,
        }

        if export_format not in exporters:
            raise ValueError(f"Unsupported export format: {export_format}")

        return exporters[export_format](data, filename)

    def _export_json(self, data: Dict[str, Any], filename: str) -> str:
        """Export data as JSON."""
        output_path = self.output_dir / f"{filename}.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return str(output_path)

    def _export_yaml(self, data: Dict[str, Any], filename: str) -> str:
        """Export data as YAML."""
        output_path = self.output_dir / f"{filename}.yaml"
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False)
        return str(output_path)

    def _export_csv(self, data: Dict[str, Any], filename: str) -> str:
        """Export data as CSV."""
        output_path = self.output_dir / f"{filename}.csv"

        # Convert the data to a format suitable for CSV
        if (
            isinstance(data, dict)
            and "entries" in data
            and isinstance(data["entries"], list)
        ):
            # If data has an 'entries' list, use that directly
            df = pd.DataFrame(data["entries"])
        elif isinstance(data, dict) and all(isinstance(v, list) for v in data.values()):
            # If data is a dict of lists, convert to DataFrame directly
            df = pd.DataFrame(data)
        elif isinstance(data, list):
            # If data is a list of dicts, convert to DataFrame
            df = pd.DataFrame(data)
        else:
            # For other structures, flatten the data first
            flat_data = self._flatten_dict(data)
            df = pd.DataFrame([flat_data])

        df.to_csv(output_path, index=False, encoding="utf-8")
        return str(output_path)

    def _export_excel(self, data: Dict[str, Any], filename: str) -> str:
        """Export data as Excel file."""
        output_path = self.output_dir / f"{filename}.xlsx"

        # Convert the data to a format suitable for Excel (same logic as CSV)
        if (
            isinstance(data, dict)
            and "entries" in data
            and isinstance(data["entries"], list)
        ):
            # If data has an 'entries' list, use that directly
            df = pd.DataFrame(data["entries"])
        elif isinstance(data, dict) and all(isinstance(v, list) for v in data.values()):
            # If data is a dict of lists, convert to DataFrame directly
            df = pd.DataFrame(data)
        elif isinstance(data, list):
            # If data is a list of dicts, convert to DataFrame
            df = pd.DataFrame(data)
        else:
            # For other structures, flatten the data first
            flat_data = self._flatten_dict(data)
            df = pd.DataFrame([flat_data])

        df.to_excel(output_path, index=False, engine="openpyxl")
        return str(output_path)

    def _flatten_dict(
        self, d: Dict[str, Any], parent_key: str = "", sep: str = "_"
    ) -> Dict[str, Any]:
        """Flatten a nested dictionary."""
        items: List[tuple] = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
