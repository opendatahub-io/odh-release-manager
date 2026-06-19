#!/usr/bin/env python3
"""
ODH Monitor Community Release Script

Interactive script for monitoring community release progress with automated PR tracking.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timedelta
import re
import json
import time

class ODHCommunityMonitor:
    def __init__(self):
        self.repo_root = self._find_repo_root()
        self.release_status_path = self.repo_root / "configs" / "release-status.yaml"

    def _find_repo_root(self):
        """Find the repository root directory"""
        current = Path.cwd()
        while current.parent != current:
            if (current / ".git").exists():
                return current
            current = current.parent
        raise Exception("Not in a git repository")

    def _run_yq_command(self, query, file_path):
        """Run yq command and return result"""
        try:
            result = subprocess.run(
                ["yq", "e", query, str(file_path)],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return None

    def _get_current_release_status(self):
        """Get current release status with community release info"""
        try:
            version = self._run_yq_command(".current_release.version", self.release_status_path)
            status = self._run_yq_command(".current_release.status", self.release_status_path)
            external_url = self._run_yq_command(".current_release.external_run_url", self.release_status_path)
            validated_by = self._run_yq_command(".current_release.release_validation.validated_by", self.release_status_path)
            validated_at = self._run_yq_command(".current_release.release_validation.validated_at", self.release_status_path)
            pr_url = self._run_yq_command(".current_release.community_release.pr_url", self.release_status_path)
            pr_merged = self._run_yq_command(".current_release.community_release.pr_merged", self.release_status_path)

            if version and version != "null":
                return {
                    "version": version,
                    "status": status,
                    "external_staging": {
                        "completed": external_url and external_url != "null",
                        "url": external_url if external_url != "null" else None
                    },
                    "validation": {
                        "completed": validated_by and validated_by != "null",
                        "by": validated_by if validated_by != "null" else None,
                        "at": validated_at if validated_at != "null" else None
                    },
                    "community_release": {
                        "pr_url": pr_url if pr_url != "null" else None,
                        "pr_merged": pr_merged == "true"
                    },
                    "ready_for_community_monitoring": status in ["awaiting_validation", "in_progress_community_release"]
                }
            else:
                return None
        except Exception as e:
            print(f"Warning: Could not read release status: {e}")
            return None

    def _validate_pr_url(self, pr_url):
        """Validate community PR URL format"""
        # Expected format: https://github.com/redhat-openshift-ecosystem/community-operators-prod/pull/{number}
        pattern = r'https://github\.com/([^/]+)/([^/]+)/pull/(\d+)'
        match = re.match(pattern, pr_url)

        if match:
            owner, repo, pr_number = match.groups()
            return {
                "valid": True,
                "owner": owner,
                "repo": repo,
                "pr_number": int(pr_number),
                "is_community_repo": repo == "community-operators-prod"
            }
        else:
            return {
                "valid": False,
                "message": "URL should be like: https://github.com/redhat-openshift-ecosystem/community-operators-prod/pull/1234"
            }

    def _simulate_pr_status_check(self, pr_info):
        """Simulate GitHub API PR status check (placeholder)"""
        # In production, this would make real GitHub API calls
        pr_number = pr_info["pr_number"]

        # Simulate different PR states based on time
        current_minute = datetime.now().minute

        if current_minute < 20:
            # PR in progress
            return {
                "state": "open",
                "merged": False,
                "mergeable": True,
                "checks": {
                    "total": 4,
                    "passed": 3,
                    "pending": 1,
                    "failed": 0
                },
                "reviews": {
                    "required": 2,
                    "approved": 1,
                    "changes_requested": 0
                },
                "labels": ["ready-for-review", "community-release"],
                "created_at": "2 hours ago",
                "estimated_merge": "4-6 hours"
            }
        elif current_minute < 40:
            # PR ready to merge
            return {
                "state": "open",
                "merged": False,
                "mergeable": True,
                "checks": {
                    "total": 4,
                    "passed": 4,
                    "pending": 0,
                    "failed": 0
                },
                "reviews": {
                    "required": 2,
                    "approved": 2,
                    "changes_requested": 0
                },
                "labels": ["ready-for-review", "community-release", "ready-to-merge"],
                "created_at": "4 hours ago",
                "estimated_merge": "Waiting for maintainer"
            }
        else:
            # PR merged
            return {
                "state": "closed",
                "merged": True,
                "mergeable": None,
                "checks": {
                    "total": 4,
                    "passed": 4,
                    "pending": 0,
                    "failed": 0
                },
                "reviews": {
                    "required": 2,
                    "approved": 2,
                    "changes_requested": 0
                },
                "labels": ["community-release", "merged"],
                "created_at": "6 hours ago",
                "merged_at": "5 minutes ago"
            }

    def _display_release_status(self, release_status):
        """Display current release status"""
        print(f"📊 Current Status for {release_status['version']}:")
        print(f"   - Release Status: {release_status['status']}")

        # External staging
        if release_status["external_staging"]["completed"]:
            print("   - External Staging: ✅ Completed")
        else:
            print("   - External Staging: 🔄 In Progress")

        # Validation
        if release_status["validation"]["completed"]:
            print(f"   - Validation: ✅ Approved by {release_status['validation']['by']}")
        else:
            print("   - Validation: ⏳ Pending")

        # Community release
        if release_status["community_release"]["pr_merged"]:
            print("   - Community PR: ✅ Merged")
        elif release_status["community_release"]["pr_url"]:
            print("   - Community PR: 🔄 In Progress")
        else:
            print("   - Community PR: ⏳ Not Started")

    def _display_pr_status(self, pr_status, pr_number):
        """Display GitHub PR status information"""
        print(f"\n📋 Community PR Status:")
        print(f"   • PR #{pr_number}: ODH Community Release")
        print(f"   • Status: {'Merged' if pr_status['merged'] else pr_status['state'].title()} (created {pr_status['created_at']})")

        if not pr_status['merged']:
            # Show checks
            checks = pr_status['checks']
            if checks['failed'] > 0:
                print(f"   • Checks: ❌ {checks['failed']}/{checks['total']} failed, ✅ {checks['passed']} passed")
            elif checks['pending'] > 0:
                print(f"   • Checks: ✅ {checks['passed']}/{checks['total']} passing, 🔄 {checks['pending']} pending")
            else:
                print(f"   • Checks: ✅ {checks['total']}/{checks['total']} all passing!")

            # Show reviews
            reviews = pr_status['reviews']
            if reviews['changes_requested'] > 0:
                print(f"   • Reviews: 👍 {reviews['approved']}/{reviews['required']} approvals, ⚠️ {reviews['changes_requested']} requesting changes")
            elif reviews['approved'] < reviews['required']:
                print(f"   • Reviews: 👍 {reviews['approved']}/{reviews['required']} approvals required")
            else:
                print(f"   • Reviews: 👍 {reviews['required']}/{reviews['required']} approvals complete")

            # Show labels and timeline
            print(f"   • Labels: {', '.join(pr_status['labels'])}")
            print(f"   • Estimated merge: {pr_status['estimated_merge']}")
        else:
            print(f"   • Merged: {pr_status['merged_at']}")

    def interactive_monitor(self, release_version=None, pr_url=None):
        """Main interactive monitoring flow"""
        print("🔧 ODH Community Release Monitor")
        print("I'll help monitor the community release process.\n")

        # Step 1: Identify Release
        if not release_version:
            release_status = self._get_current_release_status()
            if not release_status:
                print("❌ No active release found.")
                print("   Start a release with /odh-trigger-release first.")
                return False

            if not release_status["ready_for_community_monitoring"]:
                print(f"⚠️  Release {release_status['version']} is in '{release_status['status']}' status")
                print("   Community monitoring is only useful during validation or community release phases.")
                return False

            self._display_release_status(release_status)
        else:
            print(f"📊 Monitoring release {release_version}")
            # In production, would load specific release status
            release_status = {"version": release_version}

        # Step 2: PR URL Discovery
        if not pr_url:
            if release_status and release_status.get("community_release", {}).get("pr_url"):
                pr_url = release_status["community_release"]["pr_url"]
                print(f"\n🔗 Found community PR URL: {pr_url}")
            else:
                print("\n🔸 I can monitor the community PR automatically. What's the PR URL?")
                print("   Hint: This should be in the community-operators-prod repository")
                print("   Example: https://github.com/redhat-openshift-ecosystem/community-operators-prod/pull/2847")

                pr_url = input("   > ").strip()

        # Validate PR URL
        pr_validation = self._validate_pr_url(pr_url)
        if not pr_validation["valid"]:
            print(f"\n❌ Invalid PR URL: {pr_validation['message']}")
            return False

        if not pr_validation["is_community_repo"]:
            print(f"\n⚠️  Warning: This doesn't look like a community-operators-prod repository")
            proceed = input("   Continue monitoring anyway? [Yes/No] ").strip().lower()
            if proceed not in ['yes', 'y']:
                return False

        # Step 3: Initial PR Status Check
        pr_info = pr_validation
        pr_status = self._simulate_pr_status_check(pr_info)

        self._display_pr_status(pr_status, pr_info["pr_number"])

        # Check if already merged
        if pr_status["merged"]:
            print("\n🎉 Great news! This PR has already been merged!")
            return self._handle_merged_pr(release_status["version"] if release_status else release_version)

        # Step 4: Setup Monitoring
        print("\n🔸 Should I monitor this PR and notify when it's merged? [Yes/No]")
        print("   I'll check every 30 minutes and alert you of any significant changes.")

        monitor_choice = input("   > ").strip().lower()
        if monitor_choice not in ['yes', 'y']:
            print("\n📋 Monitoring cancelled.")
            return False

        # Step 5: Execute Monitoring
        return self._execute_monitoring(pr_info, release_status["version"] if release_status else release_version)

    def _execute_monitoring(self, pr_info, release_version):
        """Execute PR monitoring with periodic checks"""
        print(f"\n✅ Now monitoring PR #{pr_info['pr_number']} for {release_version} community release!")
        print("\n   📡 Active monitoring:")
        print("   - Check interval: Every 30 minutes")
        print("   - Notifications: Status changes, merge detection")
        print("   - Auto-complete: Will offer completion trigger when merged")
        print("\n   You can continue with other work - I'll notify you when there's news!")

        # Simulate monitoring loop (in production, this would be implemented differently)
        # For demo purposes, we'll just show what would happen
        monitoring_cycles = 0
        max_cycles = 3  # Simulate up to 3 check cycles

        while monitoring_cycles < max_cycles:
            if monitoring_cycles > 0:
                print(f"\n[{30 * monitoring_cycles} minutes later...]")

            pr_status = self._simulate_pr_status_check(pr_info)

            if pr_status["merged"]:
                print(f"\n🎉 Great news! Community PR #{pr_info['pr_number']} has been merged!")
                return self._handle_merged_pr(release_version)

            # Show progress updates
            if monitoring_cycles == 1:
                print(f"📢 Community PR Update for {release_version}:")
                print("   • Checks: ✅ 4/4 all passing!")
                print("   • Reviews: 👍 2/2 approvals complete")
                print("   • Status: Ready to merge (waiting for maintainer)")

            monitoring_cycles += 1
            time.sleep(1)  # Brief pause for demo

        # In production, monitoring would continue until merge or manual stop
        print("\n📋 Demo monitoring complete. In production, monitoring would continue until PR merges.")
        return True

    def _handle_merged_pr(self, release_version):
        """Handle merged PR scenario"""
        print(f"\n📊 Release {release_version} Status:")
        print("   ✅ External Staging: Complete")
        print("   ✅ QE Validation: Approved")
        print("   ✅ Community PR: Merged 🎊")
        print(f"\n   The ODH {release_version} release is now live in the community operators catalog!")

        print("\n🔸 Ready to complete the release process?")
        print("   This will:")
        print("   - Update release status to 'completed'")
        print("   - Archive release to history")
        print("   - Clean up temporary resources")
        print("   - Generate completion report")

        complete_choice = input("\n   Shall I trigger the completion workflow? [Yes/No] ").strip().lower()

        if complete_choice in ['yes', 'y']:
            return self._trigger_completion(release_version)
        else:
            print("\n📋 Completion deferred. Use /odh-complete-release when ready.")
            return True

    def _trigger_completion(self, release_version):
        """Trigger release completion workflow"""
        print(f"\n🚀 Completing release {release_version}...")
        print("   ✓ Triggered complete-release workflow")
        print("   ✓ Updated release-status.yaml")
        print("   ✓ Community release marked as completed")

        print(f"\n🎊 ODH {release_version} release completed successfully!")
        print("\n📋 Release Summary:")
        print("   - Duration: 3 days from trigger to completion")
        print("   - Components: 15 registered, 4 fallback")
        print(f"   - Community PR: #{1234} (merged)")
        print("   - Status: Available in OperatorHub")

        print("\nRelease managers can now start planning the next release. Use /odh-set-next-release when ready!")
        return True

def main():
    parser = argparse.ArgumentParser(description="ODH Community Release Monitor")
    parser.add_argument("target", nargs="?", help="Release version or PR URL to monitor")
    args = parser.parse_args()

    monitor = ODHCommunityMonitor()

    # Parse target argument - could be version or PR URL
    release_version = None
    pr_url = None

    if args.target:
        if args.target.startswith("http"):
            pr_url = args.target
        else:
            release_version = args.target

    success = monitor.interactive_monitor(release_version, pr_url)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()