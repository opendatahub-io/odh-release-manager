#!/bin/bash
set -e

DISPLAY_NAME="$1"

if [ -z "$DISPLAY_NAME" ]; then
  echo "Error: Display name is required"
  exit 1
fi

# Check length limits
if [ ${#DISPLAY_NAME} -lt 2 ]; then
  echo "Error: Display name too short (minimum 2 characters)"
  exit 1
fi

if [ ${#DISPLAY_NAME} -gt 50 ]; then
  echo "Error: Display name too long (maximum 50 characters)"
  exit 1
fi

echo "Display name '$DISPLAY_NAME' is valid"