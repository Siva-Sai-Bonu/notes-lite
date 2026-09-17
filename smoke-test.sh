#!/usr/bin/env bash
set -euo pipefail
BASE_URL="${BASE_URL:-http://localhost:8080}"

echo "==> $BASE_URL/healthz"
curl -fsS "$BASE_URL/healthz"

echo "==> create a note"
ID=$(curl -fsS -X POST "$BASE_URL/api/notes" \
      -H 'Content-Type: application/json' \
      -d '{"title":"smoke","body":"created by pipeline"}' \
     | sed -n 's/.*"id":"\([^"]*\)".*/\1/p')
[ -n "$ID" ] || { echo "no id returned"; exit 1; }
echo "    id=$ID"

echo "==> read it back"
curl -fsS "$BASE_URL/api/notes/$ID" | grep -q smoke

echo "==> clean up"
curl -fsS -X DELETE "$BASE_URL/api/notes/$ID" >/dev/null

echo "==> smoke test passed"
