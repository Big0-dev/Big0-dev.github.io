#!/usr/bin/env python3
"""
Static Site Generator
Generates website from templates and content files based on site_config.yaml
"""

import yaml
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
import logging
import os
from datetime import datetime
from typing import Dict, Any
import markdown
from bs4 import BeautifulSoup

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class SiteGenerator:
    """Static site generator using config and templates"""
    
    def __init__(self, config_file="site_config.yaml"):
        # Load configuration
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
            
        self.output_dir = self.config['assets']['output_dir']
        self.static_dir = self.config['assets']['static_dir']
        self.templates_dir = "./templates"
        
        # Setup Jinja2
        self.env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            autoescape=select_autoescape(enabled_extensions=("html",)),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        
        # Add custom functions
        self.env.globals['inject_svg'] = self._inject_svg
        
        # Add custom filters
        self.env.filters['xmlescape'] = self._xml_escape_filter
        
    def generate(self):
        """Generate the entire website"""
        logger.info("Starting website generation...")
        
        # Clean and prepare
        self._clean_output()
        
        # Copy assets
        self._copy_assets()
        
        # Generate pages
        self._generate_static_pages()
        self._generate_gallery_pages()
        self._generate_content_pages()
        
        # Generate sitemaps
        self._generate_sitemaps()
        
        # Generate search index
        self._generate_search_index()
        
        logger.info("Website generation complete!")
        
    def _clean_output(self):
        """Clean and recreate output directory"""
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
            
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create subdirectories
        for content_type in self.config['content_types'].values():
            os.makedirs(os.path.join(self.output_dir, content_type['output_dir']), exist_ok=True)
            
        os.makedirs(os.path.join(self.output_dir, "static"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "content/gallery"), exist_ok=True)
        
    def _copy_assets(self):
        """Copy all assets according to config"""
        # Copy static assets (excluding SVGs and favicon files)
        if os.path.exists(self.static_dir):
            dest_static = os.path.join(self.output_dir, "static")
            
            for item in os.listdir(self.static_dir):
                if item.endswith('.svg') or item.startswith('favicon'):
                    continue
                    
                src = os.path.join(self.static_dir, item)
                dest = os.path.join(dest_static, item)
                
                if os.path.isfile(src):
                    shutil.copy2(src, dest)
                elif os.path.isdir(src):
                    shutil.copytree(src, dest)
                    
        # Copy gallery images
        gallery_dir = self.config['assets']['gallery_dir']
        if os.path.exists(gallery_dir):
            dest_gallery = os.path.join(self.output_dir, "content", "gallery")
            
            for item in os.listdir(gallery_dir):
                if item.endswith(('.avif', '.jpg', '.jpeg', '.png', '.webp', '.json')):
                    src = os.path.join(gallery_dir, item)
                    dest = os.path.join(dest_gallery, item)
                    shutil.copy2(src, dest)
                    
        # Copy root assets
        for asset in self.config['assets']['root_assets']:
            src = Path(asset)
            if src.exists():
                dest = Path(self.output_dir) / asset
                shutil.copy2(src, dest)
                
        # Copy favicon files to build root
        favicon_files = ['favicon.ico', 'favicon.png']
        for favicon in favicon_files:
            src = Path(self.static_dir) / favicon
            if src.exists():
                dest = Path(self.output_dir) / favicon
                shutil.copy2(src, dest)
                
    def _inject_svg(self, filename: str, wrap: bool = False, css_class: str = "") -> str:
        """Inject SVG content directly into HTML"""
        svg_path = Path(self.static_dir) / f"{filename}.svg"
        
        if not svg_path.exists():
            return f"<!-- SVG {filename} not found -->"
            
        try:
            svg_content = svg_path.read_text()
            
            if css_class:
                svg_content = svg_content.replace('<svg', f'<svg class="{css_class}"', 1)
                
            if wrap:
                return f'<span class="svg-wrapper">{svg_content}</span>'
                
            return svg_content
        except Exception as e:
            logger.error(f"Error injecting SVG {filename}: {e}")
            return f"<!-- Error loading SVG {filename} -->"
            
    def _get_base_context(self, depth: int = 0) -> Dict[str, Any]:
        """Get base context for all templates"""
        # Calculate relative path prefix based on depth
        path_prefix = '../' * depth if depth > 0 else ''
        
        context = {
            'static': f'{path_prefix}static',
            'domain': self.config['domain'],
            'copyright': datetime.now().year,
            'path_prefix': path_prefix,
            'image_sitemap': f'{path_prefix}sitemap-images.xml',
        }
        
        # Add navigation URLs with proper paths
        for key, value in self.config['navigation'].items():
            context[key] = f'{path_prefix}{value}'
        
        return context
        
    def _load_gallery_data(self) -> Dict[str, Any]:
        """Load gallery images and metadata"""
        gallery_dir = Path(self.config['assets']['gallery_dir'])
        metadata_file = gallery_dir / 'metadata.json'
        
        images = []
        gallery_url = 'content/gallery'
        
        if metadata_file.exists():
            import json
            with open(metadata_file, 'r') as f:
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
                        from datetime import datetime
                        image_data['date'] = datetime.strptime(image_data['date'], '%Y-%m-%d')
                    images.append(image_data)
                else:
                    # Add image even without metadata
                    images.append({
                        'filename': image_file.name,
                        'title': image_file.stem.replace('-', ' ').title(),
                        'category': 'Gallery'
                    })
        
        return {
            'images': images,
            'gallery_url': gallery_url
        }
        
    def _generate_static_pages(self):
        """Generate static pages from templates"""
        context = self._get_base_context()
        
        for page in self.config['static_pages']:
            try:
                template = self.env.get_template(page['template'])
                output_path = Path(self.output_dir) / page['output']
                
                # Special handling for different pages
                page_context = context.copy()
                
                if page['template'] == 'gallery.html':
                    # Skip generating the base gallery.html here, it will be handled with pagination
                    continue
                elif page['template'] == 'index.html':
                    # Load all content for homepage
                    for content_type, config in self.config['content_types'].items():
                        content_dir = Path(config['content_dir'])
                        if content_dir.exists():
                            items = []
                            for file_path in content_dir.glob('*.md'):
                                item = self._load_markdown_content(file_path)
                                items.append(item)
                            # Sort by date if available
                            items.sort(key=lambda x: x.get('date') or datetime.min, reverse=True)
                            page_context[f'all_{content_type}'] = items
                    
                    # Also load news articles
                    news_dir = Path('content/news')
                    if news_dir.exists():
                        news_articles = []
                        for file_path in news_dir.glob('*.md'):
                            article = self._load_markdown_content(file_path)
                            news_articles.append(article)
                        news_articles.sort(key=lambda x: x.get('date') or datetime.min, reverse=True)
                        page_context['news_articles'] = news_articles
                
                html_content = template.render(**page_context)
                output_path.write_text(html_content)
                
                logger.info(f"Generated: {page['output']}")
            except Exception as e:
                logger.error(f"Error generating {page['template']}: {e}")
    
    def _generate_gallery_pages(self):
        """Generate gallery pages with pagination"""
        try:
            gallery_data = self._load_gallery_data()
            images = gallery_data.get('images', [])
            gallery_url = gallery_data.get('gallery_url')
            
            # Pagination settings
            per_page = 6
            total_images = len(images)
            total_pages = (total_images + per_page - 1) // per_page if total_images > 0 else 1
            
            template = self.env.get_template('gallery.html')
            
            for page_num in range(1, total_pages + 1):
                # Get images for this page
                start_idx = (page_num - 1) * per_page
                end_idx = start_idx + per_page
                page_images = images[start_idx:end_idx]
                
                # Determine output path
                if page_num == 1:
                    output_path = Path(self.output_dir) / 'gallery.html'
                else:
                    output_path = Path(self.output_dir) / f'gallery-{page_num}.html'
                
                # Create context
                context = self._get_base_context()
                context.update({
                    'images': page_images,
                    'gallery_url': gallery_url,
                    'page_num': page_num,
                    'total_pages': total_pages,
                    'per_page': per_page,
                })
                
                html_content = template.render(**context)
                output_path.write_text(html_content)
                
                logger.info(f"Generated: gallery{'' if page_num == 1 else f'-{page_num}'}.html")
                
        except Exception as e:
            logger.error(f"Error generating gallery pages: {e}")
                
    def _parse_date(self, date_value):
        """Parse date from various formats"""
        if not date_value:
            return None
            
        # If already a datetime object
        if isinstance(date_value, datetime):
            return date_value
            
        date_str = str(date_value)
        
        # Try different date formats
        date_formats = [
            '%Y-%m-%d',          # 2024-01-15
            '%B %d, %Y',         # January 15, 2024
            '%b %d, %Y',         # Jan 15, 2024
            '%d %B %Y',          # 15 January 2024
            '%d %b %Y',          # 15 Jan 2024
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
                
        # If no format matches, return None
        logger.warning(f"Could not parse date: {date_str}")
        return None
    
    def _process_template_directives(self, content: str) -> str:
        """Process template directives like {{template:cta}} in markdown content"""
        import re
        
        # Define template replacements
        templates = {
            'cta': '''
<div class="inline-cta">
  <h3>Ready to Transform Your Business?</h3>
  <p>Let's discuss how we can help you achieve your goals with our innovative solutions.</p>
  <a href="../contact.html" class="btn btn-primary">Get Started Today</a>
</div>
''',
            'cta-service': '''
<div class="inline-cta">
  <h3>Ready to Get Started?</h3>
  <p>Our experts are ready to help you implement these solutions for your business.</p>
  <a href="../contact.html" class="btn btn-primary">Schedule a Consultation</a>
</div>
''',
            'cta-case-study': '''
<div class="inline-cta">
  <h3>Want Similar Results?</h3>
  <p>Let's discuss how we can deliver transformative solutions for your organization.</p>
  <a href="../contact.html" class="btn btn-primary">Contact Our Team</a>
</div>
'''
        }
        
        # Find and replace all template directives
        def replace_template(match):
            template_name = match.group(1)
            return templates.get(template_name, match.group(0))
        
        # Process {{template:name}} directives (updated to handle hyphens in template names)
        content = re.sub(r'\{\{template:([\w-]+)\}\}', replace_template, content)
        
        # Process {{related-services:service1,service2,service3}} directives
        def replace_related_services(match):
            services = [s.strip() for s in match.group(1).split(',')]
            html = '<div class="related-services-inline">\n<h3>Related Services</h3>\n<div class="related-services-grid">\n'
            for service in services:
                html += f'  <a href="../services/{service}.html" class="related-service-link">\n'
                html += f'    <span class="link-icon">→</span>\n'
                html += f'    <span>{service.replace("-", " ").replace("_", " ").title()}</span>\n'
                html += f'  </a>\n'
            html += '</div>\n</div>'
            return html
        
        content = re.sub(r'\{\{related-services:([^}]+)\}\}', replace_related_services, content)
        
        # Process {{related-industries:industry1,industry2}} directives
        def replace_related_industries(match):
            industries = [i.strip() for i in match.group(1).split(',')]
            html = '<div class="related-industries-inline">\n<h3>Industries We Serve</h3>\n<div class="related-industries-grid">\n'
            for industry in industries:
                html += f'  <a href="../industries/{industry}.html" class="related-industry-link">\n'
                html += f'    <span class="link-icon">→</span>\n'
                html += f'    <span>{industry.replace("-", " ").title()}</span>\n'
                html += f'  </a>\n'
            html += '</div>\n</div>'
            return html
        
        content = re.sub(r'\{\{related-industries:([^}]+)\}\}', replace_related_industries, content)
        
        # Process {{industry-challenges:challenge1,challenge2}} directives
        def replace_industry_challenges(match):
            challenges = [c.strip() for c in match.group(1).split('|')]
            html = '<div class="industry-challenges">\n<h3>Key Challenges We Address</h3>\n<div class="challenges-grid">\n'
            for challenge in challenges:
                html += f'  <div class="challenge-item">\n'
                html += f'    <svg class="challenge-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n'
                html += f'      <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>\n'
                html += f'    </svg>\n'
                html += f'    <p>{challenge}</p>\n'
                html += f'  </div>\n'
            html += '</div>\n</div>'
            return html
        
        content = re.sub(r'\{\{industry-challenges:([^}]+)\}\}', replace_industry_challenges, content)
        
        # Process {{industry-solutions:solution1|description1,solution2|description2}} directives
        def replace_industry_solutions(match):
            solutions = [s.strip() for s in match.group(1).split(',')]
            html = '<div class="industry-solutions">\n<h3>Our Solutions</h3>\n<div class="solutions-grid">\n'
            for solution in solutions:
                if '|' in solution:
                    title, desc = solution.split('|', 1)
                else:
                    title, desc = solution, ''
                html += f'  <div class="solution-card">\n'
                html += f'    <h4>{title.strip()}</h4>\n'
                if desc:
                    html += f'    <p>{desc.strip()}</p>\n'
                html += f'  </div>\n'
            html += '</div>\n</div>'
            return html
        
        content = re.sub(r'\{\{industry-solutions:([^}]+)\}\}', replace_industry_solutions, content)
        
        return content
    
    def _process_template_directives_in_html(self, html_content: str) -> str:
        """Process template directives that may be wrapped in HTML tags"""
        import re
        
        # First process any directives that are already in the markdown
        html_content = self._process_template_directives(html_content)
        
        # Also handle directives that got wrapped in <p> tags
        # Replace <p>{{template:xxx}}</p> patterns
        def replace_p_wrapped_template(match):
            directive = match.group(1)
            templates = {
                'cta': '''<div class="inline-cta">
  <h3>Ready to Transform Your Business?</h3>
  <p>Let's discuss how we can help you achieve your goals with our innovative solutions.</p>
  <a href="../contact.html" class="btn btn-primary">Get Started Today</a>
</div>''',
                'cta-service': '''<div class="inline-cta">
  <h3>Ready to Get Started?</h3>
  <p>Our experts are ready to help you implement these solutions for your business.</p>
  <a href="../contact.html" class="btn btn-primary">Schedule a Consultation</a>
</div>''',
                'cta-case-study': '''<div class="inline-cta">
  <h3>Want Similar Results?</h3>
  <p>Let's discuss how we can deliver transformative solutions for your organization.</p>
  <a href="../contact.html" class="btn btn-primary">Contact Our Team</a>
</div>'''
            }
            return templates.get(directive, match.group(0))
        
        html_content = re.sub(r'<p>\{\{template:([\w-]+)\}\}</p>', replace_p_wrapped_template, html_content)
        
        return html_content
    
    def _load_markdown_content(self, file_path: Path) -> Dict[str, Any]:
        """Load and parse markdown content"""
        content = file_path.read_text()
        
        # Extract frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = yaml.safe_load(parts[1])
                markdown_content = parts[2].strip()
            else:
                frontmatter = {}
                markdown_content = content
        else:
            # Check if this is a blog file with the special format
            lines = content.strip().split('\n')
            if len(lines) >= 5 and 'blogs' in str(file_path):
                # Parse blog format: title, category, date, image, description
                frontmatter = {
                    'title': lines[0],
                    'category': lines[1],
                    'date': lines[2],
                    'image_url': lines[3] if lines[3] else '',
                    'meta_description': lines[4]
                }
                markdown_content = '\n'.join(lines[5:]).strip()
            else:
                frontmatter = {}
                markdown_content = content
            
        # Process template directives before converting to HTML
        markdown_content = self._process_template_directives(markdown_content)
        
        # Convert markdown to HTML
        md = markdown.Markdown(extensions=['extra', 'codehilite', 'toc'])
        html_content = md.convert(markdown_content)
        
        # Also process any remaining directives that might have been wrapped in HTML tags
        html_content = self._process_template_directives_in_html(html_content)
        
        # Extract first paragraph as excerpt
        soup = BeautifulSoup(html_content, 'html.parser')
        first_p = soup.find('p')
        excerpt = first_p.text if first_p else ""
        
        # Parse features if they exist
        features = frontmatter.get('features', '')
        if isinstance(features, str):
            features = [f.strip() for f in features.split(',') if f.strip()]
        
        # Create short description from description or excerpt
        short_description = frontmatter.get('description', '')
        if not short_description and excerpt:
            short_description = excerpt[:160] + '...' if len(excerpt) > 160 else excerpt
        
        return {
            'slug': file_path.stem,
            'title': frontmatter.get('title', 'Untitled'),
            'meta_description': frontmatter.get('meta_description', excerpt[:160]),
            'short_description': short_description,
            'content_html': html_content,
            'frontmatter': frontmatter,
            'icon': frontmatter.get('icon', ''),
            'price': frontmatter.get('price', ''),
            'features': features,
            'excerpt': frontmatter.get('description', excerpt[:200] + '...' if len(excerpt) > 200 else excerpt),
            'category': frontmatter.get('category', 'General'),
            'date': self._parse_date(frontmatter.get('date')),
            'tags': frontmatter.get('tags', '').split(',') if frontmatter.get('tags') else [],
            'external_link': frontmatter.get('external_link', ''),
        }
        
    def _generate_content_pages(self):
        """Generate pages from content files"""
        context = self._get_base_context()
        
        for content_type, config in self.config['content_types'].items():
            content_dir = Path(config['content_dir'])
            if not content_dir.exists():
                continue
                
            # Load all content
            items = []
            for file_path in content_dir.glob('*.md'):
                item = self._load_markdown_content(file_path)
                items.append(item)
                
                # Generate detail page
                if 'template' in config:
                    try:
                        template = self.env.get_template(config['template'])
                        output_path = Path(self.output_dir) / config['output_dir'] / f"{item['slug']}.html"
                        
                        # Get context with depth 1 for subdirectory pages
                        # Map content_type to singular form
                        singular_map = {
                            'services': 'service',
                            'industries': 'industry', 
                            'blog': 'blog',
                            'case_studies': 'case_studie'
                        }
                        singular = singular_map.get(content_type, content_type[:-1])
                        # Get base context
                        base_context = self._get_base_context(depth=1)
                        
                        # Create item context, ensuring navigation URLs are preserved
                        item_context = {
                            **base_context,
                            'item': item, 
                            f'current_{singular}': item
                        }
                        
                        # Add related items for news
                        if content_type == 'news':
                            # Get other news items excluding current
                            related_news = [n for n in items if n['slug'] != item['slug']]
                            # Sort by date and take first 3
                            related_news.sort(key=lambda x: x.get('date') or datetime.min, reverse=True)
                            item_context['related_news'] = related_news[:3]
                        
                        html_content = template.render(**item_context)
                        output_path.write_text(html_content)
                        
                        logger.info(f"Generated: {content_type}/{item['slug']}.html")
                    except Exception as e:
                        logger.error(f"Error generating {content_type} detail: {e}")
                        
            # Generate listing pages
            if 'listing_template' in config and items:
                try:
                    template = self.env.get_template(config['listing_template'])
                    per_page = config.get('per_page', len(items))
                    
                    # Paginate if needed
                    for page_num, i in enumerate(range(0, len(items), per_page), 1):
                        page_items = items[i:i + per_page]
                        total_pages = (len(items) + per_page - 1) // per_page
                        
                        output_name = f"{content_type.replace('_', '-')}.html" if page_num == 1 else f"{content_type.replace('_', '-')}-{page_num}.html"
                        output_path = Path(self.output_dir) / output_name
                        
                        # Get base context first
                        base_context = self._get_base_context()
                        
                        list_context = {
                            **base_context,
                            'items': page_items,
                            f'all_{content_type}': page_items,  # Use all_ prefix to avoid conflicts
                            'page_num': page_num,
                            'total_pages': total_pages,
                            'per_page': per_page,
                        }
                        
                        # Special handling for news template
                        if content_type == 'news':
                            list_context['news_articles'] = page_items
                        
                        html_content = template.render(**list_context)
                        output_path.write_text(html_content)
                        
                        logger.info(f"Generated: {output_name}")
                except Exception as e:
                    logger.error(f"Error generating {content_type} listing: {e}")
                    
    def _generate_sitemaps(self):
        """Generate XML sitemaps"""
        # Simple sitemap generation
        sitemap_path = Path(self.output_dir) / "sitemap.xml"
        
        urls = []
        
        # Add static pages
        for page in self.config['static_pages']:
            urls.append(f"{self.config['domain']}/{page['output']}")
            
        # Add content pages
        for content_type, config in self.config['content_types'].items():
            content_dir = Path(config['content_dir'])
            if content_dir.exists():
                for file_path in content_dir.glob('*.md'):
                    slug = file_path.stem
                    urls.append(f"{self.config['domain']}/{config['output_dir']}/{slug}.html")
                    
        # Generate sitemap XML
        sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        sitemap_xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        
        for url in urls:
            sitemap_xml += f'  <url>\n    <loc>{url}</loc>\n  </url>\n'
            
        sitemap_xml += '</urlset>'
        
        sitemap_path.write_text(sitemap_xml)
        logger.info("Generated sitemap.xml")
        
        # Generate image sitemap
        self._generate_image_sitemap()
        
        # Generate RSS feed
        self._generate_rss_feed()
    
    def _generate_image_sitemap(self):
        """Generate image sitemap"""
        image_sitemap_path = Path(self.output_dir) / "sitemap-images.xml"
        
        # Get gallery images
        gallery_data = self._load_gallery_data()
        images = gallery_data.get('images', [])
        
        # Generate image sitemap XML
        sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        sitemap_xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        sitemap_xml += '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
        
        # Add gallery page with all images
        if images:
            sitemap_xml += '  <url>\n'
            sitemap_xml += f'    <loc>{self.config["domain"]}/gallery.html</loc>\n'
            
            for image in images:
                sitemap_xml += '    <image:image>\n'
                sitemap_xml += f'      <image:loc>{self.config["domain"]}/content/gallery/{image["filename"]}</image:loc>\n'
                if 'title' in image:
                    # Escape XML special characters
                    title = image["title"].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')
                    sitemap_xml += f'      <image:title>{title}</image:title>\n'
                if 'description' in image:
                    # Escape XML special characters
                    description = image["description"].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')
                    sitemap_xml += f'      <image:caption>{description}</image:caption>\n'
                sitemap_xml += '    </image:image>\n'
            
            sitemap_xml += '  </url>\n'
        
        sitemap_xml += '</urlset>'
        
        image_sitemap_path.write_text(sitemap_xml)
        logger.info("Generated sitemap-images.xml")
    
    def _escape_xml(self, text):
        """Escape special characters for XML"""
        if not text:
            return text
        # Even in CDATA, we need to handle the CDATA end sequence
        return text.replace(']]>', ']]]]><![CDATA[>')
    
    def _xml_escape_filter(self, text):
        """Escape special characters for XML (for use as Jinja2 filter)"""
        if not text:
            return text
        # Replace XML special characters
        text = str(text)
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&apos;')
        return text
    
    def _generate_rss_feed(self):
        """Generate RSS feed for news and blog posts"""
        try:
            from email.utils import formatdate
            import time
            
            # Collect all feed items
            feed_items = []
            
            # Add news articles
            news_dir = Path('content/news')
            if news_dir.exists():
                for file_path in news_dir.glob('*.md'):
                    item = self._load_markdown_content(file_path)
                    feed_items.append({
                        'title': item['title'],
                        'url': f"news/{item['slug']}.html",
                        'description': item['frontmatter'].get('description', item.get('excerpt', '')),
                        'content_html': self._escape_xml(item.get('content_html', '')),
                        'pub_date': formatdate(time.mktime(item['date'].timetuple()) if item.get('date') else time.time()),
                        'category': item['frontmatter'].get('category', 'News'),
                        'tags': item['frontmatter'].get('tags', '').split(',') if item['frontmatter'].get('tags') else [],
                        'date_obj': item.get('date', datetime.now())
                    })
            
            # Add blog posts
            blog_dir = Path('content/blogs')
            if blog_dir.exists():
                for file_path in blog_dir.glob('*.md'):
                    item = self._load_markdown_content(file_path)
                    feed_items.append({
                        'title': item['title'],
                        'url': f"blog/{item['slug']}.html",
                        'description': item['frontmatter'].get('description', item.get('excerpt', '')),
                        'content_html': self._escape_xml(item.get('content_html', '')),
                        'pub_date': formatdate(time.mktime(item['date'].timetuple()) if item.get('date') else time.time()),
                        'category': item['frontmatter'].get('category', 'Blog'),
                        'tags': item['frontmatter'].get('tags', '').split(',') if item['frontmatter'].get('tags') else [],
                        'date_obj': item.get('date', datetime.now())
                    })
            
            # Add case studies
            case_studies_dir = Path('content/case_studies')
            if case_studies_dir.exists():
                for file_path in case_studies_dir.glob('*.md'):
                    item = self._load_markdown_content(file_path)
                    feed_items.append({
                        'title': item['title'],
                        'url': f"case-studies/{item['slug']}.html",
                        'description': item['frontmatter'].get('description', item.get('excerpt', '')),
                        'content_html': self._escape_xml(item.get('content_html', '')),
                        'pub_date': formatdate(time.mktime(item['date'].timetuple()) if item.get('date') else time.time()),
                        'category': 'Case Study',
                        'tags': item['frontmatter'].get('tags', '').split(',') if item['frontmatter'].get('tags') else [],
                        'date_obj': item.get('date', datetime.now())
                    })
            
            # Sort by date (newest first)
            feed_items.sort(key=lambda x: x['date_obj'] or datetime.min, reverse=True)
            
            # Remove date_obj from items
            for item in feed_items:
                del item['date_obj']
            
            # Generate RSS
            template = self.env.get_template('rss.xml')
            rss_content = template.render(
                domain=self.config['domain'],
                build_date=formatdate(time.time()),
                current_year=datetime.now().year,
                feed_items=feed_items[:20]  # Limit to 20 most recent items
            )
            
            rss_path = Path(self.output_dir) / "rss.xml"
            rss_path.write_text(rss_content)
            logger.info("Generated rss.xml")
            
        except Exception as e:
            logger.error(f"Error generating RSS feed: {e}")
    
    def _generate_search_index(self):
        """Generate search index for all pages"""
        try:
            import json
            
            search_documents = []
            doc_id = 1
            
            # Index static pages
            for page in self.config['static_pages']:
                # Skip sitemap pages
                if page['output'].endswith('.xml'):
                    continue
                    
                doc = {
                    'id': doc_id,
                    'url': page['output'],
                    'title': page.get('title', page['output'].replace('.html', '').title()),
                    'content': '',  # Could extract content from template if needed
                    'description': page.get('description', ''),
                    'type': 'page'
                }
                search_documents.append(doc)
                doc_id += 1
            
            # Index all content pages
            for content_type, config in self.config['content_types'].items():
                content_dir = Path(config['content_dir'])
                if not content_dir.exists():
                    continue
                    
                # Add listing page
                if 'listing_template' in config:
                    doc = {
                        'id': doc_id,
                        'url': f"{content_type.replace('_', '-')}.html",
                        'title': content_type.replace('_', ' ').title(),
                        'content': '',
                        'description': f"Browse all {content_type.replace('_', ' ')}",
                        'type': 'listing'
                    }
                    search_documents.append(doc)
                    doc_id += 1
                
                # Add individual content pages
                for file_path in content_dir.glob('*.md'):
                    item = self._load_markdown_content(file_path)
                    
                    # Clean content for search - remove HTML tags
                    clean_content = ''
                    if item.get('content_html'):
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(item['content_html'], 'html.parser')
                        clean_content = soup.get_text(' ', strip=True)
                    
                    # Fix type for news articles and industries
                    doc_type = content_type.rstrip('s')  # Remove plural
                    if content_type == 'news':
                        doc_type = 'news'  # Keep 'news' as is, don't change to 'new'
                    elif content_type == 'industries':
                        doc_type = 'industry'  # Change 'industries' to 'industry', not 'industrie'
                    
                    doc = {
                        'id': doc_id,
                        'url': f"{config['output_dir']}/{item['slug']}.html",
                        'title': item['title'],
                        'content': clean_content[:1000],  # Limit content length
                        'description': item.get('short_description', item.get('excerpt', '')),
                        'type': doc_type,
                        'category': item.get('category', ''),
                        'date': item['date'].strftime('%Y-%m-%d') if item.get('date') else ''
                    }
                    search_documents.append(doc)
                    doc_id += 1
            
            # Add gallery page if it exists
            gallery_doc = {
                'id': doc_id,
                'url': 'gallery.html',
                'title': 'Gallery',
                'content': 'Photo gallery showcasing our events, team, and projects',
                'description': 'Browse through our collection of photos from events, team activities, and project showcases',
                'type': 'page'
            }
            search_documents.append(gallery_doc)
            
            # Write search index
            search_index_path = Path(self.output_dir) / 'static' / 'search-index.json'
            search_index_path.write_text(json.dumps(search_documents, indent=2))
            
            logger.info(f"Generated search index with {len(search_documents)} documents")
            
        except Exception as e:
            logger.error(f"Error generating search index: {e}")


def main():
    """Main entry point"""
    generator = SiteGenerator()
    generator.generate()


if __name__ == "__main__":
    main()