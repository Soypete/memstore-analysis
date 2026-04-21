#!/bin/bash
# Connect to homelab storage for experiments
# Usage: ./scripts/connect-storage.sh [macos|linux]

set -e

PLATFORM="${1:-$(uname -s | tr '[:upper:]' '[:lower:]')}"
MOUNT_POINT="${MOUNT_POINT:-/mnt/homelab}"

echo "Connecting to homelab storage (platform: $PLATFORM)..."

case "$PLATFORM" in
  darwin|macos)
    # Check if already mounted
    if mount | grep -q "$MOUNT_POINT"; then
      echo "Already mounted at $MOUNT_POINT"
      exit 0
    fi

    # Create mount point
    mkdir -p "$MOUNT_POINT"

    # Try SSHFS first (requires ssh to referb)
    if command -v sshfs &> /dev/null; then
      echo "Mounting via SSHFS..."
      sshfs referb:/opt/experiments "$MOUNT_POINT" -o reconnect,ServerAliveInterval=15
    else
      echo "Error: sshfs not found. Install with: brew install sshfs"
      exit 1
    fi
    ;;

  linux)
    mkdir -p "$MOUNT_POINT"
    if command -v sshfs &> /dev/null; then
      sshfs referb:/opt/experiments "$MOUNT_POINT" -o reconnect
    else
      sudo apt-get install -y sshfs
      sshfs referb:/opt/experiments "$MOUNT_POINT" -o reconnect
    fi
    ;;

  *)
    echo "Unknown platform: $PLATFORM"
    exit 1
    ;;
esac

echo "Mounted at $MOUNT_POINT"
ls -la "$MOUNT_POINT"