#!/bin/bash
# update-workflow-dropdown.sh - Reusable script for updating workflow dropdown options
# Usage: update-workflow-dropdown.sh <workflow-file> <input-name> <options-json>
# Example: update-workflow-dropdown.sh .github/workflows/validate-release.yaml release_version '["v3.4.0"]'

set -euo pipefail

# Check arguments
if [ $# -ne 3 ]; then
    echo "Usage: $0 <workflow-file> <input-name> <options-json>"
    echo "Example: $0 .github/workflows/validate-release.yaml release_version '[\"v3.4.0\"]'"
    exit 1
fi

WORKFLOW_FILE="$1"
INPUT_NAME="$2"
OPTIONS_JSON="$3"

# Validate workflow file exists
if [[ ! -f "$WORKFLOW_FILE" ]]; then
    echo "Error: Workflow file not found: $WORKFLOW_FILE"
    exit 1
fi

# Validate JSON format
if ! echo "$OPTIONS_JSON" | jq empty 2>/dev/null; then
    echo "Error: Invalid JSON format in options: $OPTIONS_JSON"
    exit 1
fi

echo "Updating dropdown in $WORKFLOW_FILE"
echo "Input: $INPUT_NAME"
echo "Options: $OPTIONS_JSON"

# Update the workflow file using yq
yq e ".on.workflow_dispatch.inputs.$INPUT_NAME.options = $OPTIONS_JSON" -i "$WORKFLOW_FILE"

echo "Dropdown updated successfully"