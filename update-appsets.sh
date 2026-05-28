#!/bin/bash
set -e

BASE_URL="gitea-gitea.apps.cluster-pwjcv.pwjcv.sandbox1619.opentlc.com"
PASSWORD="thisisthepassword"
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

for i in $(seq 4 10); do
  USER="user${i}"
  REPO_URL="https://${USER}:${PASSWORD}@${BASE_URL}/${USER}/genaiops-gitops"
  CLONE_DIR="${TMPDIR}/${USER}-genaiops-gitops"

  echo "==> Processing ${USER}..."

  git clone "$REPO_URL" "$CLONE_DIR"

  for FILE in appset-prod.yaml appset-test.yaml; do
    FILE_PATH="${CLONE_DIR}/${FILE}"
    if [[ -f "$FILE_PATH" ]]; then
      sed -i '' 's|https://github.com/rhoai-genaiops/genaiops-helmcharts.git|https://github.com/ckavili/genaiops-helmcharts.git|g' "$FILE_PATH"
      echo "    Updated ${FILE}"
    else
      echo "    WARNING: ${FILE} not found, skipping"
    fi
  done

  cd "$CLONE_DIR"
  git add appset-prod.yaml appset-test.yaml
  if git diff --cached --quiet; then
    echo "    No changes to commit for ${USER}"
  else
    git commit -m "Update helmcharts repoURL from rhoai-genaiops to ckavili"
    git push origin main
    echo "    Pushed changes for ${USER}"
  fi
  cd - > /dev/null
done

echo "Done."
