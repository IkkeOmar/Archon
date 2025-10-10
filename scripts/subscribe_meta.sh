#!/usr/bin/env bash
set -euo pipefail

if [ -f .env ]; then
  # shellcheck disable=SC2046
  export $(grep -v '^#' .env | xargs -d '\n')
fi

if [ -z "${META_PAGE_ACCESS_TOKEN:-}" ]; then
  echo "META_PAGE_ACCESS_TOKEN is required" >&2
  exit 1
fi

if [ -z "${META_VERIFY_TOKEN:-}" ]; then
  echo "META_VERIFY_TOKEN is required" >&2
  exit 1
fi

curl -X POST "https://graph.facebook.com/v20.0/me/subscribed_apps" \
  -d "access_token=${META_PAGE_ACCESS_TOKEN}" \
  -d "subscribed_fields=messages,messaging_postbacks,messaging_referrals,messaging_handovers"

echo "Subscribed to Messenger webhook. Ensure Instagram is enabled via app dashboard."
