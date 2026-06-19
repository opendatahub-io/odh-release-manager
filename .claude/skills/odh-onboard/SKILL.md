---
name: odh-onboard
description: Interactively onboard new ODH components with guided questions and validation
user_invocable: true
---

# ODH Component Onboarding Skill

## Purpose
Guide teams through the ODH component onboarding process using conversational prompts with helpful hints and real-time validation. This skill asks intelligent questions to gather the required information, validates inputs using existing scripts, and triggers the established onboard-component.yaml workflow.

## Usage
- `/odh-onboard` - Start interactive onboarding process
- `/odh-onboard <component-name>` - Start with pre-filled component name

## Conversational Flow

### 1. Component Name Collection & Validation
- If not provided, ask for component name with kebab-case guidance
- Validate format using existing `.github/scripts/validate-component-name.sh`
- Check for conflicts against existing registry
- Provide helpful examples and format corrections

### 2. Display Name Guidance
- Ask for human-readable display name with examples from existing components
- Explain where this appears in ODH UIs
- Validate length and format appropriateness

### 3. Component Type Selection
- Explain difference between "component" and "image" types with clear examples
- Provide guidance on which type to choose based on component characteristics
- Default to "component" with explanation for most cases

### 4. Preview & Confirmation
- Show complete onboarding summary before execution
- Explain what will happen next (PR creation, approval process)
- Offer options to proceed or modify inputs

## Integration Points

### Existing ODH Infrastructure
- **Validation**: Uses `.github/scripts/validate-component-name.sh` for name validation
- **Registry**: Reads `configs/components-registry.yaml` for conflict checking and examples
- **Workflow**: Triggers existing `onboard-component.yaml` GitHub Actions workflow
- **Authentication**: Reuses existing GitHub App token infrastructure

### Preserves Existing Process
- All validation rules remain unchanged
- Same approval process and YAML structure
- Identical audit trail through Git commits
- No modifications to existing GitHub workflows

## Example Interaction

```
User: /odh-onboard

Claude: I'll help you onboard a new component to ODH. Let me ask a few questions:

What's the component name?
   Hint: Use kebab-case format like "model-serving" or "notebook-controller"
   This becomes the technical identifier in all ODH systems.

User: my-new-component

Component name: "my-new-component" 
   ✓ Good - kebab-case format is correct

What's the human-readable display name?
   Hint: This appears in UIs and documentation, e.g., "Model Serving", "Notebook Controller"
   Examples from existing components: "Dashboard", "Workbenches", "KServe"

User: My New Component

Is this a "component" or "image"?
   Hint: 
   - "component" = has source code repositories, builds from source
   - "image" = container image only, no source code in ODH
   Most ODH components are "component" type (17 out of 19 existing components)

User: component

Ready to onboard:
   - Name: my-new-component
   - Display Name: My New Component  
   - Type: component

This will create a PR to add your component to the registry. After approval by the ODH team, 
you'll be able to register versions for releases.

Shall I create the onboarding PR? [Yes/No]

User: Yes

Creating onboarding PR... 
   PR created: https://github.com/opendatahub-io/odh-release-manager/pull/123
   
The ODH team will review and approve your component. You'll be notified when it's ready!
```

## Error Handling & Guidance

### Invalid Component Names
- Real-time validation feedback with specific error explanations
- Suggestions for valid alternatives
- Examples of correctly formatted names from existing registry

### Existing Component Names
- Check against current registry to prevent conflicts
- Show similar existing names if conflicts found
- Guide users to modify their component name appropriately

### Workflow Execution Issues
- Clear error messages if GitHub API calls fail
- Guidance on manual workflow execution as fallback
- Links to relevant documentation and support channels

## Implementation Details

### Required Tools & Scripts
- **Python script**: `.claude/skills/odh-onboard/scripts/onboard.py`
- **Validation integration**: Wrapper for existing validation scripts
- **GitHub API integration**: Trigger existing workflows with gathered inputs
- **YAML parsing**: Read existing registry for context and conflict checking

### Dependencies
- Access to `.github/scripts/validate-component-name.sh`
- Read access to `configs/components-registry.yaml`
- GitHub API permissions for workflow triggering
- Existing GitHub App authentication infrastructure

## Testing Strategy
- Validate integration with existing validation scripts
- Test GitHub workflow triggering without breaking existing functionality  
- Verify conflict detection against current registry
- Ensure proper error handling for edge cases

## Future Enhancements
- Automatic notification when onboarding PR is approved
- Integration with component registration workflow for seamless handoff
- Enhanced validation with additional checks for component readiness
- Batch onboarding support for multiple components