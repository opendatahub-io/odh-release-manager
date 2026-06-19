#!/usr/bin/env python3
"""
ODH Component Registration Script

Interactive script for registering ODH components for releases with intelligent guidance.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import re

class ODHComponentRegistrar:
    def __init__(self):
        self.repo_root = self._find_repo_root()
        self.registry_path = self.repo_root / "configs" / "components-registry.yaml"
        self.release_status_path = self.repo_root / "configs" / "release-status.yaml"
        self.validate_component_script = self.repo_root / ".github" / "scripts" / "validate-component-name.sh"

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

    def _load_components_registry(self):
        """Load components from registry"""
        try:
            result = subprocess.run(
                ["yq", "e", ".components[]", str(self.registry_path)],
                capture_output=True,
                text=True,
                check=True
            )

            components = []
            current_component = {}

            for line in result.stdout.strip().split('\n'):
                if line.startswith('name: '):
                    if current_component:
                        components.append(current_component)
                    current_component = {'name': line.split('name: ')[1]}
                elif line.startswith('display_name: '):
                    current_component['display_name'] = line.split('display_name: ')[1]
                elif line.startswith('type: '):
                    current_component['type'] = line.split('type: ')[1]

            if current_component:
                components.append(current_component)

            return components
        except Exception as e:
            print(f"Warning: Could not load components registry: {e}")
            return []

    def _get_current_release_info(self):
        """Get current active release information"""
        try:
            # Get current release info
            version = self._run_yq_command(".current_release.version", self.release_status_path)
            status = self._run_yq_command(".current_release.status", self.release_status_path)
            release_date = self._run_yq_command(".current_release.release_date", self.release_status_path)

            if version and version != "null":
                return {
                    "version": version,
                    "status": status,
                    "release_date": release_date,
                    "valid": status in ["scheduled", "awaiting_validation"]
                }
            else:
                return None
        except Exception as e:
            print(f"Warning: Could not read release status: {e}")
            return None

    def _get_component_registration_history(self, component_name, max_versions=3):
        """Get previous registrations for this component"""
        try:
            # Look in releases directory for previous registrations
            releases_dir = self.repo_root / "releases"
            registrations = []

            if releases_dir.exists():
                for version_dir in sorted(releases_dir.iterdir(), reverse=True):
                    if version_dir.is_dir():
                        components_file = version_dir / "components.yaml"
                        if components_file.exists():
                            # Check if component is registered in this release
                            component_info = self._run_yq_command(
                                f'.components[] | select(.name == "{component_name}")',
                                components_file
                            )
                            if component_info:
                                # Parse component info
                                lines = component_info.split('\n')
                                reg = {"release": version_dir.name}
                                for line in lines:
                                    if line.startswith('version: '):
                                        reg['version'] = line.split('version: ')[1]
                                    elif line.startswith('branch: '):
                                        reg['branch'] = line.split('branch: ')[1]
                                    elif line.startswith('registered_at: '):
                                        reg['registered_at'] = line.split('registered_at: ')[1]
                                registrations.append(reg)

                            if len(registrations) >= max_versions:
                                break

            return registrations
        except Exception as e:
            print(f"Warning: Could not load registration history: {e}")
            return []

    def _validate_component_name(self, component_name):
        """Validate component exists in registry"""
        components = self._load_components_registry()
        component_names = [comp['name'] for comp in components]

        if component_name in component_names:
            # Find component details
            component = next(comp for comp in components if comp['name'] == component_name)
            return {"valid": True, "component": component}
        else:
            return {
                "valid": False,
                "message": f"Component '{component_name}' not found in registry",
                "available": component_names[:10]  # Show first 10 for reference
            }

    def _validate_version_format(self, version):
        """Basic version format validation"""
        # Check semantic versioning pattern
        semver_pattern = r'^v?\d+\.\d+\.\d+(-[a-zA-Z0-9\-\.]+)?$'
        if re.match(semver_pattern, version):
            return {"valid": True, "message": f"✓ Version format looks good"}
        else:
            return {
                "valid": False,
                "message": f"Version should follow semantic versioning like 'v2.8.0' or '1.0.0'"
            }

    def interactive_register(self, component_name=None):
        """Main interactive registration flow"""
        print("🔧 ODH Component Registration")
        print("I'll help you register a component for an ODH release.\n")

        # Step 1: Component Selection/Validation
        if not component_name:
            print("🔸 What component would you like to register?")
            components = self._load_components_registry()
            if components:
                print(f"   Available components ({len(components)}): {', '.join([c['name'] for c in components[:5]])}{'...' if len(components) > 5 else ''}")
            component_name = input("   > ").strip()

        validation = self._validate_component_name(component_name)
        if not validation["valid"]:
            print(f"\n❌ {validation['message']}")
            if 'available' in validation:
                print(f"   Available components: {', '.join(validation['available'])}")
            print("\n💡 Use /odh-onboard to add a new component to the registry first.")
            return False

        component = validation["component"]
        print(f"\n✅ Component: {component['name']} ({component['display_name']})")

        # Step 2: Release Version Detection
        current_release = self._get_current_release_info()
        if not current_release:
            print("\n❌ No active release found. Cannot register components at this time.")
            return False

        print(f"\n📊 Current Release Status:")
        print(f"   - Active Release: {current_release['version']}")
        print(f"   - Status: {current_release['status']}")
        if current_release.get('release_date'):
            print(f"   - Release Date: {current_release['release_date']}")

        if not current_release["valid"]:
            print(f"\n⚠️  Release is in '{current_release['status']}' status - registration may not be allowed")
            print("   Check with release managers about timing")

        confirm_release = input(f"\n🔸 Register {component_name} for {current_release['version']}? [Yes/No] ").strip().lower()
        if confirm_release not in ['yes', 'y']:
            print("\n📋 Registration cancelled.")
            return False

        # Step 3: Component Version Input
        history = self._get_component_registration_history(component_name)
        print(f"\n🔸 What version/tag are you registering?")
        print("   Hint: Usually semantic version like 'v2.8.0'")
        if history:
            prev_versions = [f"{h['version']} ({h['release']})" for h in history[:3]]
            print(f"   Previous registrations: {', '.join(prev_versions)}")

        version = input("   > ").strip()

        version_validation = self._validate_version_format(version)
        print(f"   {version_validation['message']}")

        if not version_validation["valid"]:
            print("\n⚠️  Proceeding with version format warning...")

        # Step 4: Branch Selection
        print(f"\n🔸 What branch should we track?")
        print("   Hint: Usually 'main' for latest development, or 'release-v2.8' for stable releases")
        print("   This tells the release system which branch to monitor for changes")
        if history:
            prev_branches = list(set([h.get('branch', 'unknown') for h in history[:3]]))
            print(f"   Previous: {', '.join(prev_branches)}")

        branch = input("   > ").strip()

        if not branch:
            print("   ❌ Branch name is required")
            return False

        # Step 5: Preview and Confirmation
        print(f"\n✅ Ready to register:")
        print(f"   - Component: {component['name']} ({component['display_name']})")
        print(f"   - Version: {version}")
        print(f"   - Branch: {branch}")
        print(f"   - Release: {current_release['version']}")
        print(f"   - Will update: releases/{current_release['version']}/components.yaml")

        print(f"\nThis will make {component['name']} {version} available for the {current_release['version']} ODH release.")

        confirm = input("\n🔸 Shall I register this component? [Yes/No] ").strip().lower()

        if confirm in ['yes', 'y']:
            return self._trigger_register_workflow(component_name, version, branch, current_release['version'])
        else:
            print("\n📋 Registration cancelled.")
            return False

    def _trigger_register_workflow(self, component_name, version, branch, release_version):
        """Trigger the existing register-component.yaml workflow"""
        print("\n🚀 Registering component...")

        # For now, show what would be done - actual GitHub API integration would go here
        print(f"   Component: {component_name}")
        print(f"   Version: {version}")
        print(f"   Branch: {branch}")
        print(f"   Release: {release_version}")
        print(f"   Timestamp: {datetime.now().isoformat()}")

        print("\n   [In production: This would trigger the register-component.yaml workflow]")
        print("   [GitHub API call would execute with these inputs]")
        print("\n✅ Registration request prepared successfully!")
        print(f"   {component_name} {version} will be included in ODH {release_version}.")
        print("\nNext: The release will include your component when triggered by release managers.")

        return True

def main():
    parser = argparse.ArgumentParser(description="ODH Component Registration")
    parser.add_argument("component_name", nargs="?", help="Component name to register")
    args = parser.parse_args()

    registrar = ODHComponentRegistrar()
    success = registrar.interactive_register(args.component_name)

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()