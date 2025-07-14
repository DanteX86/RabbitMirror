import json
from pathlib import Path
from typing import Any, Dict, List, Union

import pandas as pd
import yaml

from .error_recovery import (
    RetryConfig,
    monitor_errors,
    robust_operation,
    with_timeout,
)
from .exceptions import (
    ExportError,
    FileOperationError,
    InvalidFormatError,
)


class ExportFormatter:
    def __init__(self, output_dir: str = "exports"):
        self.output_dir = Path(output_dir)
        self.retry_config = RetryConfig(
            max_attempts=3,
            base_delay=0.5,
            retryable_exceptions=[OSError, IOError, PermissionError],
        )
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise FileOperationError(
                f"Failed to create output directory: {output_dir}",
                file_path=output_dir,
                operation="create_directory",
                error_code="DIRECTORY_CREATION_FAILED",
            ) from e

    @robust_operation(
        retry_config=RetryConfig(max_attempts=3, base_delay=0.5),
        timeout_seconds=30.0,
    )
    @monitor_errors
    def load_data(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Load data from a file based on its extension.

        Args:
            file_path: Path to the file to load

        Returns:
            Dict containing the loaded data

        Raises:
            FileOperationError: If the file cannot be read
            InvalidFormatError: If the file format is not supported
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileOperationError(
                f"File not found: {file_path}",
                file_path=str(file_path),
                operation="read",
                error_code="FILE_NOT_FOUND",
            )

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
                try:
                    df = pd.read_csv(file_path)
                    return df.to_dict(orient="dict")
                except pd.errors.EmptyDataError as exc:
                    raise InvalidFormatError(
                        f"CSV file is empty: {file_path}",
                        file_path=str(file_path),
                        error_code="EMPTY_CSV_FILE",
                    ) from exc
                except pd.errors.ParserError as e:
                    raise InvalidFormatError(
                        f"CSV parsing error: {str(e)}",
                        file_path=str(file_path),
                        error_code="CSV_PARSE_ERROR",
                    ) from e

            elif file_format in [".xlsx", ".xls"]:
                try:
                    df = pd.read_excel(file_path)
                    return df.to_dict(orient="dict")
                except Exception as e:
                    raise InvalidFormatError(
                        f"Excel file reading error: {str(e)}",
                        file_path=str(file_path),
                        error_code="EXCEL_READ_ERROR",
                    ) from e

            else:
                raise InvalidFormatError(
                    f"Unsupported file format: {file_format}. "
                    "Supported formats: .json, .yaml, .yml, .csv, .xlsx, .xls",
                    file_path=str(file_path),
                    error_code="UNSUPPORTED_FORMAT",
                )

        except (FileNotFoundError, PermissionError, OSError) as e:
            raise FileOperationError(
                f"Error reading file {file_path}: {str(e)}",
                file_path=str(file_path),
                operation="read",
                error_code="FILE_READ_ERROR",
            ) from e
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise InvalidFormatError(
                f"Invalid file format in {file_path}: {str(e)}",
                file_path=str(file_path),
                error_code="INVALID_FILE_FORMAT",
            ) from e

    @robust_operation(
        retry_config=RetryConfig(max_attempts=3, base_delay=0.5),
        timeout_seconds=60.0,
    )
    @monitor_errors
    def export_data(
        self, data: Dict[str, Any], export_format: str, filename: str
    ) -> str:
        """Export data in the specified format.

        Args:
            data: Data to export
            export_format: Format to export to (json, yaml, csv, excel)
            filename: Base filename (without extension)

        Returns:
            Path to the exported file

        Raises:
            ExportError: If export operation fails
        """
        exporters = {
            "json": self._export_json,
            "yaml": self._export_yaml,
            "csv": self._export_csv,
            "excel": self._export_excel,
        }

        if export_format not in exporters:
            raise ExportError(
                f"Unsupported export format: {export_format}. "
                f"Supported formats: {', '.join(exporters.keys())}",
                export_format=export_format,
                error_code="UNSUPPORTED_EXPORT_FORMAT",
            )

        try:
            return exporters[export_format](data, filename)
        except Exception as e:
            raise ExportError(
                f"Export failed for format {export_format}: {str(e)}",
                export_format=export_format,
                error_code="EXPORT_FAILED",
            ) from e

    @with_timeout(30.0)
    def _export_json(self, data: Dict[str, Any], filename: str) -> str:
        """Export data as JSON."""
        output_path = self.output_dir / f"{filename}.json"
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return str(output_path)
        except (OSError, PermissionError) as e:
            raise FileOperationError(
                f"Failed to write JSON file: {output_path}",
                file_path=str(output_path),
                operation="write",
                error_code="JSON_WRITE_ERROR",
            ) from e
        except TypeError as e:
            raise ExportError(
                f"JSON serialization error: {str(e)}",
                export_format="json",
                error_code="JSON_SERIALIZATION_ERROR",
            ) from e

    @with_timeout(30.0)
    def _export_yaml(self, data: Dict[str, Any], filename: str) -> str:
        """Export data as YAML."""
        output_path = self.output_dir / f"{filename}.yaml"
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, allow_unicode=True, sort_keys=False)
            return str(output_path)
        except (OSError, PermissionError) as e:
            raise FileOperationError(
                f"Failed to write YAML file: {output_path}",
                file_path=str(output_path),
                operation="write",
                error_code="YAML_WRITE_ERROR",
            ) from e
        except yaml.YAMLError as e:
            raise ExportError(
                f"YAML serialization error: {str(e)}",
                export_format="yaml",
                error_code="YAML_SERIALIZATION_ERROR",
            ) from e

    @with_timeout(30.0)
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

    @with_timeout(30.0)
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
