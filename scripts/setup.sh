#!/usr/bin/env bash
#
# Full setup flow for CASS-VLA / PlanDiscrim.
#
#   ./scripts/setup.sh              create venv, install, verify
#   ./scripts/setup.sh --force      recreate the venv from scratch
#   ./scripts/setup.sh --probe      also run the MetaDrive capability probe
#   ./scripts/setup.sh --gui        also check the renderers (3D window fails on macOS)
#   ./scripts/setup.sh --verbose    do not filter the objc SDL warnings
#
set -euo pipefail

PYVER=3.11
FORCE=0; PROBE=0; GUI=0; VERBOSE=0
for arg in "$@"; do
  case "$arg" in
    --force)   FORCE=1 ;;
    --probe)   PROBE=1 ;;
    --gui)     GUI=1 ;;
    --verbose) VERBOSE=1 ;;
    -h|--help) sed -n '3,10p' "$0"; exit 0 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
VENV="$ROOT/.venv"
PY="$VENV/bin/python"

step() { printf '\n\033[1m==> %s\033[0m\n' "$1"; }
warn() { printf '\033[33m    %s\033[0m\n' "$1"; }

# objc duplicate-SDL warnings are expected and harmless on macOS; see
# docs/phase1_findings.md. Filter them so real errors stay visible.
run() {
  if [ "$VERBOSE" = 1 ]; then "$@"; else "$@" 2> >(grep -v '^objc\[' >&2 || true); fi
}

step "Checking uv"
if ! command -v uv >/dev/null 2>&1; then
  echo "uv not found. Install it with one of:" >&2
  echo "    brew install uv" >&2
  echo "    curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
  exit 1
fi
echo "    $(uv --version)"

step "Virtual environment (python $PYVER)"
if [ "$FORCE" = 1 ] && [ -d "$VENV" ]; then
  echo "    --force: removing existing $VENV"
  rm -rf "$VENV"
fi
if [ -d "$VENV" ]; then
  echo "    reusing $VENV  (--force to recreate)"
else
  uv venv --python "$PYVER" "$VENV"
fi

step "Installing dependencies"
uv pip install --python "$PY" -r requirements.txt

# metadrive-simulator depends on opencv-python (GUI build). We prefer the
# headless build: it is smaller and does not pull GUI libs. Note this does NOT
# silence the SDL warnings on macOS -- headless 5.x bundles libSDL2 too.
step "Preferring headless opencv"
if uv pip list --python "$PY" 2>/dev/null | grep -q '^opencv-python '; then
  echo "    swapping opencv-python -> opencv-python-headless"
  uv pip uninstall --python "$PY" opencv-python >/dev/null
  uv pip install --python "$PY" opencv-python-headless >/dev/null
else
  echo "    already headless"
fi

step "Verifying setup"
echo "    (first run downloads ~200MB of MetaDrive assets)"
CHECK_ARGS=""
[ "$GUI" = 1 ] && CHECK_ARGS="--gui"
if run "$PY" scripts/check_setup.py $CHECK_ARGS; then
  echo "    checks passed"
else
  warn "one or more checks FAILED -- see output above"
  if [ "$GUI" = 1 ]; then
    warn "the Panda3D 3D window is known to fail on macOS; top-down works."
    warn "see docs/phase1_findings.md"
  fi
fi

if [ "$PROBE" = 1 ]; then
  step "MetaDrive capability probe"
  run "$PY" scripts/probe_state.py
fi

step "Done"
cat <<MSG
    Activate the environment with:

        source .venv/bin/activate

    Then:
        python scripts/check_setup.py          verify setup
        python scripts/probe_state.py          MetaDrive capability probe

    Expect objc "Class SDL... implemented in both" warnings on macOS.
    They are harmless -- see docs/phase1_findings.md.
MSG
