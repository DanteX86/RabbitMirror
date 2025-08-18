import json
from pathlib import Path

base = Path("exports")
parsed_path = base / "parsed.json"
clusters_path = base / "clusters.json"
patterns_path = base / "patterns.json"


def load_json(p: Path):
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


parsed = load_json(parsed_path)
clusters = load_json(clusters_path)
patterns = load_json(patterns_path)

combined = {
    "entries": parsed.get("entries", parsed),
    "clusters": clusters,
    "patterns": patterns,
    "metadata": {"source": "watch-history.html"},
}

out_path = base / "demo_data.json"
out_path.write_text(
    json.dumps(combined, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(f"Wrote {out_path}")
