#!/bin/bash

# Validate inputs for set-next-release workflow
# Usage: ./validate_set_release_inputs.sh <mode> [release_version] [release_date] [current_version] [current_release_date] [code_freeze_date]

set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <mode> [release_version] [release_date] [current_version] [current_release_date] [code_freeze_date]"
  exit 1
fi

MODE="$1"
RELEASE_VERSION="${2:-}"
RELEASE_DATE="${3:-}"
CURRENT_VERSION="${4:-}"
CURRENT_RELEASE_DATE="${5:-}"
CODE_FREEZE_DATE="${6:-}"

RELEASE_REGEX='^v[0-9]+\.[0-9]+\.[0-9]+(-ea\.[0-9]+)?$'

echo "Validating inputs for mode: $MODE"

# Validate inputs based on mode
if [ "$MODE" == "next_release_only" ] || [ "$MODE" == "both" ]; then
  if [ -z "$RELEASE_VERSION" ]; then
    echo "::error::release_version is required for $MODE mode"
    exit 1
  fi
  if [ -z "$RELEASE_DATE" ]; then
    echo "::error::release_date is required for $MODE mode"
    exit 1
  fi
  if [[ ! "$RELEASE_VERSION" =~ $RELEASE_REGEX ]]; then
    echo "::error::Invalid release version format: '$RELEASE_VERSION'. Expected format: v<major>.<minor>.<patch> or v<major>.<minor>.<patch>-ea.<number> (e.g., v3.4.0, v3.4.0-ea.2)"
    exit 1
  fi
fi

if [ "$MODE" == "current_release_only" ] || [ "$MODE" == "both" ]; then
  if [ -z "$CURRENT_VERSION" ]; then
    echo "::error::current_version is required for $MODE mode"
    exit 1
  fi
  if [ -z "$CURRENT_RELEASE_DATE" ]; then
    echo "::error::current_release_date is required for $MODE mode"
    exit 1
  fi
  if [[ ! "$CURRENT_VERSION" =~ $RELEASE_REGEX ]]; then
    echo "::error::Invalid current version format: '$CURRENT_VERSION'. Expected format: v<major>.<minor>.<patch> or v<major>.<minor>.<patch>-ea.<number> (e.g., v3.4.0, v3.4.0-ea.2)"
    exit 1
  fi
fi

echo "Input validation passed for mode: $MODE"

# Date validation and calculation
echo "Validating and calculating dates..."

# Validate next release dates (if needed)
if [ "$MODE" == "next_release_only" ] || [ "$MODE" == "both" ]; then
  # Validate release date format (cross-platform)
  if ! (date -d "$RELEASE_DATE" >/dev/null 2>&1 || date -j -f "%Y-%m-%d" "$RELEASE_DATE" >/dev/null 2>&1); then
    echo "::error::Invalid release date format: '$RELEASE_DATE'. Expected YYYY-MM-DD format (e.g., 2026-06-01)"
    exit 1
  fi

  # Calculate code freeze date if not provided (3 days before release to get Friday for Monday release)
  if [ -z "$CODE_FREEZE_DATE" ]; then
    CODE_FREEZE_DATE=$(date -d "$RELEASE_DATE - 3 days" +"%Y-%m-%d" 2>/dev/null || date -d "$RELEASE_DATE" -v-3d +"%Y-%m-%d")
    echo "Calculated code freeze date: $CODE_FREEZE_DATE (3 days before release)"
  else
    # Validate provided code freeze date (cross-platform)
    if ! (date -d "$CODE_FREEZE_DATE" >/dev/null 2>&1 || date -j -f "%Y-%m-%d" "$CODE_FREEZE_DATE" >/dev/null 2>&1); then
      echo "::error::Invalid code freeze date format: '$CODE_FREEZE_DATE'. Expected YYYY-MM-DD format"
      exit 1
    fi
    echo "Using provided code freeze date: $CODE_FREEZE_DATE"
  fi

  # Ensure code freeze is before release date
  FREEZE_EPOCH=$(date -d "$CODE_FREEZE_DATE" +%s 2>/dev/null || date -d "$CODE_FREEZE_DATE" +%s)
  RELEASE_EPOCH=$(date -d "$RELEASE_DATE" +%s 2>/dev/null || date -d "$RELEASE_DATE" +%s)

  if [ "$FREEZE_EPOCH" -ge "$RELEASE_EPOCH" ]; then
    echo "::error::Code freeze date ($CODE_FREEZE_DATE) must be before release date ($RELEASE_DATE)"
    exit 1
  fi
fi

# Validate current release date (if needed)
if [ "$MODE" == "current_release_only" ] || [ "$MODE" == "both" ]; then
  if ! (date -d "$CURRENT_RELEASE_DATE" >/dev/null 2>&1 || date -j -f "%Y-%m-%d" "$CURRENT_RELEASE_DATE" >/dev/null 2>&1); then
    echo "::error::Invalid current release date format: '$CURRENT_RELEASE_DATE'. Expected YYYY-MM-DD format (e.g., 2026-06-01)"
    exit 1
  fi
  echo "Validated current release date: $CURRENT_RELEASE_DATE"
fi

# Output for GitHub Actions
if [ -n "${GITHUB_OUTPUT:-}" ]; then
  echo "release_date=$RELEASE_DATE" >> "$GITHUB_OUTPUT"
  echo "code_freeze_date=$CODE_FREEZE_DATE" >> "$GITHUB_OUTPUT"
  echo "current_release_date=$CURRENT_RELEASE_DATE" >> "$GITHUB_OUTPUT"
fi

echo "All validations passed successfully"

# Output to stdout for other consumers
echo "RELEASE_DATE=$RELEASE_DATE"
echo "CODE_FREEZE_DATE=$CODE_FREEZE_DATE"
echo "CURRENT_RELEASE_DATE=$CURRENT_RELEASE_DATE"