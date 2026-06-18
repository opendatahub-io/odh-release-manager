# Release Manager Guide

This guide is for Release Managers who orchestrate ODH community releases from start to finish. Release managers are responsible for assessing release readiness, triggering releases, monitoring progress, and ensuring successful completion.


## Release Manager Responsibilities

Release managers orchestrate the complete release lifecycle: assess component readiness, trigger releases when ready, monitor external staging progress, coordinate with validation for validation, handle issues that arise, and finalize successful releases. During emergencies, manage rollbacks, hotfixes, and escalations as needed.

## Release Lifecycle Overview

The complete release process involves these phases:

```
1. Component Registration → 2. Release Trigger → 3. External Staging → 4. validation Signoff → 5. Community Release → 6. Completion
   [Ongoing]                [You trigger]     [Monitor]           [validation triggers]   [Auto-triggered]    [Auto/Manual]
   
   Status: scheduled → awaiting_validation → in_progress_community_release → completed
```

### Your Key Decision Points
- **When to trigger**: Is the release ready based on component registrations?
- **Whether to use fallback**: Should we include additional components from previous releases?
- **How to handle issues**: What to do when external staging fails?
- **When to complete**: Is the release fully done and ready for archival?

## Prerequisites and Access

Requires admin access to `opendatahub-io/odh-release-manager`, GitHub CLI (`gh`) and YAML tools (`yq`), plus understanding of component registration process and ODH architecture.

## Release Readiness Assessment

Before triggering, assess component registration status (at least 80% of core components registered), validate registrations using `./.github/scripts/check_release_readiness.sh "$CURRENT_VERSION"`, and consider timing factors like code freeze deadlines and validation availability.

## Triggering a Release

Once readiness is confirmed:

1. **Final validation**: Check release status is `"scheduled"` and component count meets threshold
2. **Trigger release**: Go to **Actions** → **Trigger Release** → **Run workflow** with release version
3. **Verify success**: Confirm status updates to `"awaiting_validation"`

The trigger workflow builds enhanced component mapping with display names and passes it to external staging.

## Monitoring Release Progress

After triggering, monitor four phases:

**External Staging (30-60 minutes)**: Check external workflow URL in `configs/release-status.yaml`. Manifests collected, bundles built, images tagged.

**validation Signoff (Variable)**: Monitor for status remaining `"awaiting_validation"` and watch for validation signoff workflow execution. validation signoff automatically triggers community release.

**Community Release (2-4 hours)**: Status becomes `"in_progress_community_release"` when validation provides signoff. Monitor community release status and PR creation/merge in release status file.

**Completion (Automatic/Manual)**: Release completes automatically if community PR merges successfully. Manual completion may be needed if issues arise.

## Managing Release Issues

**External Staging Failures**: Check external workflow logs, identify if component-specific (contact team) or infrastructure (retry trigger).

**validation Signoff Delays**: Ensure validation knows release is pending, provide context on changes, escalate if needed.

**Community Release Problems**: Monitor `release-community.yaml` workflow, watch community PR review delays, contact Red Hat maintainers for OperatorHub issues.

## Completing Releases

Most releases complete automatically when community PR merges successfully - the validation signoff workflow triggers completion automatically. For releases where community merge fails or manual intervention is needed, use the **Complete Release** workflow manually. Verify completion by checking release history and OperatorHub publication.

## Post-Release Activities

If next release was configured, it automatically becomes current. Notify stakeholders of completion, ensure release notes are accurate, and begin planning next cycle.

## Emergency Procedures

**Release Rollback**: Assess if rollback needed vs hotfix, coordinate with teams, follow rollback process in specs/001-rollback-system.md.

**Hotfix Management**: Create patch version releases, fast-track component registrations, streamline validation validation.

**Crisis Communication**: Provide regular status updates, keep leadership informed, document resolution process.

## Troubleshooting Common Issues

**Idempotency Errors**: Check release status - if `"failed"` retry, if `"awaiting_validation"` release is proceeding normally.

**Permission Errors**: Verify GitHub access and PAT tokens via `gh api` and `gh secret list`.

**Late Component Registrations**: Assess criticality, consider delaying trigger or using fallback mechanism.

**Invalid Registrations**: Run `./.github/scripts/check_release_readiness.sh` and work with teams to fix issues.

**Infrastructure Outages**: Monitor status.github.com, registry status pages, and Konflux console. Delay trigger until stable.

**Konflux Build Failures**: Check Konflux console logs. Contact [#konflux-users](https://redhat.enterprise.slack.com/archives/C04PZ7H0VA8) or [#rhoai-devtestops-requests](https://redhat.enterprise.slack.com/archives/C07TF3MBMMW).

