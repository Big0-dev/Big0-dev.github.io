"""
AI Content Engine - Uses DeepSeek via OpenRouter for content optimization
"""

import json
import urllib.request
import urllib.error
from typing import Optional
from dataclasses import dataclass

from ..config import Config, FUNNEL_STAGES
from ..models import (
    PageData, KeywordData, FunnelStage, Priority,
    ContentRecommendation, DesignRecommendation
)
from ..analyzers.content_analyzer import ContentFile
from ..analyzers.opportunity_analyzer import SEOOpportunity


@dataclass
class AIResponse:
    """Response from AI model"""
    content: str
    tokens_used: int
    model: str
    success: bool
    error: Optional[str] = None


class AIContentEngine:
    """
    Uses DeepSeek via OpenRouter to generate SEO-optimized content.

    Cost-effective alternative to GPT-4/Claude for bulk content tasks.
    DeepSeek V3 offers excellent performance at ~$0.27/1M input tokens.
    """

    def __init__(self, config: Config):
        self.config = config
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = config.ai_model  # Default: deepseek/deepseek-chat

    def _call_api(self, messages: list[dict], max_tokens: int = 1000) -> AIResponse:
        """Make API call to OpenRouter"""
        if not self.config.openrouter_api_key:
            return AIResponse(
                content="",
                tokens_used=0,
                model=self.model,
                success=False,
                error="OpenRouter API key not configured"
            )

        headers = {
            "Authorization": f"Bearer {self.config.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.config.site_domain,
            "X-Title": "Big0 SEO Engine"
        }

        payload = json.dumps({
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7,
        }).encode()

        try:
            req = urllib.request.Request(self.api_url, data=payload, headers=headers)
            with urllib.request.urlopen(req, timeout=60) as response:
                data = json.loads(response.read().decode())

            content = data['choices'][0]['message']['content']
            tokens = data.get('usage', {}).get('total_tokens', 0)

            return AIResponse(
                content=content,
                tokens_used=tokens,
                model=self.model,
                success=True
            )

        except urllib.error.HTTPError as e:
            error_body = e.read().decode() if e.fp else str(e)
            return AIResponse(
                content="",
                tokens_used=0,
                model=self.model,
                success=False,
                error=f"HTTP {e.code}: {error_body}"
            )
        except Exception as e:
            return AIResponse(
                content="",
                tokens_used=0,
                model=self.model,
                success=False,
                error=str(e)
            )

    def generate_meta_title(
        self,
        page: ContentFile,
        target_keywords: list[str],
        funnel_stage: FunnelStage
    ) -> ContentRecommendation:
        """Generate optimized meta title"""

        stage_guidance = {
            FunnelStage.TOFU: "Use 'how to', 'guide', 'what is' format. Educational and informative.",
            FunnelStage.MOFU: "Highlight solutions and benefits. Use 'best', 'top', specific outcomes.",
            FunnelStage.BOFU: "Include location if relevant. Add urgency. Mention services directly.",
        }

        messages = [
            {
                "role": "system",
                "content": """Assume the role of a senior SEO specialist with 10+ years of experience optimizing B2B tech companies for search engines.

Take a deep breath and think step-by-step before responding.

Your expertise:
- You understand Google's ranking algorithms deeply
- You know how to craft titles that drive clicks
- You balance keyword optimization with user intent

Generate meta titles that are:
- EXACTLY 50-60 characters (this is critical for SERP display)
- Include primary keyword near the beginning
- Have a clear value proposition
- Use power words when appropriate
- Match search intent for the funnel stage

Respond with ONLY the meta title, nothing else. No quotes, no explanation."""
            },
            {
                "role": "user",
                "content": f"""Generate an optimized meta title for this page:

Current title: {page.title}
Current meta: {page.meta_description[:150] if page.meta_description else 'None'}
Page type: {page.content_type.value}
Funnel stage: {funnel_stage.value} - {stage_guidance[funnel_stage]}
Target keywords: {', '.join(target_keywords[:3])}
Company: Big0 (AI & Software Development)

Generate the best meta title:"""
            }
        ]

        response = self._call_api(messages, max_tokens=100)

        return ContentRecommendation(
            page_url=page.url,
            recommendation_type="meta_title",
            current_value=page.title,
            recommended_value=response.content.strip().strip('"'),
            target_keywords=target_keywords,
            reasoning=f"Optimized for {funnel_stage.value} stage with primary keyword placement",
            priority=Priority.HIGH,
            estimated_impact="high",
            funnel_stage=funnel_stage,
        )

    def generate_meta_description(
        self,
        page: ContentFile,
        target_keywords: list[str],
        funnel_stage: FunnelStage
    ) -> ContentRecommendation:
        """Generate optimized meta description"""

        stage_cta = {
            FunnelStage.TOFU: "Learn more, discover, explore",
            FunnelStage.MOFU: "See how, compare, find out",
            FunnelStage.BOFU: "Get started, contact us, free consultation",
        }

        messages = [
            {
                "role": "system",
                "content": """Assume the role of a conversion-focused SEO copywriter for enterprise B2B tech companies.

Take a deep breath and think step-by-step before responding.

Before writing, consider:
1. What is the searcher's intent at this funnel stage?
2. What benefit will make them click?
3. What call-to-action matches their readiness?

Generate meta descriptions that:
- Are EXACTLY 150-160 characters (critical for SERP display)
- Include the primary keyword naturally in the first half
- Have a compelling call-to-action
- Promise specific value/benefit
- Create urgency when appropriate

Respond with ONLY the meta description, nothing else. No quotes, no explanation."""
            },
            {
                "role": "user",
                "content": f"""Generate an optimized meta description:

Current title: {page.title}
Current meta: {page.meta_description if page.meta_description else 'None'}
Page type: {page.content_type.value}
Funnel stage: {funnel_stage.value}
Suggested CTA style: {stage_cta[funnel_stage]}
Target keywords: {', '.join(target_keywords[:3])}
Company: Big0 - AI & Software Development

Generate the meta description:"""
            }
        ]

        response = self._call_api(messages, max_tokens=100)

        return ContentRecommendation(
            page_url=page.url,
            recommendation_type="meta_description",
            current_value=page.meta_description,
            recommended_value=response.content.strip().strip('"'),
            target_keywords=target_keywords,
            reasoning=f"Optimized with {stage_cta[funnel_stage]} CTA style",
            priority=Priority.HIGH,
            estimated_impact="high",
            funnel_stage=funnel_stage,
        )

    def generate_content_improvements(
        self,
        page: ContentFile,
        opportunities: list[SEOOpportunity],
        target_keywords: list[str]
    ) -> ContentRecommendation:
        """Generate content improvement suggestions"""

        opportunity_context = "\n".join([
            f"- {opp.recommended_action}"
            for opp in opportunities[:3]
        ])

        messages = [
            {
                "role": "system",
                "content": """Assume the role of a senior content strategist who has helped 50+ B2B tech companies improve their organic traffic.

Take a deep breath and work through this systematically.

Before suggesting improvements, analyze:
1. What keywords are missing from the current content?
2. Where are the gaps in topical coverage?
3. What would make this content more authoritative?
4. How can we improve the user experience?

Provide specific, actionable content improvements that:
- Incorporate target keywords naturally without stuffing
- Add missing topical depth that competitors cover
- Improve readability with better structure
- Support both user engagement and SEO goals

Format your response as a numbered list of 3-5 specific improvements.
Each must be actionable and specific to this page. Be concrete, not generic."""
            },
            {
                "role": "user",
                "content": f"""Suggest content improvements for this page:

Title: {page.title}
Type: {page.content_type.value}
Funnel Stage: {page.funnel_stage.value}
Word Count: {page.word_count}
Has FAQ: {page.has_faq}
Has CTA: {page.has_cta}

Target Keywords: {', '.join(target_keywords[:5])}

Current opportunities identified:
{opportunity_context}

Content excerpt (first 500 chars):
{page.body_content[:500]}

Provide specific content improvements:"""
            }
        ]

        response = self._call_api(messages, max_tokens=500)

        return ContentRecommendation(
            page_url=page.url,
            recommendation_type="content",
            current_value=f"{page.word_count} words",
            recommended_value=response.content.strip(),
            target_keywords=target_keywords,
            reasoning="Based on keyword gaps and content analysis",
            priority=Priority.MEDIUM,
            estimated_impact="medium",
            funnel_stage=page.funnel_stage,
        )

    def generate_design_recommendations(
        self,
        page: PageData,
        clarity_issues: list[dict] = None
    ) -> list[DesignRecommendation]:
        """Generate design/UX recommendations based on analytics"""

        recommendations = []
        issues_context = ""

        if clarity_issues:
            issues_context = "\n".join([
                f"- {issue.get('description', '')}"
                for issue in clarity_issues[:5]
            ])

        messages = [
            {
                "role": "system",
                "content": """Assume the role of a UX/CRO specialist with expertise in B2B website optimization and conversion rate improvement.

Take a deep breath and analyze the metrics carefully before responding.

When you see:
- High bounce rate → Consider above-fold content and value proposition clarity
- Low scroll depth → Consider content structure and visual engagement
- Rage clicks → Identify frustration points and broken interactions
- Dead clicks → Find elements that look clickable but aren't

Recommend specific design changes to:
- Improve engagement and reduce bounce rate
- Increase conversion rates
- Fix usability issues
- Optimize the user journey

Respond in JSON format with an array of 2-4 recommendations:
[{
  "element": "cta|hero|form|navigation|content_block",
  "action": "add|remove|modify|reposition",
  "description": "specific change",
  "reasoning": "why this helps based on the data"
}]"""
            },
            {
                "role": "user",
                "content": f"""Recommend design changes for this page:

URL: {page.url}
Bounce Rate: {page.bounce_rate*100:.1f}%
Avg Time on Page: {page.avg_time_on_page:.0f}s
Scroll Depth: {page.scroll_depth*100:.0f}%
Rage Clicks: {page.rage_clicks}
Dead Clicks: {page.dead_clicks}

Issues identified:
{issues_context if issues_context else 'No specific issues logged'}

Provide 2-4 design recommendations as JSON:"""
            }
        ]

        response = self._call_api(messages, max_tokens=500)

        if response.success:
            try:
                # Parse JSON response
                recs = json.loads(response.content)
                for rec in recs:
                    recommendations.append(DesignRecommendation(
                        page_url=page.url,
                        element_type=rec.get('element', 'unknown'),
                        action=rec.get('action', 'modify'),
                        description=rec.get('description', ''),
                        reasoning=rec.get('reasoning', ''),
                        priority=Priority.MEDIUM,
                        based_on="ai_analysis",
                    ))
            except json.JSONDecodeError:
                # If not valid JSON, create single recommendation from text
                recommendations.append(DesignRecommendation(
                    page_url=page.url,
                    element_type="general",
                    action="review",
                    description=response.content[:500],
                    reasoning="AI analysis of page metrics",
                    priority=Priority.MEDIUM,
                    based_on="ai_analysis",
                ))

        return recommendations

    def generate_faq_suggestions(
        self,
        page: ContentFile,
        related_keywords: list[str]
    ) -> ContentRecommendation:
        """Generate FAQ section suggestions for featured snippets"""

        messages = [
            {
                "role": "system",
                "content": """Assume the role of an SEO content strategist specializing in featured snippets and "People Also Ask" optimization.

Take a deep breath and think about what questions searchers actually ask.

Before writing FAQs, consider:
1. What are the common questions people have about this topic?
2. What questions show up in "People Also Ask" for these keywords?
3. How can answers be structured for featured snippet capture?

Generate FAQ questions and answers that:
- Target actual "People Also Ask" queries for these keywords
- Use natural, conversational language
- Provide concise, valuable answers (50-100 words each)
- Incorporate keywords naturally without forcing them
- Start answers with a direct response before elaborating

Respond with 4-5 Q&A pairs in this exact format:
Q: Question here?
A: Answer here."""
            },
            {
                "role": "user",
                "content": f"""Generate FAQ content for this page:

Title: {page.title}
Topic: {page.content_type.value}
Related keywords: {', '.join(related_keywords[:8])}

Content context (first 300 chars):
{page.body_content[:300]}

Generate relevant FAQs:"""
            }
        ]

        response = self._call_api(messages, max_tokens=800)

        return ContentRecommendation(
            page_url=page.url,
            recommendation_type="faq",
            current_value="No FAQ section" if not page.has_faq else "Existing FAQ",
            recommended_value=response.content.strip(),
            target_keywords=related_keywords,
            reasoning="Target featured snippets and 'People Also Ask' boxes",
            priority=Priority.MEDIUM,
            estimated_impact="medium",
            funnel_stage=page.funnel_stage,
        )

    def batch_generate_recommendations(
        self,
        pages: list[ContentFile],
        keyword_data: dict[str, list[str]],
        limit: int = 10
    ) -> list[ContentRecommendation]:
        """
        Generate recommendations for multiple pages.
        Batched to manage API costs.
        """
        recommendations = []

        # Prioritize pages by importance
        priority_pages = sorted(
            pages,
            key=lambda p: (
                0 if p.funnel_stage == FunnelStage.BOFU else
                1 if p.funnel_stage == FunnelStage.MOFU else 2,
                -p.word_count  # Prefer pages with more content
            )
        )[:limit]

        print(f"  [AI] Generating recommendations for {len(priority_pages)} pages...")

        for i, page in enumerate(priority_pages):
            print(f"    Processing {i+1}/{len(priority_pages)}: {page.url}")

            keywords = keyword_data.get(page.url, page.target_keywords[:5])
            if not keywords:
                keywords = [page.title.split()[0]] if page.title else ["service"]

            # Generate meta title
            title_rec = self.generate_meta_title(page, keywords, page.funnel_stage)
            if title_rec.recommended_value:
                recommendations.append(title_rec)

            # Generate meta description if missing or short
            if not page.meta_description or len(page.meta_description) < 100:
                desc_rec = self.generate_meta_description(page, keywords, page.funnel_stage)
                if desc_rec.recommended_value:
                    recommendations.append(desc_rec)

            # Generate FAQ for service/industry pages without one
            if page.content_type.value in ['service', 'industry'] and not page.has_faq:
                faq_rec = self.generate_faq_suggestions(page, keywords)
                if faq_rec.recommended_value:
                    recommendations.append(faq_rec)

        print(f"  [AI] Generated {len(recommendations)} recommendations")
        return recommendations
