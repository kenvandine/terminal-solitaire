#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DIST_DIR="$SCRIPT_DIR/dist"

usage() {
    echo "Usage: $0 <target>"
    echo ""
    echo "Targets:"
    echo "  alpine   Build for Alpine Linux (musl, static-linked Python)"
    echo "  debian   Build for Debian/Ubuntu/Fedora (glibc, most Linux distros)"
    echo "  both     Build both Alpine and Debian binaries"
    exit 1
}

build_alpine() {
    echo "Building Alpine (musl) binary..."
    docker run --rm -v "$SCRIPT_DIR:/src" -w /src python:3.12-alpine sh -c '
      apk add --no-cache gcc musl-dev &&
      pip install pyinstaller &&
      pyinstaller --onefile --distpath dist solitaire.py
    '
    mv "$DIST_DIR/solitaire" "$DIST_DIR/solitaire-alpine-x86_64"
    echo "Alpine binary: $DIST_DIR/solitaire-alpine-x86_64"
}

build_debian() {
    echo "Building Debian (glibc) binary..."
    docker run --rm -v "$SCRIPT_DIR:/src" -w /src python:3.12-slim sh -c '
      apt-get update && apt-get install -y --no-install-recommends gcc libc6-dev &&
      pip install pyinstaller &&
      pyinstaller --onefile --distpath dist solitaire.py
    '
    mv "$DIST_DIR/solitaire" "$DIST_DIR/solitaire-debian-x86_64"
    echo "Debian binary: $DIST_DIR/solitaire-debian-x86_64"
}

mkdir -p "$DIST_DIR"

TARGET="${1:-}"
case "$TARGET" in
    alpine)  build_alpine ;;
    debian)  build_debian ;;
    both)    build_alpine; build_debian ;;
    *)       usage ;;
esac