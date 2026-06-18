# Component Onboarding Guide

Welcome to the ODH Release GitOps system! This guide will help you add your component to the OpenDataHub release process.

## Overview

The ODH release system uses a GitOps approach where component teams register their component versions for each release through automated GitHub workflows. To participate in releases, your component must first be added to the component registry.

**For system architecture details**, see the [Repository Structure Guide](repository-structure.md).
**For release management details**, see the [Release Manager Guide](release-manager-guide.md).

## Prerequisites

Before adding your component to releases, ensure you have:

1. **A stable component**: Your component should be in a releasable state
2. **Semantic versioning**: Your component should follow semantic versioning (e.g., v1.2.3)
3. **GitHub repository**: Your component code should be in a public GitHub repository
4. **Release branches/tags**: Your component should have clear release points (tags or branches)

## Step 1: Add Your Component to the Registry

### Option A: Use the Self-Service Workflow (Recommended)

1. **Navigate to the GitHub Actions tab** in this repository
2. **Find "Onboard Component" workflow** in the workflow list
3. **Click "Run workflow"** and fill in the required information:
   - **Component Name**: Use kebab-case (e.g., `my-awesome-component`)
   - **Display Name**: Human-readable name (e.g., `My Awesome Component`)
   - **Component Type**: Choose `component` for regular components or `image` for container images

4. **Submit the workflow** - this will create a pull request for review
5. **Wait for approval** - ODH release managers will review and approve your request

### Component Naming Guidelines

- Use **kebab-case** (lowercase with hyphens): `my-component`, `data-pipeline`
- Be **descriptive but concise**: `notebook-controller` not `nc`
- Use **namespace prefixes** if needed: `workbenches/kf-notebook-controller`
- **Avoid special characters** except hyphens and forward slashes
- **Maximum 50 characters**

### Component Types

- **`component`**: Regular software components with version tags and branches
- **`image`**: Container images that only have version tags (no branches)

## Step 2: Component Registration Process

Once your component is approved and added to the registry:

1. **Your component appears in the registration workflow** automatically
2. **You can register versions** for each release using the "Register Component" workflow

## Step 3: Participating in Releases

### How Releases Work

ODH follows a release cycle with multiple versions:
- **Stable releases**: e.g., `v3.4.0`
- **Early Access (EA) releases**: e.g., `v3.5.0-ea.1`, `v3.5.0-ea.2`

### Registering Your Component for a Release

1. **Go to GitHub Actions** → "Register Component" workflow
2. **Run the workflow** with:
   - **Component name**: Select your component from the dropdown
   - **Release version**: Leave empty to use current active release (or specify manually)
   - **Component tag**: Component tag (e.g., v1.5.3) - leave empty for branch-based components
   - **Branch name**: Branch name (e.g., release-v2.1) - required for all components

3. **Automated processing**: The workflow will:
   - Validate your inputs
   - Add your component to the release
   - Update the release dashboard
   - Commit the changes to Git

### Component Version Guidelines

**For Tag-Based Components (Most Components):**
- Follow **semantic versioning**: `vMAJOR.MINOR.PATCH` 
- Use **Git tags** for version references (e.g., `v1.2.3`)
- Provide **branch context** for where the tag exists (e.g., `main`, `release-v1.2`)
- **Test thoroughly** before registering for a release

**For Branch-Based Components (e.g., OGX):**
- Use **branch names** for versioning (e.g., `odh`, `release-v2.1`)
- Leave **component tag field empty** during registration
- Still provide **branch name** (same as the version in this case)

**Registration Examples:**
- **Tag-based**: `component_tag: "v2.8.0"`, `branch_name: "main"`
- **Branch-based**: `component_tag: ""`, `branch_name: "odh"`

## Step 4: Monitoring Release Progress

### Release Dashboard

- Check the **main repository README** for overall release status
- View **individual release pages** at `releases/<version>/README.md`
- Track **component registration progress** with visual indicators

### What Happens After Registration

Once you register your component:
1. **Tracking**: Your registration appears in the release dashboard
2. **Validation**: The system validates your component version is accessible
3. **Integration**: When the release is triggered, your component is included in the build
4. **Completion**: You'll be notified when the release is published

**For complete release process details**, see the [Release Process Diagram](release-process-diagram.md).

## Troubleshooting

### Common Issues

**"Component not found in registry"**
- Solution: Use the "Onboard Component" workflow first
- Your component must be approved before you can register versions

**"Invalid component name format"**
- Solution: Use kebab-case naming (lowercase, hyphens only)
- Examples: `my-component`, `workbenches/notebook-controller`

**"Invalid release version format"**
- Solution: Use semantic versioning format
- Examples: `v3.4.0`, `v3.5.0-ea.1`

**"Component already registered for this release"**
- Solution: This updates your existing registration
- You can re-run the workflow to update your component version

### Getting Help

1. **Check the FAQ** section below
2. **Review workflow logs** in GitHub Actions for detailed error messages
3. **Repository guides**: Check the [Repository Structure Guide](repository-structure.md) for technical details
4. **Contact release managers** if you need assistance
5. **Check existing issues** in the repository for known problems

## FAQ

### Q: How long does component approval take?
**A:** Typically 1-3 business days. Release managers review requests during regular business hours.

### Q: Can I update my component information?
**A:** Yes, you can re-register your component for a release to update the version. For registry changes (name, type), contact release managers.

### Q: What if my component isn't ready for a release?
**A:** No problem! You can skip any release and join when ready. The system maintains fallback versions from previous releases.

### Q: Can I register multiple versions?
**A:** You can only have one version per release. Re-registering updates your previous entry for that release.

### Q: What's the difference between component and image types?
**A:** Components have both versions and branches, while images only have version tags. Choose based on your release process.

### Q: How do I know when a release is happening?
**A:** Watch the main repository README and GitHub notifications. Release managers announce upcoming releases.


---

**Next Steps:**
1. Review the prerequisites
2. Use the "Onboard Component" workflow
3. Wait for approval
4. Start registering for releases!

Welcome to the ODH release community!
