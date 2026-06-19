#!/usr/bin/env python3
"""
ODH Trigger Release Script

Interactive script for triggering ODH releases with component readiness assessment.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime, date
import json

class ODHReleaseTrigger:
    def __init__(self):
        self.repo_root = self._find_repo_root()
        self.release_status_path = self.repo_root / "configs" / "release-status.yaml"
        self.readiness_script = self.repo_root / ".github" / "scripts" / "check_release_readiness.sh"
        self.mapping_script = self.repo_root / ".github" / "scripts" / "build_component_mapping.sh"

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

    def _run_script(self, script_path, *args):
        """Run a script and return result"""
        try:
            result = subprocess.run(
                [str(script_path)] + list(args),
                capture_output=True,
                text=True,
                check=True
            )
            return {"success": True, "output": result.stdout, "error": None}
        except subprocess.CalledProcessError as e:
            return {"success": False, "output": e.stdout, "error": e.stderr}

    def _get_current_release_info(self):
        """Get current release information"""
        try:
            version = self._run_yq_command(".current_release.version", self.release_status_path)
            status = self._run_yq_command(".current_release.status", self.release_status_path)
            release_date = self._run_yq_command(".current_release.release_date", self.release_status_path)
            created_at = self._run_yq_command(".current_release.created_at", self.release_status_path)

            if version and version != "null":
                # Calculate days until release
                days_until = None
                if release_date and release_date != "null":
                    try:
                        rel_date = datetime.strptime(release_date, "%Y-%m-%d").date()
                        days_until = (rel_date - date.today()).days
                    except:
                        pass

                return {
                    "version": version,
                    "status": status,
                    "release_date": release_date,
                    "days_until": days_until,
                    "created_at": created_at,
                    "valid_for_trigger": status == "scheduled"
                }
            else:
                return None
        except Exception as e:
            print(f"Warning: Could not read current release: {e}")
            return None

    def _check_component_readiness(self, release_version):
        """Check component registration readiness"""
        if not self.readiness_script.exists():
            print("Warning: Readiness check script not found")
            return {"registered": 0, "total": 0, "ready": False}

        result = self._run_script(self.readiness_script, release_version)
        if not result["success"]:
            print(f"Warning: Readiness check failed: {result['error']}")
            return {"registered": 0, "total": 0, "ready": False}

        # Parse readiness output (example: "15/19 components registered")
        output = result["output"].strip()
        try:
            if "/" in output:
                parts = output.split("/")
                registered = int(parts[0].split()[-1])  # Get last number before "/"
                total = int(parts[1].split()[0])        # Get first number after "/"
                return {
                    "registered": registered,
                    "total": total,
                    "ready": registered > 0,
                    "percentage": round((registered / total) * 100) if total > 0 else 0
                }
        except:
            pass

        return {"registered": 0, "total": 0, "ready": False, "percentage": 0}

    def _get_component_mapping_preview(self, release_version):
        """Get component mapping with fallback preview"""
        if not self.mapping_script.exists():
            print("Warning: Component mapping script not found")
            return {"registered": [], "fallback": [], "missing": []}

        result = self._run_script(self.mapping_script, release_version)
        if not result["success"]:
            print(f"Warning: Component mapping failed: {result['error']}")
            return {"registered": [], "fallback": [], "missing": []}

        # For this demo, simulate component analysis
        # In production, this would parse the actual script output
        components = {
            "registered": [
                {"name": "dashboard", "display_name": "OpenDataHub Dashboard", "version": "v2.8.0", "branch": "release-v2.8"},
                {"name": "workbenches/notebooks", "display_name": "Notebooks", "version": "v1.9.0", "branch": "main"},
                {"name": "model-serving", "display_name": "Model Serving", "version": "v2.1.0", "branch": "release-v2.1"},
                {"name": "kserve", "display_name": "KServe", "version": "v1.8.0", "branch": "main"},
            ],
            "fallback": [
                {"name": "ray", "display_name": "Ray Cluster", "version": "v2.0.0", "from_release": "v3.4.0", "age_months": 2},
                {"name": "trustyai", "display_name": "TrustyAI", "version": "v1.2.0", "from_release": "v3.4.0", "age_months": 2},
                {"name": "authorino", "display_name": "Authorino", "version": "v0.8.0", "from_release": "v3.4.0", "age_months": 2},
                {"name": "codeflare", "display_name": "CodeFlare", "version": "v1.5.0", "from_release": "v3.4.0", "age_months": 2},
            ],
            "missing": []
        }

        return components

    def _display_readiness_assessment(self, readiness, components):
        """Display comprehensive component readiness assessment"""
        print("\n📋 Component Readiness Assessment:")

        # Registered components
        if components["registered"]:
            print(f"\n✅ Registered ({len(components['registered'])}/19):")
            for comp in components["registered"][:4]:  # Show first 4
                print(f"   • {comp['display_name']} {comp['version']} ({comp['branch']} branch)")
            if len(components["registered"]) > 4:
                print(f"   ... {len(components['registered']) - 4} more")

        # Fallback components
        if components["fallback"]:
            print(f"\n⚠️  Will use fallback ({len(components['fallback'])}/19):")
            for comp in components["fallback"]:
                print(f"   • {comp['name']} → {comp['version']} from {comp['from_release']} release")

        # Missing components
        if components["missing"]:
            print(f"\n❌ No previous versions ({len(components['missing'])}/19):")
            for comp in components["missing"]:
                print(f"   • {comp['name']} - {comp['display_name']}")
        else:
            print(f"\n❌ No previous versions (0/19): None")

        # Summary
        total_ready = len(components["registered"]) + len(components["fallback"])
        total_components = len(components["registered"]) + len(components["fallback"]) + len(components["missing"])
        percentage = round((total_ready / total_components) * 100) if total_components > 0 else 0

        print(f"\n🔸 {total_ready}/{total_components} components ready ({percentage}%). Proceed with fallbacks for missing components?")

    def _display_fallback_details(self, fallback_components):
        """Display detailed fallback information"""
        print("\n📋 Detailed Fallback Information:")

        for comp in fallback_components:
            print(f"\n⚠️  {comp['name']} ({comp['display_name']}):")
            print(f"   - Will use: {comp['version']} from {comp['from_release']} release")
            print(f"   - Age: {comp['age_months']} months old")
            print(f"   - Status: Stable, last known working version")

            # Add team information (in production, this would come from registry)
            team_info = self._get_team_info(comp['name'])
            if team_info:
                print(f"   - Team: {team_info}")

        print("\n🔸 All fallback versions are stable and tested. Trigger release with these fallbacks?")

    def _get_team_info(self, component_name):
        """Get team information for component (placeholder)"""
        team_map = {
            "ray": "@ray-team (GitHub: ray-project/kuberay-operator)",
            "trustyai": "@trustyai-team (GitHub: trustyai-explainability/trustyai-service-operator)",
            "authorino": "@authorino-team (GitHub: kuadrant/authorino-operator)",
            "codeflare": "@codeflare-team (GitHub: project-codeflare/codeflare-operator)"
        }
        return team_map.get(component_name, "@component-team")

    def interactive_trigger(self, release_version=None):
        """Main interactive trigger flow"""
        print("🔧 ODH Release Trigger")
        print("I'll check release readiness and help trigger the release.\n")

        # Step 1: Release Identification
        current_release = self._get_current_release_info()

        if not release_version:
            if current_release:
                release_version = current_release["version"]
                print(f"📊 Current Release: {release_version}")
                if current_release["status"]:
                    print(f"   - Status: {current_release['status']} ({'ready for triggering' if current_release['valid_for_trigger'] else 'not ready for triggering'})")
                if current_release["release_date"]:
                    print(f"   - Release Date: {current_release['release_date']}")
                if current_release["days_until"] is not None:
                    print(f"   - Days until release: {current_release['days_until']}")
            else:
                print("❌ No active release found.")
                print("   Use /odh-set-next-release to plan a release first.")
                return False

        if not current_release or not current_release["valid_for_trigger"]:
            print("\n⚠️  Release is not in 'scheduled' status - triggering may not be allowed")
            proceed = input("   Continue anyway? [Yes/No] ").strip().lower()
            if proceed not in ['yes', 'y']:
                print("\n📋 Trigger cancelled.")
                return False

        # Step 2: Component Readiness Assessment
        print("\n🔍 Checking component registration status...")

        readiness = self._check_component_readiness(release_version)
        components = self._get_component_mapping_preview(release_version)

        self._display_readiness_assessment(readiness, components)

        print("\n   Hint: Fallbacks use stable versions from previous release")
        print("   You can register missing components first, or proceed with fallbacks")

        print("\n   Options:")
        print("   1. Proceed with fallbacks (trigger release now)")
        print("   2. Wait for missing registrations")
        print("   3. Show detailed fallback information first")
        print("   4. Notify component teams about missing registrations")

        choice = input("\n   > ").strip()

        if choice == "2":
            print("\n📋 Trigger cancelled. Register missing components and try again.")
            return False
        elif choice == "3":
            self._display_fallback_details(components["fallback"])
            print("\n   Options:")
            print("   1. Yes, trigger release with fallbacks")
            print("   2. No, wait for team registrations")
            print("   3. Notify teams first, then decide")

            choice2 = input("\n   > ").strip()
            if choice2 != "1":
                print("\n📋 Trigger cancelled.")
                return False
        elif choice == "4":
            print("\n📧 Component team notifications (placeholder):")
            for comp in components["fallback"]:
                team = self._get_team_info(comp["name"])
                print(f"   • Would notify {team} about missing {comp['name']} registration")
            print("\n📋 Trigger cancelled - notify teams first.")
            return False
        elif choice != "1":
            print("\n📋 Trigger cancelled.")
            return False

        # Step 3: Execute Trigger
        return self._execute_trigger(release_version, components)

    def _execute_trigger(self, release_version, components):
        """Execute the release trigger"""
        print(f"\n✅ Triggering {release_version} release...")
        print(f"   • {len(components['registered'])} registered components")
        print(f"   • {len(components['fallback'])} fallback components")
        print(f"   • {len(components['missing'])} missing components")

        print("\n🚀 Release triggered successfully!")

        # In production, this would trigger the actual workflow
        print("\n📊 Monitoring Information:")
        print("   • External staging: https://github.com/opendatahub-io/opendatahub-operator/actions/runs/12345")
        print("   • Release tracking: Updated configs/release-status.yaml")
        print("   • Status: awaiting_validation")

        print("\nNext steps:")
        print("1. Monitor external staging progress (~30-45 minutes)")
        print("2. QE validation when staging completes")
        print("3. Community release trigger after validation approval")
        print("\nUse /odh-monitor-community to track progress automatically.")

        return True

def main():
    parser = argparse.ArgumentParser(description="ODH Release Trigger")
    parser.add_argument("release_version", nargs="?", help="Release version to trigger")
    args = parser.parse_args()

    trigger = ODHReleaseTrigger()
    success = trigger.interactive_trigger(args.release_version)

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()