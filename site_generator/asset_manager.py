"""
Asset Manager Module for Big0 Site Generator

Handles all asset operations including:
- Static file copying
- SVG injection with caching
- Gallery image handling
- File optimization and minification
"""

import os
import shutil
import json
import re
import logging
from pathlib import Path
from datetime import datetime
from functools import lru_cache
from typing import Dict, Any, List, Optional

# Minification imports
from bs4 import BeautifulSoup
import minify_html
import rcssmin
import jsmin

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

    def copy_static_assets(self, source: Optional[str] = None, destination: Optional[str] = None) -> None:
        """
        Copy static assets excluding SVGs and favicon files

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

        for item in os.listdir(source_dir):
            # Skip SVG files and favicon files (handled separately)
            if item.endswith('.svg') or item.startswith('favicon'):
                continue

            src_path = os.path.join(source_dir, item)
            dest_path = os.path.join(dest_dir, item)

            try:
                if os.path.isfile(src_path):
                    shutil.copy2(src_path, dest_path)
                    logger.debug(f"Copied file: {item}")
                elif os.path.isdir(src_path):
                    if os.path.exists(dest_path):
                        shutil.rmtree(dest_path)
                    shutil.copytree(src_path, dest_path)
                    logger.debug(f"Copied directory: {item}")
            except Exception as e:
                logger.error(f"Error copying {item}: {e}")

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

    def optimize_html(self, html: str) -> str:
        """
        Optimize HTML content

        Args:
            html: HTML content to optimize

        Returns:
            Minified HTML content
        """
        try:
            # Extract and minify inline scripts and styles
            soup = BeautifulSoup(html, 'html.parser')

            # Minify inline JavaScript
            for script in soup.find_all('script'):
                if script.string and not script.get('src'):
                    try:
                        minified_js = jsmin.jsmin(script.string)
                        script.string = minified_js
                    except Exception as e:
                        logger.warning(f"Failed to minify inline JS: {e}")

            # Minify inline CSS
            for style in soup.find_all('style'):
                if style.string:
                    try:
                        minified_css = rcssmin.cssmin(style.string)
                        style.string = minified_css
                    except Exception as e:
                        logger.warning(f"Failed to minify inline CSS: {e}")

            # Convert back to string
            modified_html = str(soup)

            # Minify the entire HTML
            try:
                # Use conservative settings to preserve cookie consent functionality
                minified_html = minify_html.minify(
                    modified_html,
                    minify_js=False,
                    minify_css=False,
                    remove_processing_instructions=False,
                    keep_html_and_head_opening_tags=True,
                    keep_closing_tags=True,
                    minify_doctype=False
                )
                return minified_html
            except Exception:
                # If minify_html fails, use simple regex-based approach
                return self._simple_html_minify(modified_html)

        except Exception as e:
            logger.error(f"Error optimizing HTML: {e}")
            return html

    def optimize_css(self, css: str) -> str:
        """
        Optimize CSS content

        Args:
            css: CSS content to optimize

        Returns:
            Minified CSS content
        """
        try:
            return rcssmin.cssmin(css, keep_bang_comments=True)
        except Exception as e:
            logger.error(f"Error optimizing CSS: {e}")
            return css

    def optimize_js(self, js: str) -> str:
        """
        Optimize JavaScript content

        Args:
            js: JavaScript content to optimize

        Returns:
            Minified JavaScript content
        """
        try:
            return jsmin.jsmin(js)
        except Exception as e:
            logger.error(f"Error optimizing JS: {e}")
            return js

    def optimize_all_files(self, directory: Optional[str] = None) -> Dict[str, Any]:
        """
        Optimize all files in the specified directory

        Args:
            directory: Directory to optimize (defaults to output_dir)

        Returns:
            Dictionary with optimization statistics
        """
        target_dir = directory or self.output_dir
        logger.info("Starting post-generation optimization...")

        # Track optimization stats
        stats = {
            'html_files': 0,
            'html_saved': 0,
            'css_files': 0,
            'css_saved': 0,
            'total_saved': 0
        }

        # Optimize HTML files
        self._optimize_html_files(target_dir, stats)

        # Optimize CSS files
        self._optimize_css_files(target_dir, stats)

        # Log optimization results
        total_saved_kb = stats['total_saved'] / 1024
        logger.info(f"Optimization complete! Saved {total_saved_kb:.2f} KB total")
        logger.info(f"  - HTML: {stats['html_files']} files, saved {stats['html_saved']/1024:.2f} KB")
        logger.info(f"  - CSS: {stats['css_files']} files, saved {stats['css_saved']/1024:.2f} KB")

        return stats

    def _optimize_html_files(self, directory: str, stats: Dict[str, Any]) -> None:
        """Minify all HTML files in the specified directory"""
        output_path = Path(directory)

        for html_file in output_path.rglob('*.html'):
            try:
                # Read original content
                original_content = html_file.read_text(encoding='utf-8')
                original_size = len(original_content.encode('utf-8'))

                # Optimize HTML
                minified_html = self.optimize_html(original_content)

                # Write optimized content
                html_file.write_text(minified_html, encoding='utf-8')

                # Calculate savings
                minified_size = len(minified_html.encode('utf-8'))
                saved = original_size - minified_size

                stats['html_files'] += 1
                stats['html_saved'] += saved
                stats['total_saved'] += saved

                if saved > 0:
                    percent_saved = (saved / original_size) * 100
                    logger.debug(f"Minified {html_file.relative_to(output_path)}: {percent_saved:.1f}% smaller")

            except Exception as e:
                logger.error(f"Error optimizing {html_file}: {e}")

    def _optimize_css_files(self, directory: str, stats: Dict[str, Any]) -> None:
        """Minify all CSS files in the static directory"""
        static_dir = Path(directory) / 'static'

        if not static_dir.exists():
            return

        for css_file in static_dir.rglob('*.css'):
            try:
                # Read original content
                original_content = css_file.read_text(encoding='utf-8')
                original_size = len(original_content.encode('utf-8'))

                # Optimize CSS
                minified_css = self.optimize_css(original_content)

                # Write optimized content
                css_file.write_text(minified_css, encoding='utf-8')

                # Calculate savings
                minified_size = len(minified_css.encode('utf-8'))
                saved = original_size - minified_size

                stats['css_files'] += 1
                stats['css_saved'] += saved
                stats['total_saved'] += saved

                if saved > 0:
                    percent_saved = (saved / original_size) * 100
                    logger.debug(f"Minified {css_file.relative_to(static_dir)}: {percent_saved:.1f}% smaller")

            except Exception as e:
                logger.error(f"Error optimizing {css_file}: {e}")

    def _simple_html_minify(self, html: str) -> str:
        """
        Simple regex-based HTML minification fallback

        Args:
            html: HTML content to minify

        Returns:
            Minified HTML content
        """
        # Remove HTML comments (but keep IE conditional comments)
        html = re.sub(r'<!--(?!\[if).*?-->', '', html, flags=re.DOTALL)

        # Remove whitespace between tags
        html = re.sub(r'>\s+<', '><', html)

        # Remove leading/trailing whitespace
        html = html.strip()

        # Collapse multiple spaces to single space
        html = re.sub(r'\s+', ' ', html)

        return html