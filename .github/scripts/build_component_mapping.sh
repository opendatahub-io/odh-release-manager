#!/bin/bash

# Build component mapping with previous release fallback
# Usage: ./build_component_mapping.sh <release_version>

set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Usage: $0 <release_version>"
  exit 1
fi

RELEASE_VERSION="$1"
RELEASE_DIR="releases/$RELEASE_VERSION"
COMPONENTS_FILE="$RELEASE_DIR/components.yaml"

echo "Building component mapping for release: $RELEASE_VERSION"

# Initialize component mapping and tracking
COMPONENT_MAP="{}"
INCLUDED_COMPONENTS=""
FALLBACK_COMPONENTS=""
SKIPPED_COMPONENTS=""

# Get previous release component data for fallback
PREVIOUS_COMPONENTS="{}"
RELEASE_HISTORY_COUNT=0
if [ -f "configs/release-status.yaml" ]; then
  PREVIOUS_COMPONENTS=$(yq e '.release_history[0].components // {}' configs/release-status.yaml)
  RELEASE_HISTORY_COUNT=$(yq e '.release_history | length' configs/release-status.yaml)
fi

# Detect bootstrap scenario
if [ "$RELEASE_HISTORY_COUNT" -eq 0 ]; then
  echo ""
  echo "BOOTSTRAP RELEASE DETECTED"
  echo "This appears to be the first release in this GitOps system"
  echo " All components must be explicitly registered - no fallback available"
  echo " Unregistered components will be SKIPPED from release"
  echo ""
else
  echo "Previous release components available for fallback:"
  echo "$PREVIOUS_COMPONENTS" | jq '.'
  echo ""
fi

# Process each component in registry
echo "Processing components from registry..."
echo ""

while IFS= read -r component_line; do
  # Parse component name and display name from registry
  component=$(echo "$component_line" | yq e '.name' -)
  display_name=$(echo "$component_line" | yq e '.display_name' -)

  # Check if component is registered in current release
  CURRENT_VERSION=$(yq e ".components[] | select(.name == \"$component\") | .version" "$COMPONENTS_FILE" 2>/dev/null || echo "")

  if [ -n "$CURRENT_VERSION" ]; then
    echo "INCLUDED (current): $component = $CURRENT_VERSION"
    COMPONENT_MAP=$(echo "$COMPONENT_MAP" | jq --arg comp "$component" --arg version "$CURRENT_VERSION" --arg display "$display_name" \
      '. + {($comp): {"ref": $version, "display_name": $display}}')
    INCLUDED_COMPONENTS="$INCLUDED_COMPONENTS $component"
  else
    # Try fallback from previous release - check if previous components had enhanced structure
    PREVIOUS_VERSION=""
    if echo "$PREVIOUS_COMPONENTS" | jq -e ".\"$component\".ref" >/dev/null 2>&1; then
      # Previous release had enhanced structure
      PREVIOUS_VERSION=$(echo "$PREVIOUS_COMPONENTS" | jq -r ".\"$component\".ref // \"\"")
    else
      # Previous release had simple structure
      PREVIOUS_VERSION=$(echo "$PREVIOUS_COMPONENTS" | jq -r ".\"$component\" // \"\"")
    fi

    if [ -n "$PREVIOUS_VERSION" ] && [ "$PREVIOUS_VERSION" != "null" ]; then
      echo "INCLUDED (fallback): $component = $PREVIOUS_VERSION"
      COMPONENT_MAP=$(echo "$COMPONENT_MAP" | jq --arg comp "$component" --arg version "$PREVIOUS_VERSION" --arg display "$display_name" \
        '. + {($comp): {"ref": $version, "display_name": $display}}')
      FALLBACK_COMPONENTS="$FALLBACK_COMPONENTS $component"
    else
      echo "SKIPPED: $component (not registered, no fallback available)"
      SKIPPED_COMPONENTS="$SKIPPED_COMPONENTS $component"
    fi
  fi
done < <(yq e '.components[] | select(.type == "component")' configs/components-registry.yaml -o=json | jq -c '.')

echo ""
echo "COMPONENT MAPPING SUMMARY"
echo ""

# Count components for summary
TOTAL_COMPONENTS=$(yq e '.components | length' configs/components-registry.yaml)
INCLUDED_COUNT=$(echo "$COMPONENT_MAP" | jq 'length')
CURRENT_COUNT=$(echo "$INCLUDED_COMPONENTS" | wc -w)
FALLBACK_COUNT=$(echo "$FALLBACK_COMPONENTS" | wc -w)
SKIPPED_COUNT=$(echo "$SKIPPED_COMPONENTS" | wc -w)

echo "Total components in registry: $TOTAL_COMPONENTS"
echo "Components included in release: $INCLUDED_COUNT"
echo "  - Current registrations: $CURRENT_COUNT"
echo "  - Fallback from previous: $FALLBACK_COUNT"
echo "Components SKIPPED: $SKIPPED_COUNT"

if [ "$SKIPPED_COUNT" -gt 0 ]; then
  echo ""
  echo " WARNING: The following components will be SKIPPED from release:"
  for component in $SKIPPED_COMPONENTS; do
    echo "  - $component"
  done
  echo ""
  echo " These components will NOT be included in the release build!"
  echo " External workflows will NOT receive version data for these components!"
  echo " Consider registering these components or verifying this is intentional!"
fi

if [ "$FALLBACK_COUNT" -gt 0 ] && [ "$RELEASE_HISTORY_COUNT" -gt 0 ]; then
  echo ""
  echo "INFO: The following components using previous release versions:"
  for component in $FALLBACK_COMPONENTS; do
    # Handle both enhanced and simple structure for display
    if echo "$PREVIOUS_COMPONENTS" | jq -e ".\"$component\".ref" >/dev/null 2>&1; then
      prev_version=$(echo "$PREVIOUS_COMPONENTS" | jq -r ".\"$component\".ref // \"\"")
    else
      prev_version=$(echo "$PREVIOUS_COMPONENTS" | jq -r ".\"$component\" // \"\"")
    fi
    echo "  - $component = $prev_version"
  done
fi

echo ""
echo "FINAL COMPONENT MAPPING"
echo "$COMPONENT_MAP" | jq '.'
echo ""

# Output the component mapping for GitHub Actions
if [ -n "${GITHUB_OUTPUT:-}" ]; then
  echo "mapping<<EOF" >> "$GITHUB_OUTPUT"
  echo "$COMPONENT_MAP" >> "$GITHUB_OUTPUT"
  echo "EOF" >> "$GITHUB_OUTPUT"
fi

echo "Component mapping build completed successfully"
