# Claude Code Skills for ODH Release Management

This document describes the conversational Claude Code skills available for ODH release management. These skills provide natural language interfaces to existing GitHub workflows, making complex release processes more accessible while preserving all GitOps functionality.

## Overview

The ODH Release Skills transform complex GitHub Actions workflows into guided conversational experiences. Instead of navigating multi-field forms, teams can use natural language to accomplish release tasks with intelligent guidance and real-time validation.

## Available Skills

### Component Teams

#### `/odh-onboard` - Component Onboarding
Add new components to ODH through guided conversation.

**When to use**: First-time component registration, adding new services to ODH ecosystem

**Example usage**:
```bash
/odh-onboard my-ai-service
```

**What it provides**:
- Real-time name validation (kebab-case format)
- Conflict detection against existing registry
- Component type guidance (component vs image)
- Display name suggestions with examples
- Automated PR creation for approval workflow

#### `/odh-register` - Component Registration
Register component versions for ODH releases.

**When to use**: Before release deadlines, updating component versions for upcoming releases

**Example usage**:
```bash
/odh-register dashboard
```

**What it provides**:
- Auto-detection of current active release
- Version format validation and guidance
- Branch tracking configuration
- Registration history context
- Preview before execution

### Release Managers

#### `/odh-set-next-release` - Release Planning
Plan and configure upcoming ODH releases with intelligent date calculations.

**When to use**: Setting release schedules, planning release timelines

**Example usage**:
```bash
/odh-set-next-release v3.6.0
```

**What it provides**:
- Intelligent code freeze calculation (release - 3 days)
- Business day awareness and weekend handling
- Mode selection guidance (next/current/both)
- Release history context
- Date validation and timeline checks

#### `/odh-trigger-release` - Smart Release Triggering
Trigger releases with component readiness assessment and fallback guidance.

**When to use**: Initiating release process, checking component readiness

**Example usage**:
```bash
/odh-trigger-release
```

**What it provides**:
- Component readiness assessment (registered/fallback/missing)
- Intelligent fallback preview using existing logic
- Decision guidance for missing components
- Team contact information for follow-up
- External staging monitoring setup

#### `/odh-monitor-community` - Community Release Monitoring
Monitor community release progress with automated PR tracking.

**When to use**: Tracking community operator catalog releases, automating release completion

**Example usage**:
```bash
/odh-monitor-community
```

**What it provides**:
- Automated GitHub PR status monitoring
- Merge detection with notifications
- Progress timeline estimation
- Release completion workflow integration
- Real-time status updates

## Getting Started

### Prerequisites
- Claude Code CLI or IDE extension installed
- Access to ODH release repository
- Existing GitHub App authentication (automatically reused)

### First Time Setup
No additional setup required! Skills automatically use existing ODH infrastructure:
- GitHub workflows remain unchanged
- YAML configurations preserved
- Authentication tokens reused
- Validation scripts integrated

### Basic Workflow
1. **Component teams**: Start with `/odh-onboard` for new components
2. **Register components**: Use `/odh-register` before release deadlines
3. **Plan releases**: Release managers use `/odh-set-next-release`
4. **Trigger releases**: Use `/odh-trigger-release` when ready
5. **Monitor completion**: Track with `/odh-monitor-community`

## Skill Features

### Intelligent Guidance
- **Context-aware hints** based on current system state
- **Real-time validation** using existing validation scripts
- **Smart defaults** from release history and patterns
- **Error prevention** with immediate feedback

### Existing Infrastructure Integration
- **Component registry** for dropdown sync and conflict detection
- **Release status** for current release detection and timeline awareness
- **Component mapping** for fallback logic and readiness assessment
- **Date intelligence** for business day calculations and freeze timing

### Conversational Flow Benefits
- **Natural language** instead of complex GitHub Actions forms
- **Progressive disclosure** of information as needed
- **Helpful examples** from existing ODH components
- **Graceful error handling** with recovery suggestions

## Comparison with Manual Workflows

| Task | Manual Process | With Skills |
|------|----------------|-------------|
| Component Onboarding | Navigate to GitHub Actions → Fill 3-field form → Submit | `/odh-onboard component-name` → Guided conversation |
| Component Registration | Find current release → Navigate to workflow → Fill 4-field form | `/odh-register component-name` → Auto-detects release, guides inputs |
| Release Planning | Calculate dates → Navigate to workflow → Choose from 3 modes | `/odh-set-next-release` → Explains modes, calculates dates |
| Release Triggering | Check component readiness manually → Navigate to workflow | `/odh-trigger-release` → Shows readiness preview, guides decisions |
| Community Monitoring | Manual PR checking → Multiple repo monitoring | `/odh-monitor-community` → Automated tracking with notifications |

## Advanced Usage

### Skill Chaining
Skills work together seamlessly for complete workflows:
```bash
/odh-onboard new-component     # 1. Add to registry
# (wait for approval)
/odh-register new-component    # 2. Register for release
/odh-set-next-release v3.7.0   # 3. Plan next release
/odh-trigger-release          # 4. Start release
/odh-monitor-community        # 5. Track completion
```

### Error Recovery
- All skills provide fallback options to manual workflows
- Clear error messages with specific guidance
- Integration with existing ODH documentation
- Graceful degradation when external services unavailable

### Monitoring and Notifications
- Real-time status updates during long-running processes
- Progress indicators with estimated completion times
- Automatic detection of state changes
- Intelligent notification timing to avoid spam

## Technical Details

### Implementation
- **Python scripts** for core logic and GitHub API integration
- **yq integration** for YAML parsing using existing ODH patterns
- **Subprocess calls** to existing validation scripts
- **GitHub API** for workflow triggering and status monitoring

### Security and Permissions
- **No new authentication** required - reuses existing GitHub App tokens
- **Same permissions** as existing manual workflows
- **Identical audit trails** through Git commits
- **Preserved validation** using existing script infrastructure

### Reliability
- **Fallback to manual workflows** always available
- **No disruption** to existing processes or automation
- **Read-only operations** for status and validation checking
- **Explicit confirmation** before any state-changing operations

## Troubleshooting

### Common Issues

**"No active release found"**
- Use `/odh-set-next-release` to configure a release first
- Check `configs/release-status.yaml` for current status

**"Component not found"**
- Use `/odh-onboard` to add component to registry first
- Verify component name spelling and format

**"Release not ready for triggering"**
- Check release status - must be in "scheduled" state
- Verify component registrations are complete

**"Invalid version format"**
- Use semantic versioning: `v2.8.0` or `v3.0.0-ea.1`
- Check examples from existing component registrations

### Getting Help
- Each skill provides contextual help and examples
- Error messages include specific guidance and next steps
- Manual workflows remain available as backup options
- Integration with existing ODH documentation and processes

## Future Enhancements

Planned improvements to the skills system:

- **Team notifications** via Slack/email integration
- **Batch operations** for multi-component management
- **Calendar integration** for release conflict detection
- **Advanced monitoring** with health checks and dependency tracking
- **Rollback support** with automated failure detection

These skills represent a new approach to developer tooling: enhancing existing automation with conversational intelligence rather than replacing proven GitOps processes.