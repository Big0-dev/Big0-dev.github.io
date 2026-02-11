"""
Asset Manager Module for Big0 Site Generator

Handles all asset operations including:
- Static file copying
- SVG injection with caching
- Gallery image handling
- Output minification (HTML, CSS, JS)
"""

import os
import re
import shutil
import json
import logging
from pathlib import Path
from datetime import datetime
from functools import lru_cache
from typing import Dict, Any, List, Optional, Set

import minify_html
import rcssmin

logger = logging.getLogger(__name__)


class AssetManager:
    """Manages all asset operations for the site generator"""

    def __init__(self, config: Dict[str, Any], static_dir: str, output_dir: str):
        """
        Initialize AssetManager

        Args:
            config: Site configuration dictionary
            static_dir: Path to static assets directory
            output_dir: Path to build output directory
        """
        self.config = config
        self.static_dir = static_dir
        self.output_dir = output_dir
        self._svg_cache = {}

    _IMAGE_EXTENSIONS = {'.avif', '.jpg', '.jpeg', '.png', '.webp'}

    def _collect_referenced_images(self) -> Set[str]:
        """Scan templates and content to find all referenced image filenames."""
        referenced: Set[str] = set()

        # Pattern for any image filename (with extension) appearing in source files
        image_pattern = re.compile(
            r'([\w][\w.\-]*\.(?:avif|jpg|jpeg|png|webp))',
            re.IGNORECASE,
        )

        # Pattern for frontmatter fields where templates append .avif
        bare_pattern = re.compile(
            r'^(?:hero_image|image_url|preload):\s*(\S+)\s*$',
            re.MULTILINE,
        )

        all_files: list[tuple[str, str]] = []

        # Collect file contents
        templates_dir = Path("templates")
        if templates_dir.exists():
            for f in templates_dir.rglob("*.html"):
                all_files.append(("template", f.read_text(encoding="utf-8", errors="ignore")))

        content_dir = Path("content")
        if content_dir.exists():
            for f in content_dir.rglob("*.md"):
                all_files.append(("content", f.read_text(encoding="utf-8", errors="ignore")))

        config_path = Path("site_config.yaml")
        if config_path.exists():
            all_files.append(("config", config_path.read_text(encoding="utf-8")))

        static_images = {p.name for p in Path(self.static_dir).glob("*") if p.suffix.lower() in self._IMAGE_EXTENSIONS}

        for source_type, text in all_files:
            for m in image_pattern.finditer(text):
                referenced.add(Path(m.group(1)).name)
            # Check bare names (no extension) that resolve to actual image files
            for m in bare_pattern.finditer(text):
                bare_name = m.group(1)
                if '.' not in bare_name:
                    for ext in ('.avif', '.jpg', '.png', '.webp'):
                        candidate = bare_name + ext
                        if candidate in static_images:
                            referenced.add(candidate)

        return referenced

    def copy_static_assets(self, source: Optional[str] = None, destination: Optional[str] = None) -> None:
        """
        Copy static assets excluding SVGs and favicon files.
        Only copies image files that are referenced in templates or content.

        Args:
            source: Source directory (defaults to self.static_dir)
            destination: Destination directory (defaults to output_dir/static)
        """
        source_dir = source or self.static_dir
        dest_dir = destination or os.path.join(self.output_dir, "static")

        if not os.path.exists(source_dir):
            logger.warning(f"Static directory not found: {source_dir}")
            return

        os.makedirs(dest_dir, exist_ok=True)

        referenced_images = self._collect_referenced_images()
        copied = skipped = 0

        for item in os.listdir(source_dir):
            # Skip SVG files and favicon files (handled separately)
            if item.endswith('.svg') or item.startswith('favicon'):
                continue

            src_path = os.path.join(source_dir, item)
            dest_path = os.path.join(dest_dir, item)

            # For image files, only copy if referenced
            ext = os.path.splitext(item)[1].lower()
            if ext in self._IMAGE_EXTENSIONS:
                if item not in referenced_images:
                    skipped += 1
                    continue

            try:
                if os.path.isfile(src_path):
                    shutil.copy2(src_path, dest_path)
                    copied += 1
                    logger.debug(f"Copied file: {item}")
                elif os.path.isdir(src_path):
                    if os.path.exists(dest_path):
                        shutil.rmtree(dest_path)
                    shutil.copytree(src_path, dest_path)
                    logger.debug(f"Copied directory: {item}")
            except Exception as e:
                logger.error(f"Error copying {item}: {e}")

        if skipped:
            logger.info(f"Copied {copied} static files, skipped {skipped} unreferenced images")

    def copy_gallery_images(self, source: Optional[str] = None, destination: Optional[str] = None) -> None:
        """
        Copy gallery images and metadata

        Args:
            source: Source gallery directory (defaults to config gallery_dir)
            destination: Destination directory (defaults to output_dir/content/gallery)
        """
        gallery_dir = source or self.config['assets']['gallery_dir']
        dest_dir = destination or os.path.join(self.output_dir, "content", "gallery")

        if not os.path.exists(gallery_dir):
            logger.warning(f"Gallery directory not found: {gallery_dir}")
            return

        os.makedirs(dest_dir, exist_ok=True)

        # Copy gallery images and metadata
        for item in os.listdir(gallery_dir):
            if item.endswith(('.avif', '.jpg', '.jpeg', '.png', '.webp', '.json')):
                src_path = os.path.join(gallery_dir, item)
                dest_path = os.path.join(dest_dir, item)

                try:
                    shutil.copy2(src_path, dest_path)
                    logger.debug(f"Copied gallery item: {item}")
                except Exception as e:
                    logger.error(f"Error copying gallery item {item}: {e}")

    def copy_root_assets(self) -> None:
        """Copy root assets and favicon files to build root"""
        # Copy configured root assets
        if 'root_assets' in self.config['assets']:
            for asset in self.config['assets']['root_assets']:
                src = Path(asset)
                if src.exists():
                    dest = Path(self.output_dir) / asset
                    try:
                        shutil.copy2(src, dest)
                        logger.debug(f"Copied root asset: {asset}")
                    except Exception as e:
                        logger.error(f"Error copying root asset {asset}: {e}")

        # Copy favicon files to build root
        favicon_files = ['favicon.ico', 'favicon.png']
        for favicon in favicon_files:
            src = Path(self.static_dir) / favicon
            if src.exists():
                dest = Path(self.output_dir) / favicon
                try:
                    shutil.copy2(src, dest)
                    logger.debug(f"Copied favicon: {favicon}")
                except Exception as e:
                    logger.error(f"Error copying favicon {favicon}: {e}")

    def copy_all_assets(self) -> None:
        """Copy all assets according to configuration"""
        logger.info("Copying assets...")
        self.copy_static_assets()
        self.copy_gallery_images()
        self.copy_root_assets()
        logger.info("Asset copying complete")

    @lru_cache(maxsize=128)
    def inject_svg(self, filename: str, wrap: bool = False, css_class: str = "") -> str:
        """
        Inject SVG content directly into HTML with caching

        Args:
            filename: SVG filename without extension
            wrap: Whether to wrap in span element
            css_class: CSS class to add to SVG element

        Returns:
            SVG content as HTML string
        """
        svg_path = Path(self.static_dir) / f"{filename}.svg"

        if not svg_path.exists():
            logger.warning(f"SVG not found: {filename}")
            return f"<!-- SVG {filename} not found -->"

        try:
            svg_content = svg_path.read_text(encoding='utf-8')

            # Replace hardcoded dark colors with currentColor for theme compatibility
            dark_colors = [
                '#000000', '#000', '#0F0F0F', '#1C1C1C', '#1C274C',
                '#212121', '#080341', '#292929'
            ]
            for color in dark_colors:
                svg_content = svg_content.replace(f'fill="{color}"', 'fill="currentColor"')
                svg_content = svg_content.replace(f'stroke="{color}"', 'stroke="currentColor"')

            if css_class:
                svg_content = svg_content.replace('<svg', f'<svg class="{css_class}"', 1)

            if wrap:
                result = f'<span class="svg-wrapper">{svg_content}</span>'
            else:
                result = svg_content

            return result

        except Exception as e:
            logger.error(f"Error injecting SVG {filename}: {e}")
            return f"<!-- Error loading SVG {filename} -->"

    def load_gallery_data(self) -> Dict[str, Any]:
        """
        Load gallery images and metadata

        Returns:
            Dictionary with images list and gallery_url
        """
        gallery_dir = Path(self.config['assets']['gallery_dir'])
        metadata_file = gallery_dir / 'metadata.json'

        images = []
        gallery_url = 'content/gallery'

        if metadata_file.exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)

                # Get all image files
                for image_file in sorted(gallery_dir.glob('*.avif')):
                    # Try to find metadata - check both with and without year variations
                    meta_key = image_file.name
                    if meta_key not in metadata:
                        # Try with 2025 instead of 25
                        alt_key = meta_key.replace('-25-', '-2025-')
                        if alt_key in metadata:
                            meta_key = alt_key

                    if meta_key in metadata:
                        image_data = metadata[meta_key].copy()
                        image_data['filename'] = image_file.name
                        # Parse date if present
                        if 'date' in image_data:
                            try:
                                image_data['date'] = datetime.strptime(image_data['date'], '%Y-%m-%d')
                            except ValueError as e:
                                logger.warning(f"Invalid date format for {image_file.name}: {e}")
                        images.append(image_data)
                    else:
                        # Add image even without metadata
                        images.append({
                            'filename': image_file.name,
                            'title': image_file.stem.replace('-', ' ').title(),
                            'category': 'Gallery'
                        })
            except Exception as e:
                logger.error(f"Error loading gallery metadata: {e}")

        return {
            'images': images,
            'gallery_url': gallery_url
        }

    def optimize_output(self, directory: Optional[str] = None) -> None:
        """Minify all HTML and CSS files in the build output.

        Uses minify-html for HTML (single-pass Rust minifier that also handles
        inline JS and CSS), and rcssmin for standalone CSS files.
        """
        target_dir = Path(directory or self.output_dir)
        html_saved = css_saved = 0
        html_count = css_count = 0

        for html_file in target_dir.rglob('*.html'):
            original = html_file.read_bytes()
            try:
                minified = minify_html.minify(
                    original.decode('utf-8'),
                    minify_js=True,
                    minify_css=True,
                    remove_processing_instructions=True,
                ).encode('utf-8')
                html_file.write_bytes(minified)
                html_saved += len(original) - len(minified)
                html_count += 1
            except BaseException:
                pass

        static_dir = target_dir / 'static'
        if static_dir.exists():
            for css_file in static_dir.rglob('*.css'):
                original = css_file.read_bytes()
                try:
                    minified = rcssmin.cssmin(original.decode('utf-8')).encode('utf-8')
                    css_file.write_bytes(minified)
                    css_saved += len(original) - len(minified)
                    css_count += 1
                except Exception:
                    pass

        total_kb = (html_saved + css_saved) / 1024
        logger.info(f"Minified {html_count} HTML + {css_count} CSS files (saved {total_kb:.1f} KB)")

