---
name: odh-register
description: Interactively register ODH components for releases with guided questions and validation
user_invocable: true
---

# ODH Component Registration Skill

## Purpose
Guide teams through registering their components for ODH releases using conversational prompts with intelligent defaults and validation. This skill automatically detects the current release, provides hints about versioning patterns, and triggers the established register-component.yaml workflow.

## Usage
- `/odh-register` - Start interactive registration (will ask for component selection)
- `/odh-register <component-name>` - Start registration for specific component

## Conversational Flow

### 1. Component Selection
- If not provided, show available components from registry with search/selection
- Validate component exists in registry
- Show component details and previous registrations for context

### 2. Release Version Detection & Confirmation
- Auto-detect current active release from `configs/release-status.yaml`
- Show release details (version, dates, status)
- Allow user to confirm or specify different release version

### 3. Version/Tag Input with Guidance
- Ask for component version with hints about semantic versioning
- Provide examples from component's previous registrations
- Validate version format and suggest corrections

### 4. Branch Tracking Configuration
- Guide branch selection with hints about typical patterns
- Explain difference between tracking main vs release branches
- Show examples from existing component registrations

### 5. Preview & Confirmation
- Show complete registration summary
- Display what will be updated in release files
- Explain next steps in the release process

## Integration Points

### Existing ODH Infrastructure
- **Release Detection**: Reads `configs/release-status.yaml` for current active release
- **Component Registry**: Uses `configs/components-registry.yaml` for component validation
- **Previous Registrations**: Analyzes `releases/{version}/components.yaml` for context
- **Workflow**: Triggers existing `register-component.yaml` GitHub Actions workflow
- **Validation**: Uses existing component and version validation patterns

### Preserves Existing Process
- Same YAML structure and update patterns
- Identical audit trail through Git commits
- No modifications to existing workflows
- Maintains all current validation rules

## Example Interaction

```
User: /odh-register dashboard

Claude: I'll help you register dashboard for an ODH release.

Current Release Status:
   - Active Release: v3.5.0
   - Status: scheduled (accepting registrations)
   - Release Date: 2026-07-15
   - Code Freeze: 2026-07-12

Register dashboard for v3.5.0? [Yes/No/Other]
   Hint: This is the current active release accepting component registrations

User: Yes

What version/tag are you registering?
   Hint: Usually semantic version like "v2.8.0" 
   Previous registrations: v2.7.0 (v3.4.0), v2.6.0 (v3.3.0)
   Check your component repo for latest tags: https://github.com/opendatahub-io/odh-dashboard/tags

User: v2.8.0

What branch should we track?
   Hint: Usually "main" for latest development, or "release-v2.8" for stable releases
   This tells the release system which branch to monitor for changes
   Previous: "main" (v3.4.0), "release-v2.7" (v3.3.0)

User: release-v2.8

Ready to register:
   - Component: dashboard (OpenDataHub Dashboard)
   - Version: v2.8.0
   - Branch: release-v2.8  
   - Release: v3.5.0
   - Registration: Will update releases/v3.5.0/components.yaml

This will make dashboard v2.8.0 available for the v3.5.0 ODH release.

Shall I register this component? [Yes/No]

User: Yes

Registering component...
   ✓ Updated releases/v3.5.0/components.yaml
   ✓ Committed changes to git
   
Registration complete! Dashboard v2.8.0 is now registered for ODH v3.5.0.
Next: The release will include your component when triggered.
```

## Error Handling & Guidance

### Component Not Found
- Show available components from registry with fuzzy search
- Guide users to use `/odh-onboard` if component needs to be added
- Provide links to component registry documentation

### Invalid Release States
- Explain current release status and what registrations are allowed
- Guide users on timing for registration (before code freeze)
- Show upcoming release schedule if current release is closed

### Version/Branch Validation
- Real-time feedback on version format with correction suggestions
- Branch existence validation with helpful error messages
- Conflict detection with existing registrations

### Workflow Execution Issues
- Clear error messages for GitHub API failures
- Fallback guidance for manual workflow execution
- Links to troubleshooting documentation

## Implementation Details

### Required Tools & Scripts
- **Python script**: `.claude/skills/odh-register/scripts/register.py`
- **Release state reader**: Parse current release status and component registrations
- **GitHub API integration**: Trigger existing register-component workflow
- **Validation integration**: Component and version format checking

### Dependencies
- Read access to `configs/release-status.yaml`
- Read access to `configs/components-registry.yaml`
- Read access to `releases/{version}/components.yaml`
- GitHub API permissions for workflow triggering
- Existing GitHub App authentication infrastructure

### Data Sources
- **Current Release**: `configs/release-status.yaml` → `current_release` field
- **Component Registry**: `configs/components-registry.yaml` → available components
- **Registration History**: `releases/{version}/components.yaml` → previous versions
- **GitHub Repository**: Component repo links for tag/branch verification

## Intelligent Features

### Smart Defaults
- Auto-detect current active release
- Suggest version increments based on previous registrations
- Default to common branch patterns based on component history

### Contextual Hints
- Show component's previous registration patterns
- Provide links to component repositories for tag verification
- Explain release timeline and deadline context

### Validation Integration
- Use existing component validation from registry
- Leverage release state validation for timing
- Check branch/tag format using established patterns

## Future Enhancements
- Branch/tag existence verification via GitHub API
- Automatic detection of new versions from component repositories
- Batch registration support for multiple components
- Integration with release triggering workflow for seamless handoff
- Notification when component is included in actual release build