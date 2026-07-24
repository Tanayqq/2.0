#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# MedRef Unified Push Script
#
# Branch strategy:
#   origin/master  → Render (backend auto-deploy)
#   origin/main    → Vercel (frontend auto-deploy, master disabled in vercel.json)
#   gitlab/master  → GitLab CI / backup
#   gitlab/main    → GitLab backup
#
# Usage: bash scripts/push.sh "commit message"
# ─────────────────────────────────────────────────────────────────────────────

set -e

MSG="${1:-chore: update}"

echo "→ Staging all changes..."
git add -A

echo "→ Committing: $MSG"
git commit -m "$MSG" || echo "(nothing new to commit)"

echo "→ Pushing to GitHub (master + main)..."
git push origin master:master master:main

echo "→ Pushing to GitLab (master + main)..."
git push gitlab master:master master:main

echo "✅ Done — Render (master) + Vercel (main) both updated"
