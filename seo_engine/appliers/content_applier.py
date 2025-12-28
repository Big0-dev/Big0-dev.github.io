"""
Content Applier - Automatically implements SEO recommendations

This module reads recommendations and applies them to content files:
- Updates meta titles in frontmatter
- Updates meta descriptions
- Adds FAQ sections
- Adds target keywords to frontmatter
- Tracks changes for review
"""

import json
import re
import yaml
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

from ..config import Config


@dataclass
class AppliedChange:
    """Record of an applied change"""
    file_path: str
    change_type: str
    field: str
    old_value: str
    new_value: str
    applied_at: datetime = field(default_factory=datetime.now)
    status: str = "applied"  # applied, skipped, failed


class ContentApplier:
    """
    Applies SEO recommendations to content files automatically.
    """

    def __init__(self, config: Config):
        self.config = config
        self.changes: list[AppliedChange] = []
        self.dry_run = False

    def apply_recommendations(
        self,
        updates_file: Path,
        dry_run: bool = False,
        auto_approve: bool = False
    ) -> list[AppliedChange]:
        """
        Apply recommendations from a content_updates JSON file.

        Args:
            updates_file: Path to content_updates_*.json
            dry_run: If True, show what would change without modifying files
            auto_approve: If True, apply all changes without confirmation

        Returns:
            List of applied changes
        """
        self.dry_run = dry_run
        self.changes = []

        if not updates_file.exists():
            print(f"Updates file not found: {updates_file}")
            return []

        with open(updates_file) as f:
            data = json.load(f)

        updates = data.get('updates', [])
        pending = [u for u in updates if u.get('status') == 'pending']

        print(f"\n{'[DRY RUN] ' if dry_run else ''}Applying {len(pending)} recommendations...")
        print("=" * 60)

        for update in pending:
            self._apply_single_update(update, auto_approve)

        # Save change log
        if not dry_run:
            self._save_change_log()
            self._update_status_file(updates_file, data)

        return self.changes

    def _apply_single_update(self, update: dict, auto_approve: bool) -> None:
        """Apply a single recommendation"""
        page_url = update.get('page_url', '')
        update_type = update.get('type', '')
        current = update.get('current_value', '')
        recommended = update.get('recommended_value', '')
        keywords = update.get('target_keywords', [])

        # Find the corresponding file
        file_path = self._url_to_file_path(page_url)
        if not file_path or not file_path.exists():
            print(f"  ⚠ File not found for: {page_url}")
            return

        print(f"\n📄 {file_path.name}")
        print(f"   Type: {update_type}")
        print(f"   Current:     {current[:50]}..." if len(current) > 50 else f"   Current:     {current}")
        print(f"   Recommended: {recommended[:50]}..." if len(recommended) > 50 else f"   Recommended: {recommended}")

        if not auto_approve and not self.dry_run:
            response = input("   Apply? [y/n/s(kip all)]: ").strip().lower()
            if response == 's':
                print("   Skipping all remaining...")
                return
            if response != 'y':
                print("   Skipped")
                self.changes.append(AppliedChange(
                    file_path=str(file_path),
                    change_type=update_type,
                    field=update_type,
                    old_value=current,
                    new_value=recommended,
                    status="skipped"
                ))
                return

        # Apply the change
        if update_type == 'meta_title':
            self._update_frontmatter(file_path, 'title', recommended, current)
        elif update_type == 'meta_description':
            self._update_frontmatter(file_path, 'meta_description', recommended, current)
        elif update_type == 'faq':
            self._add_faq_section(file_path, recommended)
        elif update_type == 'content':
            # Content suggestions are logged but need manual review
            print("   ℹ Content suggestions require manual review")
            self.changes.append(AppliedChange(
                file_path=str(file_path),
                change_type=update_type,
                field="content",
                old_value="",
                new_value=recommended,
                status="manual_review"
            ))

        # Add target keywords to frontmatter
        if keywords and update_type in ['meta_title', 'meta_description']:
            self._update_frontmatter_keywords(file_path, keywords)

    def _url_to_file_path(self, url: str) -> Optional[Path]:
        """Convert a page URL to its source file path"""
        # Remove domain
        path = url.replace(self.config.site_domain, '').strip('/')

        # Handle different content types
        if path.startswith('services/locations/'):
            # Location pages: services/locations/usa/ai-ml-services-usa.html
            # -> content/services/locations/usa/ai-ml-services-usa.md
            md_path = path.replace('.html', '.md')
            return self.config.content_dir / md_path

        elif path.startswith('services/'):
            md_path = path.replace('.html', '.md')
            return self.config.content_dir / md_path

        elif path.startswith('industries/'):
            md_path = path.replace('.html', '.md')
            return self.config.content_dir / md_path

        elif path.startswith('blogs/'):
            md_path = path.replace('.html', '.md')
            return self.config.content_dir / md_path

        elif path.startswith('case-studies/'):
            md_path = path.replace('case-studies/', 'case_studies/').replace('.html', '.md')
            return self.config.content_dir / md_path

        elif path.startswith('news/'):
            md_path = path.replace('.html', '.md')
            return self.config.content_dir / md_path

        return None

    def _update_frontmatter(self, file_path: Path, field: str, new_value: str, old_value: str) -> None:
        """Update a field in the frontmatter"""
        if self.dry_run:
            print(f"   [DRY RUN] Would update {field}")
            self.changes.append(AppliedChange(
                file_path=str(file_path),
                change_type="frontmatter",
                field=field,
                old_value=old_value,
                new_value=new_value,
                status="dry_run"
            ))
            return

        try:
            content = file_path.read_text(encoding='utf-8')

            # Parse frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1]) or {}
                    body = parts[2]

                    # Update field
                    frontmatter[field] = new_value

                    # Rebuild file
                    new_frontmatter = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
                    new_content = f"---\n{new_frontmatter}---{body}"

                    file_path.write_text(new_content, encoding='utf-8')

                    print(f"   ✓ Updated {field}")
                    self.changes.append(AppliedChange(
                        file_path=str(file_path),
                        change_type="frontmatter",
                        field=field,
                        old_value=old_value,
                        new_value=new_value,
                        status="applied"
                    ))
            else:
                print(f"   ⚠ No frontmatter found in {file_path.name}")

        except Exception as e:
            print(f"   ✗ Error updating {field}: {e}")
            self.changes.append(AppliedChange(
                file_path=str(file_path),
                change_type="frontmatter",
                field=field,
                old_value=old_value,
                new_value=new_value,
                status="failed"
            ))

    def _update_frontmatter_keywords(self, file_path: Path, keywords: list[str]) -> None:
        """Add target keywords to frontmatter"""
        if self.dry_run:
            return

        try:
            content = file_path.read_text(encoding='utf-8')

            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1]) or {}
                    body = parts[2]

                    # Merge keywords
                    existing = frontmatter.get('keywords', [])
                    if isinstance(existing, str):
                        existing = [k.strip() for k in existing.split(',')]

                    merged = list(set(existing + keywords))
                    frontmatter['keywords'] = merged

                    # Rebuild file
                    new_frontmatter = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
                    new_content = f"---\n{new_frontmatter}---{body}"

                    file_path.write_text(new_content, encoding='utf-8')

        except Exception as e:
            print(f"   ⚠ Could not add keywords: {e}")

    def _add_faq_section(self, file_path: Path, faq_content: str) -> None:
        """Add FAQ section to content"""
        if self.dry_run:
            print(f"   [DRY RUN] Would add FAQ section")
            return

        try:
            content = file_path.read_text(encoding='utf-8')

            # Check if FAQ already exists
            if 'frequently asked questions' in content.lower() or '## faq' in content.lower():
                print(f"   ℹ FAQ section already exists, skipping")
                return

            # Add FAQ before the last CTA template or at the end
            if '{{template:cta' in content:
                # Insert before last CTA
                last_cta = content.rfind('{{template:cta')
                new_content = content[:last_cta] + f"\n\n## Frequently Asked Questions\n\n{faq_content}\n\n" + content[last_cta:]
            else:
                # Append to end
                new_content = content + f"\n\n## Frequently Asked Questions\n\n{faq_content}\n"

            file_path.write_text(new_content, encoding='utf-8')
            print(f"   ✓ Added FAQ section")

            self.changes.append(AppliedChange(
                file_path=str(file_path),
                change_type="content",
                field="faq",
                old_value="",
                new_value=faq_content[:100],
                status="applied"
            ))

        except Exception as e:
            print(f"   ✗ Error adding FAQ: {e}")

    def _save_change_log(self) -> None:
        """Save log of all changes"""
        log_file = self.config.output_dir / f"changes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        log_data = {
            'applied_at': datetime.now().isoformat(),
            'total_changes': len(self.changes),
            'applied': len([c for c in self.changes if c.status == 'applied']),
            'skipped': len([c for c in self.changes if c.status == 'skipped']),
            'failed': len([c for c in self.changes if c.status == 'failed']),
            'changes': [
                {
                    'file': c.file_path,
                    'type': c.change_type,
                    'field': c.field,
                    'old': c.old_value[:100] if c.old_value else '',
                    'new': c.new_value[:100] if c.new_value else '',
                    'status': c.status,
                }
                for c in self.changes
            ]
        }

        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)

        print(f"\n📋 Change log saved: {log_file}")

    def _update_status_file(self, updates_file: Path, data: dict) -> None:
        """Mark applied updates as 'implemented' in the source file"""
        for update in data.get('updates', []):
            for change in self.changes:
                if change.status == 'applied' and update.get('page_url', '') in change.file_path:
                    update['status'] = 'implemented'
                    update['implemented_at'] = datetime.now().isoformat()

        with open(updates_file, 'w') as f:
            json.dump(data, f, indent=2)


def apply_latest_recommendations(config: Config, dry_run: bool = False, auto_approve: bool = False):
    """Helper function to apply the most recent recommendations"""
    reports_dir = config.output_dir

    # Find the latest content_updates file
    update_files = sorted(reports_dir.glob("content_updates_*.json"), reverse=True)

    if not update_files:
        print("No recommendation files found. Run analysis first:")
        print("  uv run python -m seo_engine --full")
        return

    latest = update_files[0]
    print(f"Using latest recommendations: {latest.name}")

    applier = ContentApplier(config)
    changes = applier.apply_recommendations(latest, dry_run=dry_run, auto_approve=auto_approve)

    # Summary
    applied = len([c for c in changes if c.status == 'applied'])
    skipped = len([c for c in changes if c.status == 'skipped'])
    failed = len([c for c in changes if c.status == 'failed'])

    print(f"\n{'='*60}")
    print(f"Summary: {applied} applied, {skipped} skipped, {failed} failed")

    if applied > 0:
        print("\nNext step: Rebuild the site to see changes:")
        print("  uv run python generate.py")
