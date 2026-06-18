#!/bin/bash

# Check release readiness by comparing registered vs total components
# Usage: ./check_release_readiness.sh <release_version>

set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Usage: $0 <release_version>"
  exit 1
fi

RELEASE_VERSION="$1"
RELEASE_DIR="releases/$RELEASE_VERSION"
COMPONENTS_FILE="${RELEASE_DIR}/components.yaml"

echo "Checking release readiness for: $RELEASE_VERSION"

REGISTERED_COUNT=$(yq e '.components | length' "$COMPONENTS_FILE")
TOTAL_COUNT=$(yq e '.components | length' configs/components-registry.yaml)

echo "Release Progress: $REGISTERED_COUNT/$TOTAL_COUNT components registered"

if [ "$REGISTERED_COUNT" == "$TOTAL_COUNT" ]; then
  echo "All components registered! Release $RELEASE_VERSION is ready to trigger."
  echo "Use the 'Trigger Release' workflow to start the release process."
else
  MISSING=$((TOTAL_COUNT - REGISTERED_COUNT))
  echo "$MISSING components still need registration for this release."
fi