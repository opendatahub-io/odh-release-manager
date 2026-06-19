---
name: odh-set-next-release
description: Interactively plan ODH releases with guided date calculations and mode selection
user_invocable: true
---

# ODH Set Next Release Skill

## Purpose
Guide release managers through ODH release planning using conversational prompts with intelligent date calculations and mode explanations. This skill simplifies the complex set-next-release workflow by explaining the three modes, auto-calculating code freeze dates, and providing smart defaults based on release history.

## Usage
- `/odh-set-next-release` - Start interactive release planning
- `/odh-set-next-release <version>` - Start with pre-filled version

## Conversational Flow

### 1. Release Version Input & Validation
- Ask for next release version with semantic versioning guidance
- Validate version format (v3.6.0, v3.6.0-ea.1, etc.)
- Check against existing release history for logical progression

### 2. Release Date Planning
- Ask for target release date with format guidance (YYYY-MM-DD)
- Explain typical ODH release patterns (Tuesdays, monthly cadence)
- Validate dates are in the future and reasonable

### 3. Code Freeze Date Intelligence
- Auto-calculate code freeze date (3 days before release)
- Show calculated date with day of week
- Allow custom override if needed
- Handle weekends and business day logic

### 4. Mode Selection with Clear Explanations
- Explain the three modes with examples:
  - `next_release_only` - Just plan next release (most common)
  - `current_release_only` - Update current release info
  - `both` - Update both current and next
- Provide guidance on when to use each mode
- Show current release status for context

### 5. Preview & Confirmation
- Show complete configuration before execution
- Explain what will be updated in release-status.yaml
- Display timeline and key dates

## Integration Points

### Existing ODH Infrastructure
- **Date Logic**: Uses existing date calculation patterns from `validate_set_release_inputs.sh`
- **Release Status**: Updates `configs/release-status.yaml` structure
- **Workflow**: Triggers existing `set-next-release.yaml` GitHub Actions workflow
- **Validation**: Leverages existing input validation and business day logic

### Preserves Existing Process
- Same YAML structure and field names
- Identical workflow inputs and execution
- No changes to existing validation rules
- Maintains audit trail through Git commits

## Example Interaction

```
User: /odh-set-next-release

Claude: I'll help you set up the next ODH release. Let me gather the details:

What's the next release version?
   Hint: Use semantic versioning like "v3.6.0" or early access "v3.6.0-ea.1"
   Recent releases: v3.5.0, v3.4.0, v3.3.0

User: v3.6.0

What's the target release date?
   Hint: Format as YYYY-MM-DD, usually Tuesdays for ODH releases
   Typical cadence: Monthly releases

User: 2026-07-15

Code freeze date will be 3 days before: July 12 (Friday)
   Is this acceptable? [Yes/No/Custom]
   Hint: Code freeze is when component registrations close

User: Yes

Current Release Status:
   - Current: No active release
   - Next: Not configured

What should I update?
   Options:
   1. Set next release only (recommended for planning)
   2. Update current release info too  
   3. Update both current and next
   
   Hint: Use option 1 for initial planning, option 3 if current release needs updating

User: 1

Ready to configure:
   - Next Release: v3.6.0 on July 15, 2026
   - Code Freeze: July 12, 2026 (Friday)
   - Mode: next_release_only
   - Will enable: next_release planning

This will set up v3.6.0 as the next planned ODH release.

Shall I configure this release? [Yes/No]

User: Yes

Configuring release...
   ✓ Updated configs/release-status.yaml
   ✓ Set next_release.enabled = true
   ✓ Committed changes to git

Release planning complete! v3.6.0 is now planned for July 15, 2026.
Next: Teams can start registering components for this release.
```

## Error Handling & Guidance

### Invalid Version Formats
- Real-time validation with specific format examples
- Suggestions for valid semantic versioning
- Check against existing release progression

### Date Validation Issues
- Past dates rejected with helpful messages
- Weekend/holiday awareness for code freeze calculation
- Business day logic for reasonable freeze timing

### Mode Selection Confusion
- Clear explanations of each mode with examples
- Context about current system state
- Recommendations based on typical usage patterns

### Workflow Execution Issues
- Clear error messages for GitHub API failures
- Fallback guidance for manual workflow execution
- Validation of release status before execution

## Implementation Details

### Required Tools & Scripts
- **Python script**: `.claude/skills/odh-set-next-release/scripts/set_next.py`
- **Date calculation**: Integration with existing date logic
- **Release status management**: YAML parsing and updates
- **GitHub API integration**: Trigger existing set-next-release workflow

### Dependencies
- Access to `configs/release-status.yaml`
- Date validation logic from `.github/scripts/validate_set_release_inputs.sh`
- GitHub API permissions for workflow triggering
- Existing GitHub App authentication infrastructure

### Intelligent Features
- **Auto-calculation**: Code freeze dates with business day awareness
- **Smart defaults**: Based on release history and patterns
- **Context awareness**: Current release status affects recommendations
- **Validation integration**: Reuse existing date and version validation

## Date Intelligence

### Code Freeze Calculation
- Default: 3 days before release date
- Business day awareness (avoid Sunday/Monday freeze)
- Holiday consideration (future enhancement)
- Custom override support

### Release Date Patterns
- Typical Tuesday releases for ODH
- Monthly cadence guidance
- Avoid major holidays and conflicts

### Timeline Validation
- Reasonable lead time for planning
- Conflict detection with existing releases
- Integration with current release timeline

## Future Enhancements
- Integration with calendar systems for conflict checking
- Automatic notification to component teams about new releases
- Release template generation with checklist items
- Integration with project planning tools for milestone tracking