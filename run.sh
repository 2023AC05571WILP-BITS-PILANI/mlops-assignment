#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# run.sh — Convenience wrapper to run the pipeline (Docker or local)
# ─────────────────────────────────────────────────────────────────────────────
#
# Usage:
#   ./run.sh                              # full pipeline in Docker
#   ./run.sh --stages merge_daily         # specific stage in Docker
#   ./run.sh --local                      # run locally (no Docker)
#   ./run.sh --local --stages fetch_weather
#   ./run.sh --build                      # rebuild Docker image + run
#   ./run.sh --list                       # list available stages
#   ./run.sh --help                       # show this help
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail
cd "$(dirname "$0")"

IMAGE_NAME="mlops-pipeline"
COMPOSE_FILE="docker-compose.yml"

# ── Parse flags ───────────────────────────────────────────────────────────────
LOCAL=false
BUILD=false
PIPELINE_ARGS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --local)
            LOCAL=true
            shift
            ;;
        --build)
            BUILD=true
            shift
            ;;
        --help|-h)
            echo "Usage: ./run.sh [OPTIONS] [PIPELINE_ARGS...]"
            echo ""
            echo "Options:"
            echo "  --local           Run locally without Docker"
            echo "  --build           Rebuild Docker image before running"
            echo "  -h, --help        Show this help"
            echo ""
            echo "Pipeline arguments (passed through):"
            echo "  --stages <s1> <s2>  Run specific stages"
            echo "  --skip <s1>         Skip specific stages"
            echo "  --list              List available stages"
            echo "  --dry-run           Preview execution plan"
            echo "  -v, --verbose       Verbose output"
            echo ""
            echo "Examples:"
            echo "  ./run.sh                                  # full pipeline in Docker"
            echo "  ./run.sh --stages fetch_weather           # one stage in Docker"
            echo "  ./run.sh --build --stages merge_daily     # rebuild + run"
            echo "  ./run.sh --local                          # run without Docker"
            echo "  ./run.sh --local --stages merge_daily -v  # local, verbose"
            exit 0
            ;;
        *)
            PIPELINE_ARGS+=("$1")
            shift
            ;;
    esac
done

# ── Local execution ───────────────────────────────────────────────────────────
if $LOCAL; then
    echo "🏃 Running pipeline locally..."
    exec python3 pipeline.py "${PIPELINE_ARGS[@]}"
fi

# ── Docker execution ──────────────────────────────────────────────────────────

# Check Docker is available
if ! command -v docker &>/dev/null; then
    echo "❌ Docker not found. Install Docker or use --local flag."
    exit 1
fi

# Build if requested or if image doesn't exist
if $BUILD || ! docker image inspect "$IMAGE_NAME" &>/dev/null; then
    echo "🔨 Building Docker image..."
    docker compose build pipeline
    echo ""
fi

# Run
echo "🐳 Running pipeline in Docker..."
docker compose run --rm pipeline "${PIPELINE_ARGS[@]}"
