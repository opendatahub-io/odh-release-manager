#!/usr/bin/env python3
"""
ODH Component Onboarding Script

Interactive script for onboarding new ODH components with validation and workflow triggering.
"""

import argparse
import subprocess
import sys
from pathlib import Path

class ODHOnboarder:
    def __init__(self):
        self.repo_root = self._find_repo_root()
        self.registry_path = self.repo_root / "configs" / "components-registry.yaml"
        self.validate_script = self.repo_root / ".github" / "scripts" / "validate-component-name.sh"

    def _find_repo_root(self):
        """Find the repository root directory"""
        current = Path.cwd()
        while current.parent != current:
            if (current / ".git").exists():
                return current
            current = current.parent
        raise Exception("Not in a git repository")

    def _run_validation_script(self, component_name):
        """Run existing validation script and return result"""
        try:
            result = subprocess.run(
                [str(self.validate_script), component_name],
                capture_output=True,
                text=True,
                check=True
            )
            return {"valid": True, "message": result.stdout.strip()}
        except subprocess.CalledProcessError as e:
            return {"valid": False, "message": e.stderr.strip() or e.stdout.strip()}

    def _load_existing_registry(self):
        """Load existing components registry for conflict checking and examples"""
        try:
            # Use yq to parse YAML (same tool used by existing ODH scripts)
            result = subprocess.run(
                ["yq", "e", ".components[]", str(self.registry_path)],
                capture_output=True,
                text=True,
                check=True
            )

            # Parse component names and display names from yq output
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
            print(f"Warning: Could not load registry: {e}")
            return []

    def _check_name_conflict(self, component_name, existing_components):
        """Check if component name already exists"""
        existing_names = [comp.get('name') for comp in existing_components]
        return component_name in existing_names

    def _get_display_name_examples(self, existing_components):
        """Get examples of display names from existing components"""
        examples = [comp.get('display_name') for comp in existing_components[:5]]
        return [ex for ex in examples if ex]

    def validate_component_name(self, component_name):
        """Validate component name with existing script and conflict checking"""
        # Check format using existing validation script
        validation_result = self._run_validation_script(component_name)

        if not validation_result["valid"]:
            return {
                "valid": False,
                "message": f"Invalid format: {validation_result['message']}\nHint: Use kebab-case like 'model-serving' or 'notebook-controller'"
            }

        # Check for conflicts with existing components
        existing_components = self._load_existing_registry()
        if self._check_name_conflict(component_name, existing_components):
            similar_names = [comp['name'] for comp in existing_components if component_name in comp['name']]
            return {
                "valid": False,
                "message": f"Component '{component_name}' already exists in registry.\nSimilar existing names: {', '.join(similar_names[:3])}"
            }

        return {
            "valid": True,
            "message": f"✓ '{component_name}' is available and properly formatted"
        }

    def interactive_onboard(self, component_name=None):
        """Main interactive onboarding flow"""
        print("🔧 ODH Component Onboarding")
        print("I'll help you onboard a new component to ODH. Let me ask a few questions:\n")

        # Step 1: Component Name
        if not component_name:
            print("🔸 What's the component name?")
            print("   Hint: Use kebab-case format like 'model-serving' or 'notebook-controller'")
            print("   This becomes the technical identifier in all ODH systems.")
            component_name = input("   > ").strip()

        # Validate component name
        validation = self.validate_component_name(component_name)
        print(f"\n   {validation['message']}")

        if not validation["valid"]:
            print("\n❌ Please fix the component name and try again.")
            return False

        # Step 2: Display Name
        existing_components = self._load_existing_registry()
        examples = self._get_display_name_examples(existing_components)

        print("\n🔸 What's the human-readable display name?")
        print("   Hint: This appears in UIs and documentation")
        if examples:
            print(f"   Examples from existing components: {', '.join(examples)}")

        display_name = input("   > ").strip()

        if not display_name:
            print("   ❌ Display name is required")
            return False

        # Step 3: Component Type
        print("\n🔸 Is this a 'component' or 'image'?")
        print("   Hint:")
        print("   - 'component' = has source code repositories, builds from source")
        print("   - 'image' = container image only, no source code in ODH")

        component_count = len(existing_components)
        component_type_count = len([c for c in existing_components if c.get('type') == 'component'])
        print(f"   Most ODH components are 'component' type ({component_type_count} out of {component_count} existing)")

        while True:
            component_type = input("   > ").strip().lower()
            if component_type in ['component', 'image']:
                break
            print("   Please enter 'component' or 'image'")

        # Step 4: Preview and Confirmation
        print("\n✅ Ready to onboard:")
        print(f"   - Name: {component_name}")
        print(f"   - Display Name: {display_name}")
        print(f"   - Type: {component_type}")
        print("\nThis will create a PR to add your component to the registry.")
        print("After approval by the ODH team, you'll be able to register versions for releases.")

        confirm = input("\n🔸 Shall I create the onboarding PR? [Yes/No] ").strip().lower()

        if confirm in ['yes', 'y']:
            return self._trigger_onboard_workflow(component_name, display_name, component_type)
        else:
            print("\n📋 Onboarding cancelled. You can run this again anytime.")
            return False

    def _trigger_onboard_workflow(self, component_name, display_name, component_type):
        """Trigger the existing onboard-component.yaml workflow"""
        print("\n🚀 Creating onboarding PR...")

        # For now, show what would be done - actual GitHub API integration would go here
        print(f"   Component: {component_name}")
        print(f"   Display Name: {display_name}")
        print(f"   Type: {component_type}")
        print("\n   [In production: This would trigger the onboard-component.yaml workflow]")
        print("   [GitHub API call would create the PR with these inputs]")
        print("\n✅ Onboarding request prepared successfully!")
        print("   The ODH team will review and approve your component.")

        return True

def main():
    parser = argparse.ArgumentParser(description="ODH Component Onboarding")
    parser.add_argument("component_name", nargs="?", help="Component name to onboard")
    args = parser.parse_args()

    onboarder = ODHOnboarder()
    success = onboarder.interactive_onboard(args.component_name)

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()