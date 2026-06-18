# Release Validation Guide

This guide is for anyone performing validation of ODH community releases before publication.

## What is Release Validation?

Release validation confirms that a staged ODH release meets quality standards before it's published to the community. Release validation triggers the community release process, which publishes the release to OperatorHub.

## When Release Validation Happens

Release validation happens when:
1. Release manager triggers a release
2. External staging completes successfully 
3. Release status becomes `awaiting_validation`

## Release Validation Process

### Step 1: Check Release Status
Verify a release is ready for validation:
- Go to `configs/release-status.yaml` 
- Look for `status: "awaiting_validation"`

### Step 2: Perform Validation
Test the release using your standard validation procedures. Key areas:
- Fresh installation works
- Components function correctly
- Basic workflows complete
- Upgrades work (if applicable)

### Step 3: Provide Validation Approval

Once validation testing passes:
1. Navigate to **Actions** → **Release Validation and Community Release**
2. Click **Run workflow**
3. Confirm the release version matches what you tested
4. Click **Run workflow** to approve

This will:
- Record your validation approval with timestamp
- Update status to `in_progress_community_release`
- Trigger the community operators workflow
- Begin the community release process

### Step 4: Monitor Community Release

After validation approval:
- Community operators workflow runs in `opendatahub-operator` repo
- Watch for community PR creation 
- PR will be submitted to community operators repositories
- Release manager will complete the process once PR merges

## Validation Standards

### Required Testing
- [ ] Clean installation on supported platforms
- [ ] Core component functionality verified
- [ ] Sample workloads execute successfully
- [ ] Documentation links work
- [ ] No breaking changes in APIs

### Optional Testing (when applicable)
- [ ] Upgrade path from previous version
- [ ] Integration with external systems
- [ ] Performance regression testing
- [ ] Security scans pass

## Validation Status Tracking

The system tracks:
- **Who**: Your GitHub username (`validated_by`)
- **When**: Timestamp of approval (`validated_at`)
- **What**: Release version being validated

## Emergency Procedures

### If Validation Fails
1. **Do not run the validation workflow**
2. Report issues to the release manager
3. Work with component teams to resolve problems
4. Re-test once fixes are available
5. Only approve when all issues are resolved

### If Community Release Fails
- Community release problems don't affect your validation record
- Release manager handles community PR issues
- Your validation approval remains valid
- Release can be re-triggered if needed

## FAQ

**Q: Can multiple people validate the same release?**  
A: Only one person needs to provide validation approval. The system records who approved it.

**Q: Can I validate a release multiple times?**  
A: The workflow can be run multiple times, but only the latest approval is recorded.

**Q: What if I approve by mistake?**  
A: Contact the release manager immediately. They can reset the release status if the community release hasn't started yet.

**Q: How do I know what's in this release?**  
A: Check `releases/{version}/README.md` for the complete component list and versions.

**Q: Who can perform validation?**  
A: Anyone with repository access can perform validation. The system is role-agnostic.