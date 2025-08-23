#!/usr/bin/env bash
set -euo pipefail

API_BASE=${API_BASE:-http://localhost:5001}
API_KEY_HEADER=()
if [[ -n "${API_KEY:-}" ]]; then
  API_KEY_HEADER=(-H "X-API-Key: ${API_KEY}")
fi

PAYLOAD="examples/api/sample_watch_history.json"
if [[ ! -f "$PAYLOAD" ]]; then
  echo "Sample payload not found at $PAYLOAD" >&2
  exit 1
fi

curl -sS -H 'Content-Type: application/json' "${API_KEY_HEADER[@]}" \
  --data-binary @"$PAYLOAD" "$API_BASE/api/analyze" | \
  jq . 2>/dev/null || python -m json.tool
