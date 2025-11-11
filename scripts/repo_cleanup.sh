#!/usr/bin/env bash
# Repo cleanup helper - review before running
set -euo pipefail

echo "This script will:
 - remove tracked virtualenvs and build artifacts from git index
 - show suggested commit message
Please review before running."

read -p "Proceed (y/N)? " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
  echo "Aborted by user."
  exit 1
fi

echo "Removing tracked venvs and build artifacts from git index..."
git rm -r --cached services/api/.venv || true
git rm -r --cached .venv || true
git rm -r --cached dist || true
git rm -r --cached build || true
git rm -r --cached **/localstack-data || true

echo "Create commit"
git add .gitignore
git commit -m "chore: remove venv and build artifacts from repo, add .gitignore"

echo "Done. Review with 'git status' and push when ready: git push origin HEAD"
