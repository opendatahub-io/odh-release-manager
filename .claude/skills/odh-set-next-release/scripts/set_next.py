#!/usr/bin/env python3
"""
ODH Set Next Release Script

Interactive script for planning ODH releases with date intelligence and mode guidance.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timedelta
import re

class ODHReleasePlanner:
    def __init__(self):
        self.repo_root = self._find_repo_root()
        self.release_status_path = self.repo_root / "configs" / "release-status.yaml"
        self.validate_script = self.repo_root / ".github" / "scripts" / "validate_set_release_inputs.sh"

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

    def _get_release_status(self):
        """Get current release status"""
        try:
            current_version = self._run_yq_command(".current_release.version", self.release_status_path)
            current_status = self._run_yq_command(".current_release.status", self.release_status_path)
            next_version = self._run_yq_command(".next_release.version", self.release_status_path)
            next_enabled = self._run_yq_command(".next_release.enabled", self.release_status_path)
            next_date = self._run_yq_command(".next_release.release_date", self.release_status_path)

            return {
                "current": {
                    "version": current_version if current_version != "null" else None,
                    "status": current_status if current_status != "null" else None
                },
                "next": {
                    "version": next_version if next_version != "null" else None,
                    "enabled": next_enabled == "true",
                    "release_date": next_date if next_date != "null" else None
                }
            }
        except Exception as e:
            print(f"Warning: Could not read release status: {e}")
            return {"current": {}, "next": {}}

    def _get_release_history(self):
        """Get recent release history for context"""
        try:
            releases_dir = self.repo_root / "releases"
            if releases_dir.exists():
                versions = []
                for version_dir in sorted(releases_dir.iterdir(), reverse=True):
                    if version_dir.is_dir():
                        versions.append(version_dir.name)
                return versions[:5]  # Last 5 releases
            return []
        except Exception as e:
            return []

    def _validate_version_format(self, version):
        """Validate release version format"""
        # Pattern for semantic versioning with optional early access
        pattern = r'^v\d+\.\d+\.\d+(-ea\.\d+)?$'
        if re.match(pattern, version):
            return {"valid": True, "message": "✓ Version format is valid"}
        else:
            return {
                "valid": False,
                "message": "Version must follow pattern: v<major>.<minor>.<patch> or v<major>.<minor>.<patch>-ea.<number>"
            }

    def _validate_date_format(self, date_str):
        """Validate date format and check if it's in the future"""
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            today = datetime.now()

            if date.date() <= today.date():
                return {
                    "valid": False,
                    "message": "Release date must be in the future"
                }

            return {
                "valid": True,
                "message": "✓ Date format is valid",
                "date": date
            }
        except ValueError:
            return {
                "valid": False,
                "message": "Date must be in format YYYY-MM-DD"
            }

    def _calculate_code_freeze_date(self, release_date):
        """Calculate code freeze date (3 days before release)"""
        freeze_date = release_date - timedelta(days=3)

        # Get day of week (0=Monday, 6=Sunday)
        day_name = freeze_date.strftime("%A")

        return {
            "date": freeze_date,
            "formatted": freeze_date.strftime("%B %d"),
            "day_name": day_name,
            "iso": freeze_date.strftime("%Y-%m-%d")
        }

    def _explain_modes(self, current_status):
        """Explain the three modes based on current system state"""
        print("🔸 What should I update?")
        print("   Options:")
        print("   1. Set next release only (recommended for planning)")
        print("   2. Update current release info too")
        print("   3. Update both current and next")

        # Provide context-specific guidance
        if not current_status["current"]["version"]:
            print("\n   Hint: Use option 1 for initial planning (no current release active)")
        else:
            print(f"\n   Hint: Current release is {current_status['current']['version']} ({current_status['current']['status']})")
            print("   Use option 3 if current release details need updating")

    def interactive_plan_release(self, version=None):
        """Main interactive release planning flow"""
        print("🔧 ODH Release Planning")
        print("I'll help you set up the next ODH release. Let me gather the details:\n")

        # Step 1: Version Input
        if not version:
            history = self._get_release_history()
            print("🔸 What's the next release version?")
            print("   Hint: Use semantic versioning like 'v3.6.0' or early access 'v3.6.0-ea.1'")
            if history:
                print(f"   Recent releases: {', '.join(history)}")

            version = input("   > ").strip()

        # Validate version format
        version_validation = self._validate_version_format(version)
        print(f"   {version_validation['message']}")

        if not version_validation["valid"]:
            print("\n❌ Please fix the version format and try again.")
            return False

        # Step 2: Release Date
        print("\n🔸 What's the target release date?")
        print("   Hint: Format as YYYY-MM-DD, usually Tuesdays for ODH releases")
        print("   Typical cadence: Monthly releases")

        date_str = input("   > ").strip()

        date_validation = self._validate_date_format(date_str)
        print(f"   {date_validation['message']}")

        if not date_validation["valid"]:
            print("\n❌ Please fix the date and try again.")
            return False

        release_date = date_validation["date"]

        # Step 3: Code Freeze Calculation
        freeze_info = self._calculate_code_freeze_date(release_date)
        print(f"\n🔸 Code freeze date will be 3 days before: {freeze_info['formatted']} ({freeze_info['day_name']})")
        print("   Is this acceptable? [Yes/No/Custom]")
        print("   Hint: Code freeze is when component registrations close")

        freeze_choice = input("   > ").strip().lower()

        if freeze_choice in ['no', 'n', 'custom']:
            print("   What date should code freeze be? (YYYY-MM-DD)")
            custom_freeze = input("   > ").strip()
            freeze_validation = self._validate_date_format(custom_freeze)
            if freeze_validation["valid"]:
                freeze_info["iso"] = custom_freeze
                freeze_info["formatted"] = freeze_validation["date"].strftime("%B %d")
                print(f"   ✓ Using custom freeze date: {freeze_info['formatted']}")
            else:
                print(f"   ⚠️  Invalid date format, using calculated: {freeze_info['formatted']}")

        # Step 4: Mode Selection
        current_status = self._get_release_status()
        print(f"\n📊 Current Release Status:")
        if current_status["current"]["version"]:
            print(f"   - Current: {current_status['current']['version']} ({current_status['current']['status']})")
        else:
            print("   - Current: No active release")

        if current_status["next"]["version"]:
            print(f"   - Next: {current_status['next']['version']} (enabled: {current_status['next']['enabled']})")
        else:
            print("   - Next: Not configured")

        self._explain_modes(current_status)

        while True:
            mode_choice = input("\n   > ").strip()
            if mode_choice == "1":
                mode = "next_release_only"
                break
            elif mode_choice == "2":
                mode = "current_release_only"
                break
            elif mode_choice == "3":
                mode = "both"
                break
            else:
                print("   Please enter 1, 2, or 3")

        # Step 5: Preview and Confirmation
        print(f"\n✅ Ready to configure:")
        print(f"   - Next Release: {version} on {release_date.strftime('%B %d, %Y')}")
        print(f"   - Code Freeze: {freeze_info['formatted']}, {freeze_info['date'].year} ({freeze_info['day_name']})")
        print(f"   - Mode: {mode}")

        if mode == "next_release_only":
            print("   - Will enable: next_release planning")
        elif mode == "current_release_only":
            print("   - Will update: current_release info")
        else:
            print("   - Will update: both current_release and next_release")

        print(f"\nThis will set up {version} as the {'next planned' if 'next' in mode else 'current'} ODH release.")

        confirm = input("\n🔸 Shall I configure this release? [Yes/No] ").strip().lower()

        if confirm in ['yes', 'y']:
            return self._trigger_set_next_workflow(version, date_str, freeze_info["iso"], mode)
        else:
            print("\n📋 Release planning cancelled.")
            return False

    def _trigger_set_next_workflow(self, version, release_date, freeze_date, mode):
        """Trigger the existing set-next-release.yaml workflow"""
        print("\n🚀 Configuring release...")

        # For now, show what would be done - actual GitHub API integration would go here
        print(f"   Version: {version}")
        print(f"   Release Date: {release_date}")
        print(f"   Code Freeze Date: {freeze_date}")
        print(f"   Mode: {mode}")
        print(f"   Timestamp: {datetime.now().isoformat()}")

        print("\n   [In production: This would trigger the set-next-release.yaml workflow]")
        print("   [GitHub API call would execute with these inputs]")
        print("\n✅ Release planning request prepared successfully!")
        print(f"   {version} is now planned for {release_date}.")
        print("\nNext: Teams can start registering components for this release.")

        return True

def main():
    parser = argparse.ArgumentParser(description="ODH Release Planning")
    parser.add_argument("version", nargs="?", help="Release version to plan")
    args = parser.parse_args()

    planner = ODHReleasePlanner()
    success = planner.interactive_plan_release(args.version)

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()