#!/bin/bash
set -e

COMPONENT="$1"

if [ -z "$COMPONENT" ]; then
  echo "Error: Component name is required"
  exit 1
fi

# Check kebab-case format
if ! echo "$COMPONENT" | grep -qE '^[a-z0-9]+([a-z0-9-]*[a-z0-9])*([/][a-z0-9]+([a-z0-9-]*[a-z0-9])*)*$'; then
  echo "Error: Component name must be kebab-case (lowercase letters, numbers, hyphens only). Examples: 'my-component', 'workbenches/notebook-controller'"
  exit 1
fi

# Check length limits
if [ ${#COMPONENT} -lt 2 ]; then
  echo "Error: Component name too short (minimum 2 characters)"
  exit 1
fi

if [ ${#COMPONENT} -gt 50 ]; then
  echo "Error: Component name too long (maximum 50 characters)"
  exit 1
fi

# Check for duplicates
if yq e '.components[].name' configs/components-registry.yaml | grep -qx "$COMPONENT"; then
  echo "Error: Component '$COMPONENT' already exists in the registry"
  echo "If you need to update the component information, please contact the release managers"
  exit 1
fi

echo "Component name '$COMPONENT' is valid and unique"