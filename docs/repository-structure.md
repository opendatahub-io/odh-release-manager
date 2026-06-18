# Repository Structure & Architecture Guide

This guide explains the technical architecture and organizational structure of the ODH Release Manager repository. It's designed for repository maintainers, system architects, and anyone who needs to understand how the release system works internally.

## Repository Overview

The ODH Release Manager repository implements a declarative, audit-friendly approach to managing ODH community releases. The system uses GitOps principles where all state changes are tracked in Git commits, provides self-service component registration, and coordinates with external workflows in the opendatahub-operator repository.

## Directory Structure

```
odh-release-manager/
├── .github/
│   ├── workflows/           # GitHub Actions workflows (7 files)
│   │   ├── trigger-release.yaml
│   │   ├── validate-release.yaml
│   │   ├── complete-release.yaml
│   │   ├── register-component.yaml
│   │   ├── set-next-release.yaml
│   │   └── sync-component-dropdown.yaml
│   ├── scripts/            # Build and validation scripts
│   │   ├── build_component_mapping.sh
│   │   ├── check_release_readiness.sh
│   │   ├── readme_manager.py
│   │   └── update-workflow-dropdown.sh
│   └── CODEOWNERS         # Repository ownership
├── configs/               # System configuration
│   ├── components-registry.yaml    # Master component registry
│   └── release-status.yaml         # Current release state
├── releases/              # Per-release tracking
│   ├── v3.5.0-ea.1/
│   │   ├── components.yaml # Component registrations for this release
│   │   └── README.md       # Release-specific documentation
│   └── v3.5.0/            # Additional release versions...
├── docs/                  # User documentation
│   ├── component-onboarding.md
│   ├── release-validation-guide.md
│   ├── release-manager-guide.md
│   └── repository-structure.md (this file)
└── README.md             # Main entry point
```


## Configuration Files

### `configs/components-registry.yaml`

Master registry of all ODH components with metadata including name, display name, type, and optional description/repository/maintainer information. Referenced by registration workflows and used to validate component registrations.

### `configs/release-status.yaml`

Central state management containing current release status, next release configuration, and release history. Tracks release progression through statuses: `scheduled` → `awaiting_validation` → `in_progress_community_release` → `completed` (or `failed`).

### `releases/{version}/components.yaml`

Per-release component tracking with component name, version/branch reference, registration timestamp, and type (tag-based, branch-based, or image-based).

## Workflow Architecture

The system uses GitHub Actions workflows organized into three categories:

**User-Facing Workflows**: Component registration, release triggering, release validation, release completion  
**Administrative Workflows**: Next release setup, dropdown synchronization  
**External Integrations**: Trigger external processes in `opendatahub-operator` for staging and community release

## Data Flow

**Component Registration**: Teams register → validate against registry → store in `releases/{version}/components.yaml`

**Release Trigger**: Check readiness → build component mapping → trigger external staging → update status to `awaiting_validation`

**Release Validation**: Validate release → record signoff → update to `in_progress_community_release` → trigger community release → monitor completion → auto-complete on success

**State Transitions**: `scheduled` → `awaiting_validation` → `in_progress_community_release` → `completed` (or `failed` at any stage)

## External Integrations

Coordinates with `opendatahub-operator` workflows: `release-staging.yaml` (triggered by release trigger) builds and stages releases, while `release-community.yaml` (triggered by release validation) creates community operators PRs.

Authentication uses GitHub App tokens for external repository triggers and PAT tokens for workflow file modifications.

## Git Strategy

Every system action creates a Git commit for audit trail. All work happens on the main branch with direct commits (no feature branches). Commit messages follow format: `action-type: brief description`.

## System Design Principles

**Declarative State Management**: System state declared in YAML files, Git commits represent state transitions  
**Separation of Concerns**: Component teams register, release managers trigger, validation is performed, automation handles transitions  
**External Integration**: Loosely coupled with external systems, failure isolation and retry logic  
**Audit Trail**: Complete Git history, signed commits, access control via GitHub permissions

## Maintenance and Customization

**Adding Components**: Update `configs/components-registry.yaml`, sync dropdowns via workflow, test registration  
**Workflow Changes**: Validate YAML, update documentation, coordinate deployment  
**Monitoring**: GitHub Actions logs, YAML state files, Git audit trail  
**Backup**: Git-based system state, configuration restore via Git checkout  
**Security**: GitHub secrets for tokens, access control via repository permissions