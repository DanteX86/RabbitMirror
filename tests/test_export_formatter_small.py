import json
from pathlib import Path

import pandas as pd
import pytest

from rabbitmirror.export_formatter import ExportFormatter


def test_export_csv_with_entries_list(tmp_path, monkeypatch):
    fmt = ExportFormatter(output_dir=str(tmp_path))
    data = {"entries": [{"a": 1, "b": 2}, {"a": 3, "b": 4}]}
    out = fmt.export_data(data, "csv", "sample")
    p = Path(out)
    assert p.exists() and p.suffix == ".csv"
    df = pd.read_csv(p)
    assert list(df.columns) == ["a", "b"]
    assert len(df) == 2


def test_export_json_roundtrip(tmp_path):
    fmt = ExportFormatter(output_dir=str(tmp_path))
    payload = {"x": 1, "y": [1, 2]}
    out = fmt.export_data(payload, "json", "data")
    p = Path(out)
    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data == payload


def test_export_unsupported_format_raises(tmp_path):
    fmt = ExportFormatter(output_dir=str(tmp_path))
    with pytest.raises(Exception):
        fmt.export_data({"a": 1}, "toml", "x")


def test_export_csv_flattens_nested_dict(tmp_path):
    fmt = ExportFormatter(output_dir=str(tmp_path))
    nested = {"a": {"b": 1, "c": 2}}
    out = fmt.export_data(nested, "csv", "flat")
    p = Path(out)
    assert p.exists()
    content = p.read_text(encoding="utf-8").strip().splitlines()
    # Header should reflect flattened keys like a_b and a_c
    assert "a_b" in content[0] and "a_c" in content[0]
    assert "," in content[1]
