#!/usr/bin/env bash
# Update vendored upstream (git subtree) and rebuild weekly notebooks.

set -euo pipefail

# --- Defaults (override with env vars or flags) ---
REMOTE_NAME="${REMOTE_NAME:-virtual}"
UPSTREAM_BRANCH="${UPSTREAM_BRANCH:-master}"   # use 'main' if your upstream uses main
VENDOR_PREFIX="${VENDOR_PREFIX:-vendor/virtual-pyprog}"
MAP_FILE="${MAP_FILE:-course/map.yml}"
OUT_DIR="${OUT_DIR:-course/weeks}"
PY_SCRIPT="${PY_SCRIPT:-tools/build_weeks.py}"
AUTO_COMMIT="${AUTO_COMMIT:-false}"

usage() {
  cat <<EOF
Usage: $0 [-b branch] [-r remote] [-p prefix] [-m map.yml] [-o outdir] [-c]
  -b  Upstream branch to pull (default: ${UPSTREAM_BRANCH})
  -r  Remote name for upstream (default: ${REMOTE_NAME})
  -p  Subtree prefix (default: ${VENDOR_PREFIX})
  -m  Manifest file (default: ${MAP_FILE})
  -o  Output dir for generated weeks (default: ${OUT_DIR})
  -c  Auto-commit changes after build
Env overrides: REMOTE_NAME, UPSTREAM_BRANCH, VENDOR_PREFIX, MAP_FILE, OUT_DIR, PY_SCRIPT, AUTO_COMMIT
EOF
}

while getopts ":b:r:p:m:o:ch" opt; do
  case "${opt}" in
    b) UPSTREAM_BRANCH="${OPTARG}" ;;
    r) REMOTE_NAME="${OPTARG}" ;;
    p) VENDOR_PREFIX="${OPTARG}" ;;
    m) MAP_FILE="${OPTARG}" ;;
    o) OUT_DIR="${OPTARG}" ;;
    c) AUTO_COMMIT="true" ;;
    h) usage; exit 0 ;;
    \?) echo "Invalid option: -$OPTARG" >&2; usage; exit 2 ;;
  esac
done

# --- Checks ---
command -v git >/dev/null 2>&1 || { echo "git not found"; exit 1; }
command -v python >/dev/null 2>&1 || { echo "python not found"; exit 1; }

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || {
  echo "Not inside a git repository."; exit 1;
}

if ! git remote get-url "${REMOTE_NAME}" >/dev/null 2>&1; then
  echo "Remote '${REMOTE_NAME}' not found."
  echo "Add it first, e.g.: git remote add ${REMOTE_NAME} https://github.com/hag007/virtual-pyprog.git"
  exit 1
fi

if [ ! -f "${PY_SCRIPT}" ]; then
  echo "Build script not found at '${PY_SCRIPT}'"; exit 1
fi

if [ ! -f "${MAP_FILE}" ]; then
  echo "Manifest not found at '${MAP_FILE}'"; exit 1
fi

# --- 1) Fetch + subtree pull ---
echo ">>> Fetching '${REMOTE_NAME}'..."
git fetch "${REMOTE_NAME}"

echo ">>> Pulling subtree into '${VENDOR_PREFIX}' from ${REMOTE_NAME}/${UPSTREAM_BRANCH}..."
git subtree pull --prefix "${VENDOR_PREFIX}" "${REMOTE_NAME}" "${UPSTREAM_BRANCH}" --squash

# --- 2) Build weekly notebooks ---
echo ">>> Building weekly notebooks from '${MAP_FILE}' -> '${OUT_DIR}'..."
python "${PY_SCRIPT}" --map "${MAP_FILE}" --outdir "${OUT_DIR}"

# --- Optional: auto-commit changes ---
if [ "${AUTO_COMMIT}" = "true" ]; then
  echo ">>> Committing changes..."
  git add "${VENDOR_PREFIX}" "${OUT_DIR}"
  git diff --cached --quiet || git commit -m "chore: update vendor subtree and rebuild weeks"
fi

echo "✅ Done."
