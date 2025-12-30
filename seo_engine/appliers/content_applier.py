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
        elif update_type == 'cta':
            self._update_cta(file_path, recommended)
        elif update_type == 'content_expansion':
            self._add_content_sections(file_path, recommended)
        elif update_type == 'headings':
            self._update_headings(file_path, recommended)
        elif update_type == 'internal_links':
            self._add_internal_links(file_path, recommended)
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

    def _update_cta(self, file_path: Path, cta_content: str) -> None:
        """Update CTA in frontmatter for template use"""
        if self.dry_run:
            print(f"   [DRY RUN] Would update CTA")
            return

        try:
            content = file_path.read_text(encoding='utf-8')

            # Parse the CTA recommendation
            cta_data = {}
            for line in cta_content.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace(' ', '_')
                    cta_data[key] = value.strip()

            if not cta_data:
                print(f"   ⚠ Could not parse CTA content")
                return

            # Update frontmatter with CTA fields
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1]) or {}
                    body = parts[2]

                    # Add CTA fields to frontmatter
                    if 'primary_cta' in cta_data:
                        frontmatter['cta_button'] = cta_data['primary_cta']
                    if 'primary_headline' in cta_data:
                        frontmatter['cta_headline'] = cta_data['primary_headline']
                    if 'primary_subtext' in cta_data:
                        frontmatter['cta_subtext'] = cta_data['primary_subtext']
                    if 'secondary_cta' in cta_data:
                        frontmatter['cta_secondary'] = cta_data['secondary_cta']

                    # Rebuild file
                    new_frontmatter = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
                    new_content = f"---\n{new_frontmatter}---{body}"

                    file_path.write_text(new_content, encoding='utf-8')
                    print(f"   ✓ Updated CTA in frontmatter")

                    self.changes.append(AppliedChange(
                        file_path=str(file_path),
                        change_type="cta",
                        field="cta",
                        old_value="",
                        new_value=cta_data.get('primary_cta', '')[:50],
                        status="applied"
                    ))

        except Exception as e:
            print(f"   ✗ Error updating CTA: {e}")

    def _add_content_sections(self, file_path: Path, new_sections: str) -> None:
        """Add new content sections to expand thin pages"""
        if self.dry_run:
            print(f"   [DRY RUN] Would add content sections")
            return

        try:
            content = file_path.read_text(encoding='utf-8')

            # Add new sections before the FAQ or last CTA, or at end
            insert_point = None

            # Try to find FAQ section
            faq_match = re.search(r'\n##\s*(?:Frequently Asked Questions|FAQ)', content, re.IGNORECASE)
            if faq_match:
                insert_point = faq_match.start()

            # Try to find last CTA
            if insert_point is None and '{{template:cta' in content:
                insert_point = content.rfind('{{template:cta')

            if insert_point:
                new_content = content[:insert_point] + f"\n\n{new_sections}\n\n" + content[insert_point:]
            else:
                new_content = content + f"\n\n{new_sections}\n"

            file_path.write_text(new_content, encoding='utf-8')
            print(f"   ✓ Added content sections")

            self.changes.append(AppliedChange(
                file_path=str(file_path),
                change_type="content_expansion",
                field="content",
                old_value="",
                new_value=new_sections[:100],
                status="applied"
            ))

        except Exception as e:
            print(f"   ✗ Error adding content sections: {e}")

    def _update_headings(self, file_path: Path, heading_suggestions: str) -> None:
        """Update headings based on AI suggestions"""
        if self.dry_run:
            print(f"   [DRY RUN] Would update headings")
            return

        try:
            content = file_path.read_text(encoding='utf-8')
            changes_made = 0

            # Parse heading suggestions (CURRENT: ... OPTIMIZED: ... format)
            current_pattern = re.compile(r'CURRENT:\s*(.+?)(?:\n|$)', re.IGNORECASE)
            optimized_pattern = re.compile(r'OPTIMIZED:\s*(.+?)(?:\n|$)', re.IGNORECASE)

            currents = current_pattern.findall(heading_suggestions)
            optimizeds = optimized_pattern.findall(heading_suggestions)

            for current, optimized in zip(currents, optimizeds):
                current = current.strip()
                optimized = optimized.strip()

                if current and optimized and current != optimized:
                    # Try to find and replace the heading
                    # Match ## Current Heading or ### Current Heading
                    heading_regex = re.compile(
                        r'^(#{2,3})\s*' + re.escape(current) + r'\s*$',
                        re.MULTILINE | re.IGNORECASE
                    )

                    if heading_regex.search(content):
                        content = heading_regex.sub(r'\1 ' + optimized, content)
                        changes_made += 1

            if changes_made > 0:
                file_path.write_text(content, encoding='utf-8')
                print(f"   ✓ Updated {changes_made} headings")

                self.changes.append(AppliedChange(
                    file_path=str(file_path),
                    change_type="headings",
                    field="headings",
                    old_value=f"{changes_made} headings",
                    new_value="optimized",
                    status="applied"
                ))
            else:
                print(f"   ℹ No heading matches found to update")

        except Exception as e:
            print(f"   ✗ Error updating headings: {e}")

    def _add_internal_links(self, file_path: Path, link_suggestions: str) -> None:
        """Add internal links based on AI suggestions"""
        if self.dry_run:
            print(f"   [DRY RUN] Would add internal links")
            return

        try:
            content = file_path.read_text(encoding='utf-8')
            changes_made = 0

            # Parse link suggestions (ANCHOR_TEXT: ... LINK_TO: ... format)
            anchor_pattern = re.compile(r'ANCHOR_TEXT:\s*(.+?)(?:\n|$)', re.IGNORECASE)
            link_pattern = re.compile(r'LINK_TO:\s*(.+?)(?:\n|$)', re.IGNORECASE)

            anchors = anchor_pattern.findall(link_suggestions)
            links = link_pattern.findall(link_suggestions)

            for anchor, link_url in zip(anchors, links):
                anchor = anchor.strip()
                link_url = link_url.strip()

                if anchor and link_url:
                    # Only link first occurrence that isn't already linked
                    # Check if anchor text exists and isn't already a link
                    if anchor in content:
                        # Make sure it's not already linked
                        already_linked = re.search(
                            r'\[' + re.escape(anchor) + r'\]\([^)]+\)',
                            content
                        )

                        if not already_linked:
                            # Replace first occurrence only
                            content = content.replace(
                                anchor,
                                f'[{anchor}]({link_url})',
                                1
                            )
                            changes_made += 1

            if changes_made > 0:
                file_path.write_text(content, encoding='utf-8')
                print(f"   ✓ Added {changes_made} internal links")

                self.changes.append(AppliedChange(
                    file_path=str(file_path),
                    change_type="internal_links",
                    field="links",
                    old_value="",
                    new_value=f"{changes_made} links added",
                    status="applied"
                ))
            else:
                print(f"   ℹ No link opportunities found")

        except Exception as e:
            print(f"   ✗ Error adding internal links: {e}")

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
