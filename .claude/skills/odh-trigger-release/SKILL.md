---
name: odh-trigger-release
description: Intelligently trigger ODH releases with component readiness preview and fallback guidance
user_invocable: true
---

# ODH Trigger Release Skill

## Purpose
Guide release managers through triggering ODH releases with intelligent component readiness assessment and fallback preview. This skill leverages existing component mapping logic to show exactly what will be included in the release and helps make informed decisions about proceeding with fallbacks or waiting for missing registrations.

## Usage
- `/odh-trigger-release` - Check release readiness and trigger current release
- `/odh-trigger-release <version>` - Trigger specific release version

## Conversational Flow

### 1. Release Identification & Status Check
- Auto-detect current active release or ask for version
- Show release status, timeline, and registration deadline context
- Validate release is in appropriate state for triggering

### 2. Component Readiness Assessment
- Use existing `check_release_readiness.sh` for component status
- Parse `build_component_mapping.sh` for fallback preview
- Show registered vs fallback vs missing components with clear categorization

### 3. Fallback Intelligence Display
- Show detailed fallback information for unregistered components
- Explain which previous release versions will be used
- Provide context about fallback component versions and their stability

### 4. Decision Guidance
- Present clear options based on readiness assessment
- Guide decision making with component team notification suggestions
- Show impact of proceeding vs waiting

### 5. Execution with Monitoring Setup
- Trigger existing workflow with gathered information
- Provide external staging monitoring links
- Set up tracking for release progression

## Integration Points

### Existing ODH Infrastructure
- **Readiness Check**: Uses existing `.github/scripts/check_release_readiness.sh`
- **Component Mapping**: Leverages `.github/scripts/build_component_mapping.sh` fallback logic
- **Release Status**: Reads current release from `configs/release-status.yaml`
- **Workflow**: Triggers existing `trigger-release.yaml` GitHub Actions workflow
- **Monitoring**: Tracks external workflow URLs for staging progress

### Preserves Existing Process
- Same trigger workflow and inputs
- Identical fallback logic and component resolution
- No changes to existing release mechanics
- Maintains audit trail and external integration

## Example Interaction

```
User: /odh-trigger-release

Claude: I'll check release readiness and help trigger the release.

Current Release: v3.5.0
   - Status: scheduled (ready for triggering)
   - Release Date: 2026-07-15
   - Days until release: 12

Checking component registration status...

Component Readiness Assessment:

Registered (15/19):
   • dashboard v2.8.0 (release-v2.8 branch)
   • workbenches/notebooks v1.9.0 (main branch)  
   • model-serving v2.1.0 (release-v2.1 branch)
   • kserve v1.8.0 (main branch)
   ... 11 more

Will use fallback (4/19):
   • ray → v2.0.0 from v3.4.0 release
   • trustyai → v1.2.0 from v3.4.0 release  
   • authorino → v0.8.0 from v3.4.0 release
   • codeflare → v1.5.0 from v3.4.0 release

No previous versions (0/19): None

15/19 components ready (79%). Proceed with fallbacks for missing components?

   Hint: Fallbacks use stable versions from previous release (v3.4.0)
   You can register missing components first, or proceed with fallbacks

   Options:
   1. Proceed with fallbacks (trigger release now)
   2. Wait for missing registrations  
   3. Show detailed fallback information first
   4. Notify component teams about missing registrations

User: 3

Detailed Fallback Information:

ray (Ray Cluster):
   - Will use: v2.0.0 from v3.4.0 release
   - Age: 2 months old
   - Status: Stable, last known working version
   - Team: @ray-team (GitHub: ray-project/kuberay-operator)

trustyai (TrustyAI):  
   - Will use: v1.2.0 from v3.4.0 release
   - Age: 2 months old
   - Status: Stable, includes security fixes
   - Team: @trustyai-team (GitHub: trustyai-explainability/trustyai-service-operator)

authorino (Authorino):
   - Will use: v0.8.0 from v3.4.0 release  
   - Age: 2 months old
   - Status: Stable, compatible with current ODH
   - Team: @authorino-team (GitHub: kuadrant/authorino-operator)

codeflare (CodeFlare):
   - Will use: v1.5.0 from v3.4.0 release
   - Age: 2 months old  
   - Status: Stable, core functionality maintained
   - Team: @codeflare-team (GitHub: project-codeflare/codeflare-operator)

All fallback versions are stable and tested. Trigger release with these fallbacks?

   Options:
   1. Yes, trigger release with fallbacks
   2. No, wait for team registrations
   3. Notify teams first, then decide

User: 1

Triggering v3.5.0 release...
   • 15 registered components
   • 4 fallback components  
   • 0 missing components

Release triggered successfully!
   
Monitoring Information:
   • External staging: https://github.com/opendatahub-io/opendatahub-operator/actions/runs/12345
   • Release tracking: Updated configs/release-status.yaml
   • Status: awaiting_validation

Next steps:
1. Monitor external staging progress (~30-45 minutes)
2. QE validation when staging completes  
3. Community release trigger after validation approval

Use /odh-monitor-community to track progress automatically.
```

## Error Handling & Guidance

### No Active Release
- Clear explanation of release status and timing
- Guidance on using `/odh-set-next-release` to plan releases
- Links to release documentation and process

### Release Not Ready for Triggering
- Explain current release status and what's needed
- Show timeline and deadline context
- Guide on registration process for missing components

### Component Readiness Issues
- Detailed breakdown of missing vs fallback components
- Suggestions for component team outreach
- Impact assessment of proceeding vs waiting

### Workflow Execution Issues
- Clear error messages for GitHub API failures
- Fallback guidance for manual workflow execution
- Links to staging monitoring and troubleshooting

## Implementation Details

### Required Tools & Scripts
- **Python script**: `.claude/skills/odh-trigger-release/scripts/trigger.py`
- **Readiness integration**: Wrapper for existing release readiness checks
- **Mapping logic**: Integration with component fallback resolution
- **GitHub API**: Workflow triggering and external URL tracking

### Dependencies
- Access to `.github/scripts/check_release_readiness.sh`
- Access to `.github/scripts/build_component_mapping.sh`  
- Read/write access to `configs/release-status.yaml`
- GitHub API permissions for workflow triggering
- External repository monitoring capabilities

### Intelligent Features
- **Component categorization**: Registered vs fallback vs missing
- **Fallback preview**: Version ages, stability assessment, team context
- **Decision support**: Impact analysis and recommendation guidance
- **Monitoring setup**: Automatic tracking of external workflows

## Component Intelligence

### Readiness Assessment
- Parse component registration completeness
- Categorize components by availability status
- Calculate readiness percentages for decision support

### Fallback Analysis  
- Use existing fallback logic from build_component_mapping.sh
- Show version ages and stability context
- Provide team contact information for missing registrations

### Impact Evaluation
- Assess release quality with current component set
- Highlight critical vs optional missing components
- Guide decision making with historical context

## Future Enhancements
- Automatic component team notification for missing registrations
- Integration with component health monitoring for fallback assessment
- Predictive analysis for optimal release timing
- Advanced conflict detection between component versions