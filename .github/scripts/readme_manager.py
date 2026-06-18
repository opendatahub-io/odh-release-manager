#!/usr/bin/env python3
"""
Unified README Manager for ODH Release Manager

This script consolidates three separate README operations:
- generate: Full root README generation (replaces generate_readme.sh + update_readme_status.py)
- release: Per-release README generation (replaces update_release_readme.sh)

Usage:
    python3 readme_manager.py --mode generate                    # Full root README
    python3 readme_manager.py --mode release --version v1.2.3    # Per-release README
"""

import yaml
import argparse
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class YAMLManager:
    """Handles all YAML file operations"""

    @staticmethod
    def load_release_status() -> Dict:
        """Load release status from configs/release-status.yaml"""
        try:
            with open('configs/release-status.yaml', 'r') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            print("Error: configs/release-status.yaml not found", file=sys.stderr)
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"Error parsing release-status.yaml: {e}", file=sys.stderr)
            sys.exit(1)

    @staticmethod
    def load_components_registry() -> Dict:
        """Load components registry from configs/components-registry.yaml"""
        try:
            with open('configs/components-registry.yaml', 'r') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            print("Error: configs/components-registry.yaml not found", file=sys.stderr)
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"Error parsing components-registry.yaml: {e}", file=sys.stderr)
            sys.exit(1)

    @staticmethod
    def load_release_components(version: str) -> Dict:
        """Load registered components for a specific release"""
        filepath = f"releases/{version}/components.yaml"
        try:
            with open(filepath, 'r') as f:
                return yaml.safe_load(f) or {'components': []}
        except FileNotFoundError:
            return {'components': []}
        except yaml.YAMLError as e:
            print(f"Error parsing {filepath}: {e}", file=sys.stderr)
            sys.exit(1)


class DateFormatter:
    """Handles date formatting and calculations"""

    @staticmethod
    def format_display_date(iso_string: str, format_type: str = 'full') -> str:
        """Format ISO string to display format"""
        if not iso_string or iso_string == 'null':
            return ""

        try:
            if 'T' in iso_string:
                # ISO 8601 with time
                dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
                if format_type == 'full':
                    return dt.strftime('%-d %b %Y, %H:%M UTC')
                elif format_type == 'date_only':
                    return dt.strftime('%-d %b %Y')
                elif format_type == 'short':
                    return dt.strftime('%-d %b, %H:%M UTC')
            else:
                # Date only
                dt = datetime.strptime(iso_string, '%Y-%m-%d')
                if format_type == 'full':
                    return dt.strftime('%A, %B %-d, %Y')
                else:
                    return dt.strftime('%-d %b %Y')
        except ValueError:
            # Return original string if parsing fails
            return iso_string

    @staticmethod
    def get_component_metrics(version: str) -> Tuple[int, int, int]:
        """Get component registration metrics for a release"""
        release_components = YAMLManager.load_release_components(version)
        registry = YAMLManager.load_components_registry()

        registered_count = len(release_components.get('components', []))
        total_count = len(registry.get('components', []))

        if total_count > 0:
            completion_percentage = (registered_count * 100) // total_count
        else:
            completion_percentage = 0

        return registered_count, total_count, completion_percentage


class MarkdownBuilder:
    """Handles markdown content generation"""

    @staticmethod
    def generate_status_section(current_release: Optional[Dict], next_release: Optional[Dict] = None) -> str:
        """Generate current release status section"""
        # If current release is completed, show next scheduled release instead
        if current_release and current_release.get('status') == 'completed':
            if next_release and next_release.get('enabled') and next_release.get('version'):
                # Show next scheduled release
                version = next_release.get('version', '')
                registered_count, total_count, completion_percentage = DateFormatter.get_component_metrics(version)

                # Format release date
                release_date = next_release.get('release_date', '')
                if release_date:
                    formatted_release_date = DateFormatter.format_display_date(release_date, 'full')
                    release_info = f"Release Date: {formatted_release_date}"
                else:
                    release_info = "Release Date: Not set"

                # Format code freeze status
                code_freeze_date = next_release.get('code_freeze_date', '')
                if code_freeze_date:
                    freeze_date = DateFormatter.format_display_date(code_freeze_date, 'full')
                    freeze_status = f"Code Freeze: {freeze_date}"
                else:
                    freeze_status = "No code freeze deadline set"

                return f"""**Scheduled Release: {version}**

{release_info}
Progress: {registered_count}/{total_count} components registered ({completion_percentage}%)
{freeze_status}
**[View Release Details](./releases/{version}/README.md)**"""
            else:
                return "**No active release**"

        # Handle active scheduled release
        if not current_release or not current_release.get('version'):
            return "**No active release**"

        status = current_release.get('status')
        version = current_release.get('version', '')

        if status == 'scheduled':
            release_date = current_release.get('release_date', '')
            code_freeze_deadline = current_release.get('code_freeze_deadline', '')

            # Get component metrics
            registered_count, total_count, completion_percentage = DateFormatter.get_component_metrics(version)

            # Format release date
            if release_date:
                formatted_release_date = DateFormatter.format_display_date(release_date, 'full')
                release_info = f"Release Date: {formatted_release_date}"
            else:
                release_info = "Release Date: Not set"

            # Format code freeze status
            if code_freeze_deadline:
                freeze_date = DateFormatter.format_display_date(code_freeze_deadline, 'full')
                freeze_status = f"Code Freeze: {freeze_date}"
            else:
                freeze_status = "No code freeze deadline set"

            return f"""**Scheduled Release: {version}**

{release_info}
Progress: {registered_count}/{total_count} components registered ({completion_percentage}%)
{freeze_status}
**[View Release Details](./releases/{version}/README.md)**"""

        elif status == 'awaiting_validation':
            # Build status display for awaiting validation
            status_lines = [f"**Current Release: {version}**"]
            status_lines.append("- Status: Awaiting validation")

            # Check if staging details are available
            external_url = current_release.get('external_run_url')
            if external_url and external_url != 'null':
                status_lines.append(f"- Staging: [View external workflow]({external_url})")

            # Add validation note
            status_lines.append("- Ready for validation approval via Release Validation workflow")
            status_lines.append(f"- **[View Release Details](./releases/{version}/README.md)**")

            return "\n".join(status_lines)

        elif status == 'in_progress_community_release':
            # Build status display for community release in progress
            status_lines = [f"**Current Release: {version}**"]
            status_lines.append("- Status: Community release in progress")

            # Add release validation information if available
            release_validation = current_release.get('release_validation', {})
            if release_validation and release_validation.get('validated_by'):
                validator = release_validation.get('validated_by')
                validation_timestamp = release_validation.get('validated_at', '')

                if validation_timestamp and validation_timestamp != 'null':
                    formatted_time = DateFormatter.format_display_date(validation_timestamp, 'short')
                    status_lines.append(f"- Validation: {validator} at {formatted_time}")
                else:
                    status_lines.append(f"- Validation: {validator}")

            # Check for community release details
            community_release = current_release.get('community_release', {})
            triggered_at = community_release.get('triggered_at')
            if triggered_at and triggered_at != 'null':
                formatted_trigger = DateFormatter.format_display_date(triggered_at, 'short')
                status_lines.append(f"- Community Release: Triggered at {formatted_trigger}")
            else:
                status_lines.append("- Community Release: In progress")

            # Check for PR URL if available
            pr_url = community_release.get('pr_url')
            if pr_url and pr_url != 'null':
                status_lines.append(f"- Community PR: [View PR]({pr_url})")

            status_lines.append(f"- **[View Release Details](./releases/{version}/README.md)**")

            return "\n".join(status_lines)

        elif status == 'completed':
            # Build status display for completed release with validation info
            status_lines = [f"**Current Release: {version}**"]
            status_lines.append("- Status: Completed")

            # Add release validation information if available
            release_validation = current_release.get('release_validation', {})
            if release_validation and release_validation.get('validated_by'):
                validator = release_validation.get('validated_by')
                validation_timestamp = release_validation.get('validated_at', '')

                if validation_timestamp and validation_timestamp != 'null':
                    formatted_time = DateFormatter.format_display_date(validation_timestamp, 'short')
                    status_lines.append(f"- Validation: {validator} at {formatted_time}")
                else:
                    status_lines.append(f"- Validation: {validator}")

            # Add community release info if available
            community_release = current_release.get('community_release', {})
            if community_release and community_release.get('pr_merged'):
                pr_url = community_release.get('pr_url')
                if pr_url and pr_url != 'null':
                    status_lines.append(f"- Community Release: [Merged]({pr_url})")
                else:
                    status_lines.append("- Community Release: Merged")

            completed_at = current_release.get('completed_at')
            if completed_at and completed_at != 'null':
                formatted_completion = DateFormatter.format_display_date(completed_at, 'short')
                status_lines.append(f"- Completed: {formatted_completion}")

            status_lines.append(f"- **[View Release Details](./releases/{version}/README.md)**")

            return "\n".join(status_lines)

        else:
            return f"""**Current Release: {version}**
- Status: {status}
- **[View Release Details](./releases/{version}/README.md)**"""

    @staticmethod
    def generate_next_release_alert(next_release: Dict, current_release: Optional[Dict] = None) -> str:
        """Generate GitHub alert box for next release"""
        if not next_release.get('enabled'):
            return ""

        # Don't show alert if current release is completed and next release is already shown in status section
        if current_release and current_release.get('status') == 'completed':
            return ""

        version = next_release.get('version', '')
        release_date = next_release.get('release_date', '')
        code_freeze_date = next_release.get('code_freeze_date', '')

        if not (version and release_date and code_freeze_date):
            return ""

        # Get component progress for the next release
        registered_count, total_count, completion_percentage = DateFormatter.get_component_metrics(version)

        # Format dates
        release_formatted = DateFormatter.format_display_date(release_date, 'full')
        freeze_formatted = DateFormatter.format_display_date(code_freeze_date, 'full')

        return f"""

> [!IMPORTANT]
> **Scheduled Release: {version}**
>
> **Release Date:** {release_formatted}
> **Progress:** {registered_count}/{total_count} components registered ({completion_percentage}%)
> **Code Freeze:** {freeze_formatted}
> **[View Release Details](./releases/{version}/README.md)** • **[Register Component](https://github.com/opendatahub-io/odh-release-manager/actions/workflows/register-component.yaml)**"""

    @staticmethod
    def generate_release_history_table(release_history: List[Dict]) -> str:
        """Generate release history table"""
        if not release_history:
            return """| | | | | | |

*No releases yet. Release history will appear here after the first release is triggered.*"""

        rows = []
        for release in release_history:
            version = release.get('version', '')
            status = release.get('status', '')
            created_at = release.get('created_at', '')
            completed = release.get('completed_at', '')

            # Format dates
            created_date = DateFormatter.format_display_date(created_at, 'date_only')
            completed_date = DateFormatter.format_display_date(completed, 'date_only') if completed and completed != 'null' else ""

            # Status icon
            status_icon = {
                'completed': 'Released',
                'scheduled': 'Scheduled',
                'awaiting_validation': 'Pending Validation',
                'in_progress_community_release': 'Community Release',
                'failed': 'Failed'
            }.get(status, status)

            # Validation info
            validation_info = ""
            release_validation = release.get('release_validation', {})
            if release_validation and release_validation.get('validated_by'):
                validator = release_validation.get('validated_by')
                validation_info = f"{validator}"

            # Links
            links = ""
            if os.path.exists(f"./releases/{version}/README.md"):
                links = f"[Components](./releases/{version}/README.md)"

            rows.append(f"| {version} | {status_icon} | {created_date} | {completed_date} | {validation_info} | {links} |")

        return "\n".join(rows)

    @staticmethod
    def generate_component_status_table(version: str) -> Tuple[str, int, int]:
        """Generate component status table for per-release README"""
        registry = YAMLManager.load_components_registry()
        release_components = YAMLManager.load_release_components(version)

        # Build registered components lookup
        registered_components = {}
        for component in release_components.get('components', []):
            name = component.get('name')
            if name:
                registered_components[name] = component

        # Generate table rows
        rows = []
        registered_count = 0
        pending_count = 0

        for component in registry.get('components', []):
            comp_name = component.get('name', '')
            display_name = component.get('display_name', comp_name)
            comp_type = component.get('type', '')

            if comp_name in registered_components:
                # Component is registered
                reg_comp = registered_components[comp_name]
                version_str = reg_comp.get('version', '')

                if reg_comp.get('type') == 'image' or comp_type == 'image':
                    branch = "(image)"
                else:
                    branch = reg_comp.get('branch', '')

                reg_date = DateFormatter.format_display_date(
                    reg_comp.get('registered_at', ''), 'short'
                )

                rows.append(f"| {display_name} | 🟢 Registered | {version_str} | {branch} | {reg_date} |")
                registered_count += 1
            else:
                # Component not registered
                rows.append(f"| {display_name} | 🔴 Pending | - | - | - |")
                pending_count += 1

        table_content = "\n".join(rows)
        return table_content, registered_count, pending_count


class FileManager:
    """Handles file I/O operations"""

    @staticmethod
    def read_readme(path: str = 'README.md') -> str:
        """Read README content"""
        try:
            with open(path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Error: {path} not found", file=sys.stderr)
            sys.exit(1)

    @staticmethod
    def write_readme(path: str, content: str) -> None:
        """Write README content"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)

            with open(path, 'w') as f:
                f.write(content)
            print(f"Successfully updated {path}")
        except Exception as e:
            print(f"Error writing {path}: {e}", file=sys.stderr)
            sys.exit(1)



def generate_root_readme():
    """Generate complete root README (replaces generate_readme.sh)"""
    print("Generating README.md...")

    # Load data
    release_status = YAMLManager.load_release_status()
    current_release = release_status.get('current_release')
    next_release = release_status.get('next_release', {})
    release_history = release_status.get('release_history', [])

    # Generate content sections
    status_section = MarkdownBuilder.generate_status_section(current_release, next_release)
    alert_box = MarkdownBuilder.generate_next_release_alert(next_release, current_release)
    history_table = MarkdownBuilder.generate_release_history_table(release_history)

    # Generate complete README content
    readme_content = f"""# ODH Release Manager

This repository manages the OpenDataHub release process through GitOps principles.

## Current Release Status

{status_section}{alert_box}

## Recent Release History

| Version | Status | Triggered | Released | Validation | Links |
|---------|--------|-----------|----------|------------|--------|
{history_table}

## Usage

### For New Component Teams
1. **Add your component**: Use the [Onboard Component](https://github.com/opendatahub-io/odh-release-manager/actions/workflows/onboard-component.yaml) workflow
2. **Wait for approval**: Release managers will review and approve your component request
3. **Start participating**: Once approved, register versions using the Register Component workflow
4. **Need help?**: See the [Component Onboarding Guide](docs/component-onboarding.md)

### For Existing Component Teams
1. **Register your component**: Use the [Register Component](https://github.com/opendatahub-io/odh-release-manager/actions/workflows/register-component.yaml) workflow
   - Select your component from the dropdown (auto-synced with registry)
   - Release version auto-detected from current active release (or specify manually)
2. **Track registration**: Check component status in release README: `./releases/<version>/README.md`

### For Release Managers
1. **Trigger release**: Use the [Trigger Release](https://github.com/opendatahub-io/odh-release-manager/actions/workflows/trigger-release.yaml) workflow
2. **Monitor progress**: Check status updates in this README and external workflow links
3. **Review new components**: Approve component addition requests via pull requests

## Repository Structure
```
├── configs/
│   ├── components-registry.yaml    # Master component registry (source of truth)
│   └── release-status.yaml         # Current and historical release status
├── releases/
│   └── <version>/
│       ├── components.yaml         # Registered components for this release
│       └── README.md              # Per-release component status
├── docs/
│   └── component-onboarding.md     # Guide for new component teams
└── .github/
    ├── CODEOWNERS                  # Required reviewers for sensitive files
    ├── pull_request_template.md    # PR template for component additions
    ├── scripts/
    │   ├── validate-component-name.sh  # Component name validation
    │   └── validate-display-name.sh    # Display name validation
    └── workflows/
        ├── register-component.yaml     # Component registration workflow
        ├── onboard-component.yaml          # Self-service component onboarding
        ├── sync-component-dropdown.yaml    # Auto-sync dropdown with registry
        ├── trigger-release.yaml            # Release trigger workflow
        └── complete-release.yaml           # Release completion workflow
```

## How It Works

### Component Registration Flow
1. Component teams use the "Register Component" workflow to register their component version for a release
   - Dropdown automatically synced with approved components from the registry
2. Data is stored in `releases/<version>/components.yaml` with validation against the component registry
3. Per-release README is auto-generated showing registration progress

### Component Onboarding Flow
1. New teams use "Onboard Component" workflow to request component addition
2. Automated PR created for registry update and review by release managers
3. Once approved, "Sync Component Dropdown" automatically updates registration workflow
4. Component immediately available in registration dropdown

### Release Trigger Flow
1. Release managers use the "Trigger Release" workflow when components are ready
2. System automatically fills missing components from the previous release (fallback)
3. Complete component mapping is passed to `opendatahub-operator/release-staging.yaml`
4. External workflow builds and creates the actual release
5. Status is tracked and displayed in this README

### Previous Release Fallback
If a component is not registered for the current release, the system automatically uses the version from the most recent completed release. This ensures no components are accidentally excluded from releases.
"""

    # Write README
    FileManager.write_readme('README.md', readme_content)

    # Print summary
    total_releases = len(release_history)
    current_version = current_release.get('version') if current_release else None
    print(f"Generated README for {total_releases} historical releases")
    if current_version:
        print(f"Current release: {current_version}")



def update_release_readme(version: str):
    """Update per-release README (replaces update_release_readme.sh)"""
    print(f"Updating README for release: {version}")

    # Generate component table and get metrics
    table_content, registered_count, pending_count = MarkdownBuilder.generate_component_status_table(version)
    total_count = registered_count + pending_count

    if total_count > 0:
        completion_percentage = (registered_count * 100) // total_count
    else:
        completion_percentage = 0

    # Generate release README content
    release_dir = f"releases/{version}"
    readme_content = f"""# Release {version}

**Progress**: {registered_count}/{total_count} components registered ({completion_percentage}%)

## Component Registration Status

| Display Name | Status | Version | Branch | Registered At |
|--------------|--------|---------|--------|---------------|
{table_content}

"""

    # Write release README
    readme_path = f"{release_dir}/README.md"
    FileManager.write_readme(readme_path, readme_content)

    # Print summary
    print("Component status:")
    print(f"  Total: {total_count}")
    print(f"  Registered: {registered_count}")
    print(f"  Pending: {pending_count}")
    print(f"Release README updated successfully")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Unified README Manager for ODH Release Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 readme_manager.py --mode generate                    # Generate full root README
  python3 readme_manager.py --mode release --version v1.2.3    # Generate per-release README
        """
    )

    parser.add_argument(
        '--mode',
        choices=['generate', 'release'],
        required=True,
        help='README operation mode'
    )

    parser.add_argument(
        '--version',
        help='Release version (required for release mode)'
    )

    args = parser.parse_args()

    # Validate arguments
    if args.mode == 'release' and not args.version:
        print("Error: --version is required for release mode", file=sys.stderr)
        sys.exit(1)

    # Execute appropriate mode
    try:
        if args.mode == 'generate':
            generate_root_readme()
        elif args.mode == 'release':
            update_release_readme(args.version)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()