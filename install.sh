#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_TARGET="$HOME/.gemini/config/skills/bndar-lead-pipeline"

echo "Installing bndar-lead-pipeline skill into $SKILL_TARGET..."
mkdir -p "$HOME/.gemini/config/skills"
rm -rf "$SKILL_TARGET"
ln -sf "$SCRIPT_DIR/skills/bndar-lead-pipeline" "$SKILL_TARGET"

echo "✅ Skill successfully installed and linked to Antigravity config!"
