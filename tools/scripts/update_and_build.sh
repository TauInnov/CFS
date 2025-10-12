#!/usr/bin/env bash
# Update vendored upstream (git subtree) and rebuild weekly notebooks.
# Add --build-only (-B) flag to skip the update step.

set -euo pipefail

# --- Defaults (override via env or flags) ---
REMOTE_NAME="${REMOTE_NAME:-virtual}"
UPSTREAM_BRANCH="${UPSTREAM_BRANCH:-master}"   # use 'main' if upstream uses main
VENDOR_PREFIX="${VENDOR_PREFIX:-vendor/virtual-pyprog}"
MAP_FILE="${MAP_FILE:-course/map.yml}"
OUT_DIR="${OUT_DIR:-course/weeks}"
PY_SCRIPT="${PY_SCRIPT:-tools/build_weeks.py}"
AUTO_COMMIT="${AUTO_COMMIT:-false}"
BUILD_ONLY="${BUILD_ONLY:-false}"

usage() {
  cat <<EOF
Usage: $0 [options]
  -b <branch>     Upstream branch to pull (default: ${UPSTREAM_BRANCH})
  -r <remote>     Remote name for upstream (default: ${REMOTE_NAME})
  -p <prefix>     Subtree prefix (default: ${VENDOR_PREFIX})
  -m <map.yml>    Manifest file (default: ${MAP_FILE})
  -o <outdir>     Output dir for generated weeks (default: ${OUT_DIR})
  -c              Auto-commit changes after build
  -B, --build-only  Skip fetching/pulling upstream, only rebuild
  -h              Show this help message
EOF
}

# --- Parse args ---
while [[ $# -gt 0 ]]; do
  case "$1" in
    -b) UPSTREAM_BRANCH="$2"; shift 2 ;;
    -r) REMOTE_NAME="$2"; shift 2 ;;
    -p) VENDOR_PREFIX="$2"; shift 2 ;;
    -m) MAP_FILE="$2"; shift 2 ;;
    -o) OUT_DIR="$2"; shift 2 ;;
    -c) AUTO_COMMIT="true"; shift ;;
    -B|--build-only) BUILD_ONLY="true"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 2 ;;
  esac
done

# --- Sanity checks ---
command -v git >/dev/null 2>&1 || { echo "❌ git not found"; exit 1; }
command -v python >/dev/null 2>&1 || { echo "❌ python not found"; exit 1; }
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || {
  echo "❌ Not inside a git repository."; exit 1;
}

if [ ! -f "${PY_SCRIPT}" ]; then
  echo "❌ Build script not found at '${PY_SCRIPT}'"; exit 1
fi
if [ ! -f "${MAP_FILE}" ]; then
  echo "❌ Manifest not found at '${MAP_FILE}'"; exit 1
fi

# --- 1) Optionally fetch + subtree pull ---
if [ "${BUILD_ONLY}" = "false" ]; then
  if ! git remote get-url "${REMOTE_NAME}" >/dev/null 2>&1; then
    echo "❌ Remote '${REMOTE_NAME}' not found."
    echo "Add it first: git remote add ${REMOTE_NAME} https://github.com/hag007/virtual-pyprog.git"
    exit 1
  fi

  echo ">>> Fetching '${REMOTE_NAME}'..."
  git fetch "${REMOTE_NAME}"

  echo ">>> Pulling subtree into '${VENDOR_PREFIX}' from ${REMOTE_NAME}/${UPSTREAM_BRANCH}..."
  git subtree pull --prefix "${VENDOR_PREFIX}" "${REMOTE_NAME}" "${UPSTREAM_BRANCH}" --squash
else
  echo "⚙️  Build-only mode: skipping upstream update."
fi

# --- 2) Build weekly notebooks ---
echo ">>> Building weekly notebooks from '${MAP_FILE}' -> '${OUT_DIR}'..."
python "${PY_SCRIPT}" --map "${MAP_FILE}" --outdir "${OUT_DIR}"

# --- 3) Optionally commit ---
if [ "${AUTO_COMMIT}" = "true" ]; then
  echo ">>> Committing changes..."
  git add "${VENDOR_PREFIX}" "${OUT_DIR}" || true
  git diff --cached --quiet || git commit -m "chore: update vendor & rebuild weeks"
fi

echo "✅ Done."
