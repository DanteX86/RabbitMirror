#!/usr/bin/env python3
"""
Matplotlib demo script (non-interactive) that saves a plot and optional CSV/YAML exports.

Usage examples:
  - Default PNG to images/, CSV/YAML to exports/:
      python scripts/mpl_demo.py

  - Custom size, DPI, format, and style:
      python scripts/mpl_demo.py \
        --out images/plot \
        --width 8 --height 4.5 --dpi 150 --format svg \
        --style seaborn-v0_8

  - Exports to a temp folder:
      python scripts/mpl_demo.py --csv-out exports/mpl_demo.csv --yaml-out exports/mpl_demo.yaml

Notes:
  - Forces the Agg backend for headless environments.
  - If --style is provided and not "none", uses plt.style.use(--style).
"""
from __future__ import annotations

import argparse
import csv
import math
import os
from pathlib import Path
from typing import Tuple

import matplotlib

# Use non-interactive backend suitable for terminals/CI
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import yaml  # noqa: E402


def generate_data(num_points: int = 400) -> Tuple[np.ndarray, np.ndarray]:
    """Generate deterministic sample data for plotting and export assertions.

    Returns (x, y) where y = sin(x^2) sampled over [0, 2π].
    """
    x = np.linspace(0, 2 * math.pi, num_points)
    y = np.sin(x**2)
    return x, y


def save_plot(
    x: np.ndarray,
    y: np.ndarray,
    out_base: Path,
    width: float,
    height: float,
    dpi: int,
    img_format: str,
    style: str | None,
) -> Path:
    """Create and save the plot to out_base with the requested format.

    out_base can be a path with or without an image suffix; the real output path is
    out_base.with_suffix(f".{img_format}").
    """
    if style and style.lower() != "none":
        try:
            plt.style.use(style)
        except Exception:
            # Fall back silently if style is unknown
            pass

    fig = plt.figure(figsize=(width, height), dpi=dpi)
    ax = fig.add_subplot(111)
    ax.plot(x, y, label="sin(x^2)", color="#1f77b4", linewidth=2)
    ax.set_title("Matplotlib Demo: sin(x^2)")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True, alpha=0.3)
    ax.legend()

    fig.tight_layout()
    out_base.parent.mkdir(parents=True, exist_ok=True)
    out_path = out_base.with_suffix(f".{img_format}")
    fig.savefig(out_path, bbox_inches="tight")
    return out_path


def export_csv(x: np.ndarray, y: np.ndarray, csv_path: Path) -> Path:
    """Export x/y data to CSV with headers x,y."""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["x", "y"])
        for xv, yv in zip(x, y):
            writer.writerow([float(xv), float(yv)])
    return csv_path


def export_yaml(x: np.ndarray, y: np.ndarray, yaml_path: Path) -> Path:
    """Export basic metadata and first/last samples to YAML for lightweight assertions."""
    yaml_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "meta": {
            "generator": "mpl_demo",
            "function": "sin(x^2)",
            "num_points": int(x.shape[0]),
        },
        "columns": ["x", "y"],
        "samples": {
            "head": {"x": float(x[0]), "y": float(y[0])},
            "tail": {"x": float(x[-1]), "y": float(y[-1])},
        },
    }
    with yaml_path.open("w") as f:
        yaml.safe_dump(payload, f, sort_keys=False)
    return yaml_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Matplotlib demo that saves an image and optional exports.")
    parser.add_argument("--out", type=Path, default=Path("images/mpl_demo.png"), help="Output image path (suffix optional)")
    parser.add_argument("--width", type=float, default=8.0, help="Figure width in inches")
    parser.add_argument("--height", type=float, default=4.5, help="Figure height in inches")
    parser.add_argument("--dpi", type=int, default=150, help="Figure DPI")
    parser.add_argument("--format", choices=["png", "svg", "pdf"], default="png", help="Image format")
    parser.add_argument("--style", default="seaborn-v0_8", help="Matplotlib style name (use 'none' to disable)")
    parser.add_argument("--csv-out", type=Path, default=Path("exports/mpl_demo.csv"), help="CSV export path")
    parser.add_argument("--yaml-out", type=Path, default=Path("exports/mpl_demo.yaml"), help="YAML export path")
    parser.add_argument("--num-points", type=int, default=400, help="Number of sample points for the curve")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    x, y = generate_data(num_points=args.num_points)

    out_path = save_plot(
        x=x,
        y=y,
        out_base=args.out,
        width=args.width,
        height=args.height,
        dpi=args.dpi,
        img_format=args.format,
        style=args.style,
    )

    export_csv(x, y, args.csv_out)
    export_yaml(x, y, args.yaml_out)

    print(f"Saved plot to: {out_path}")
    print(f"CSV export: {args.csv_out}")
    print(f"YAML export: {args.yaml_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
