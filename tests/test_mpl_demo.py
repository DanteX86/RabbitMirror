import csv
import subprocess
import sys
from pathlib import Path

import yaml


def test_mpl_demo_cli_exports(tmp_path: Path):
    script = Path("scripts/mpl_demo.py").resolve()
    out_img = tmp_path / "plot.png"
    out_csv = tmp_path / "data.csv"
    out_yaml = tmp_path / "meta.yaml"

    cmd = [
        sys.executable,
        str(script),
        "--out",
        str(out_img),
        "--format",
        "png",
        "--csv-out",
        str(out_csv),
        "--yaml-out",
        str(out_yaml),
        "--num-points",
        "10",
        "--style",
        "none",
    ]
    r = subprocess.run(cmd, check=True, capture_output=True, text=True)
    assert r.returncode == 0

    # Image assertions
    assert out_img.exists(), "Expected image output not found"
    assert out_img.stat().st_size > 0, "Image file is empty"

    # CSV assertions
    assert out_csv.exists() and out_csv.stat().st_size > 0
    rows = list(csv.DictReader(out_csv.open()))
    assert rows[0].keys() == {"x", "y"}
    # Deterministic sample ends
    assert rows[0]["x"] == "0.0"
    assert "y" in rows[0]

    # YAML assertions
    assert out_yaml.exists() and out_yaml.stat().st_size > 0
    payload = yaml.safe_load(out_yaml.read_text())
    assert payload["meta"]["generator"] == "mpl_demo"
    assert payload["columns"] == ["x", "y"]
    assert (
        "samples" in payload
        and "head" in payload["samples"]
        and "tail" in payload["samples"]
    )
