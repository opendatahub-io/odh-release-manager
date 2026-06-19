---
name: odh-monitor-community
description: Monitor ODH community release progress with automated PR tracking and completion assistance
user_invocable: true
---

# ODH Monitor Community Release Skill

## Purpose
Monitor and assist with ODH community release progression through automated PR tracking, status monitoring, and intelligent completion guidance. This skill provides real-time visibility into the community release process and automates the transition from community PR merge to release completion.

## Usage
- `/odh-monitor-community` - Monitor current community release progress
- `/odh-monitor-community <version>` - Monitor specific release version
- `/odh-monitor-community <pr-url>` - Monitor specific community PR

## Conversational Flow

### 1. Release Status Assessment
- Identify current release in community release phase
- Parse release status from `configs/release-status.yaml`
- Show external staging completion and validation status
- Display community release progression timeline

### 2. Community PR Discovery & Tracking
- Auto-detect community PR URL from release status
- If missing, ask user for community PR URL with guidance
- Validate PR URL format and accessibility
- Parse PR status, checks, and approval requirements

### 3. Real-time Monitoring Setup
- Offer automated monitoring with configurable check intervals
- Set up periodic PR status checks via GitHub API
- Track merge status, check results, and approval progress
- Provide estimated merge timeline based on PR activity

### 4. Merge Detection & Completion
- Automatically detect when community PR merges
- Notify user of merge completion with celebration
- Offer immediate release completion workflow triggering
- Guide through final release steps and verification

### 5. Progress Notifications & Updates
- Provide periodic status updates during monitoring
- Alert on significant changes (approvals, check failures, etc.)
- Show progress indicators and estimated completion times
- Maintain engagement without being overwhelming

## Integration Points

### Existing ODH Infrastructure
- **Release Status**: Reads and updates `configs/release-status.yaml`
- **Community PR Tracking**: Uses existing `community_pr_url` field
- **External Monitoring**: Tracks external staging workflow completion
- **Completion Workflow**: Triggers existing `complete-release.yaml` workflow
- **GitHub API**: Direct integration for PR status and merge detection

### Preserves Existing Process
- Same release status tracking structure
- Identical completion workflow and audit trail
- No changes to community PR creation process
- Maintains existing external workflow integration

## Example Interaction

```
User: /odh-monitor-community

Claude: I'll help monitor the community release process.

Current Status for v3.5.0:
   - Release Status: in_progress_community_release
   - External Staging: ✅ Completed (45 minutes ago)
   - Validation: ✅ Approved by QE team
   - Community Release: 🔄 In Progress

I can monitor the community PR automatically. What's the PR URL?
   Hint: This should be in the community-operators-prod repository
   Example: https://github.com/redhat-openshift-ecosystem/community-operators-prod/pull/2847

User: https://github.com/redhat-openshift-ecosystem/community-operators-prod/pull/2847

Community PR Status:
   • PR #2847: ODH v3.5.0 Community Release
   • Status: Open (created 2 hours ago)
   • Checks: ✅ 3/4 passing, 🔄 1 pending (community-ci-pipeline)
   • Reviews: 👍 1/2 approvals required
   • Labels: ready-for-review, community-release
   • Estimated merge: 4-6 hours (based on check completion + review time)

Should I monitor this PR and notify when it's merged? [Yes/No]
   I'll check every 30 minutes and alert you of any significant changes.

User: Yes

Now monitoring PR #2847 for v3.5.0 community release!

   Active monitoring:
   - Check interval: Every 30 minutes  
   - Notifications: Status changes, merge detection
   - Auto-complete: Will offer completion trigger when merged

   You can continue with other work - I'll notify you when there's news!

[30 minutes later...]
Community PR Update for v3.5.0:
   • Checks: ✅ 4/4 all passing! 
   • Reviews: 👍 2/2 approvals complete
   • Status: Ready to merge (waiting for maintainer)

[2 hours later...]
Great news! Community PR #2847 has been merged! 

Release v3.5.0 Status:
   ✅ External Staging: Complete
   ✅ QE Validation: Approved  
   ✅ Community PR: Merged
   
   The ODH v3.5.0 release is now live in the community operators catalog!

Ready to complete the release process?
   This will:
   - Update release status to 'completed'
   - Archive release to history
   - Clean up temporary resources
   - Generate completion report

   Shall I trigger the completion workflow? [Yes/No]

User: Yes

Completing release v3.5.0...
   ✓ Triggered complete-release workflow
   ✓ Updated release-status.yaml  
   ✓ Community release marked as completed

ODH v3.5.0 release completed successfully!
   
Release Summary:
   - Duration: 3 days from trigger to completion
   - Components: 15 registered, 4 fallback
   - Community PR: #2847 (merged in 6 hours)
   - Status: Available in OperatorHub

Release managers can now start planning v3.6.0. Use /odh-set-next-release when ready!
```

## Error Handling & Guidance

### No Community Release in Progress
- Show current release status and phase
- Explain community release timing and prerequisites
- Guide to appropriate workflow based on current phase

### Invalid or Inaccessible PR URLs
- Validate URL format with helpful corrections
- Check PR accessibility and provide troubleshooting
- Guide manual PR discovery if auto-detection fails

### PR Status Issues
- Handle rate limiting with intelligent backoff
- Graceful degradation when GitHub API unavailable
- Clear messaging about monitoring limitations

### Monitoring Interruptions
- Resume monitoring state across skill invocations
- Handle skill restart scenarios gracefully
- Provide manual status checking options

## Implementation Details

### Required Tools & Scripts
- **Python script**: `.claude/skills/odh-monitor-community/scripts/monitor.py`
- **GitHub API integration**: PR status checking and merge detection
- **Release status management**: YAML parsing and updates
- **Notification system**: Progress updates and completion alerts

### Dependencies
- Read/write access to `configs/release-status.yaml`
- GitHub API permissions for PR status checking
- Existing GitHub App authentication infrastructure
- Background monitoring capabilities (or periodic skill invocation)

### Intelligent Features
- **Automated PR discovery**: Parse community_pr_url from release status
- **Smart monitoring intervals**: Adjust frequency based on PR activity
- **Merge prediction**: Estimate completion time based on checks/reviews
- **Proactive completion**: Auto-suggest release completion when ready

## Monitoring Intelligence

### PR Status Analysis
- Parse GitHub PR API responses for comprehensive status
- Track check runs, reviews, labels, and merge conflicts
- Identify blocking issues and provide resolution guidance

### Timeline Prediction
- Analyze historical PR merge patterns
- Consider check run duration and review velocity
- Provide realistic completion estimates

### Notification Management  
- Balance informativeness with non-intrusiveness
- Escalate critical issues requiring immediate attention
- Summarize progress at appropriate intervals

## Background Monitoring Options

### Skill Invocation Pattern
- Use `/odh-monitor-community` to start monitoring
- Skill sets up periodic checks (every 30 minutes)
- Re-invoke automatically until PR merges or user stops

### Cron Integration (Future)
- Schedule automatic monitoring checks
- Persist monitoring state across sessions
- Integration with notification systems (Slack, email)

## Future Enhancements
- Slack/email notification integration for team updates
- Advanced PR analysis (conflict detection, review suggestions)
- Integration with OperatorHub verification for post-merge validation
- Automatic rollback detection and alerting for failed releases