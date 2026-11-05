#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$HOME/.gemini/config/skills"

mkdir -p "$SKILLS_DIR"

echo "Installing bndar skills into $SKILLS_DIR..."

rm -rf "$SKILLS_DIR/bndar-lead-pipeline"
ln -sf "$SCRIPT_DIR/skills/bndar-lead-pipeline" "$SKILLS_DIR/bndar-lead-pipeline"
echo "✅ Linked bndar-lead-pipeline"

rm -rf "$SKILLS_DIR/bndar-prospection"
ln -sf "$SCRIPT_DIR/skills/bndar-prospection" "$SKILLS_DIR/bndar-prospection"
echo "✅ Linked bndar-prospection"

echo "🎉 All Bndar skills successfully installed and linked to Antigravity config!"
