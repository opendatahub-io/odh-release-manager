# ODH Release Manager

This repository manages the OpenDataHub release process through GitOps principles.

## Current Release Status

**No active release**

## Recent Release History

| Version | Status | Triggered | Released | Validation | Links |
|---------|--------|-----------|----------|------------|--------|
| | | | | | |

*No releases yet. Release history will appear here after the first release is triggered.*

## Usage

### **Recommended: Claude Code Skills**
Use conversational skills for guided workflows: **[Skills Documentation](docs/claude-code-skills.md)**

### **Alternative: Manual GitHub Workflows**

#### For New Component Teams
1. **Add your component**: Use the [Onboard Component](https://github.com/opendatahub-io/odh-release-manager/actions/workflows/onboard-component.yaml) workflow
2. **Wait for approval**: Release managers will review and approve your component request
3. **Start participating**: Once approved, register versions using the Register Component workflow
4. **Need help?**: See the [Component Onboarding Guide](docs/component-onboarding.md)

#### For Existing Component Teams
1. **Register your component**: Use the [Register Component](https://github.com/opendatahub-io/odh-release-manager/actions/workflows/register-component.yaml) workflow
   - Select your component from the dropdown (auto-synced with registry)
   - Release version auto-detected from current active release (or specify manually)
2. **Track registration**: Check component status in release README: `./releases/<version>/README.md`

#### For Release Managers
1. **Trigger release**: Use the [Trigger Release](https://github.com/opendatahub-io/odh-release-manager/actions/workflows/trigger-release.yaml) workflow
2. **Monitor progress**: Check status updates in this README and external workflow links
3. **Review new components**: Approve component addition requests via pull requests

## Repository Structure
```
├── configs/
│   ├── components-registry.yaml    # Master component registry (source of truth)
│   └── release-status.yaml         # Current and historical release status
├── releases/
│   └── <version>/
│       ├── components.yaml         # Registered components for this release
│       └── README.md              # Per-release component status
├── docs/
│   ├── claude-code-skills.md       # Claude Code skills documentation
│   └── component-onboarding.md     # Guide for new component teams
└── .github/
    ├── CODEOWNERS                  # Required reviewers for sensitive files
    ├── pull_request_template.md    # PR template for component additions
    ├── scripts/
    │   ├── validate-component-name.sh  # Component name validation
    │   └── validate-display-name.sh    # Display name validation
    └── workflows/
        ├── register-component.yaml     # Component registration workflow
        ├── onboard-component.yaml          # Self-service component onboarding
        ├── sync-component-dropdown.yaml    # Auto-sync dropdown with registry
        ├── trigger-release.yaml            # Release trigger workflow
        └── complete-release.yaml           # Release completion workflow
```

## How It Works

### Component Registration Flow
1. Component teams use the "Register Component" workflow to register their component version for a release
   - Dropdown automatically synced with approved components from the registry
2. Data is stored in `releases/<version>/components.yaml` with validation against the component registry
3. Per-release README is auto-generated showing registration progress

### Component Onboarding Flow
1. New teams use "Onboard Component" workflow to request component addition
2. Automated PR created for registry update and review by release managers
3. Once approved, "Sync Component Dropdown" automatically updates registration workflow
4. Component immediately available in registration dropdown

### Release Trigger Flow
1. Release managers use the "Trigger Release" workflow when components are ready
2. System automatically fills missing components from the previous release (fallback)
3. Complete component mapping is passed to `opendatahub-operator/release-staging.yaml`
4. External workflow builds and creates the actual release
5. Status is tracked and displayed in this README

### Previous Release Fallback
If a component is not registered for the current release, the system automatically uses the version from the most recent completed release. This ensures no components are accidentally excluded from releases.
