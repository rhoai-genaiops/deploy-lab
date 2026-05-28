#!/usr/bin/env bash
set -euo pipefail

GITEA_BASE="https://gitea-gitea.apps.cluster-pwjcv.pwjcv.sandbox1619.opentlc.com"
GITEA_PASSWORD="thisisthepassword"
GITHUB_ORG="rhoai-genaiops"
REPOS=(backend)
# REPOS=(experiments backend frontend evals genaiops-gitops)
WORKDIR=$(mktemp -d)

cleanup() {
  rm -rf "$WORKDIR"
}
trap cleanup EXIT

echo "Working in $WORKDIR"

for i in $(seq 1 10); do
  USER="user${i}"
  echo ""
  echo "=== Processing $USER ==="

  for REPO in "${REPOS[@]}"; do
    echo "  -- $REPO"
    REPO_DIR="$WORKDIR/${USER}-${REPO}"

    git clone \
      "https://${USER}:${GITEA_PASSWORD}@${GITEA_BASE#https://}/${USER}/${REPO}.git" \
      "$REPO_DIR"

    git -C "$REPO_DIR" remote add github \
      "https://github.com/${GITHUB_ORG}/${REPO}.git"

    git -C "$REPO_DIR" fetch github mlflow
    git -C "$REPO_DIR" reset --hard github/mlflow

    git -C "$REPO_DIR" push --force origin main

    echo "  -- $REPO done"
  done

  echo "=== $USER done ==="
done

echo ""
echo "All users synced."
