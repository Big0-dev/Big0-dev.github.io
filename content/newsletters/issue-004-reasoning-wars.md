---
title: "The Reasoning Wars"
issue_number: 4
date: December 16, 2025
meta_description: Every major lab has a reasoning model now. o3, extended thinking, DeepSeek R1 - the wars are reshaping what we expect AI to do.
subtitle: Your weekly guide to AI technology and the future
topics: [reasoning, o3, claude, deep-research, inference-compute]
---

Remember when we thought chain-of-thought prompting was the ceiling?

That was eighteen months ago. Now every major lab has a dedicated reasoning model. OpenAI's o3, Anthropic's extended thinking, Google's reasoning mode, DeepSeek's R1 lineage - each claiming breakthroughs in complex problem-solving.

The reasoning wars are here. And they're reshaping what we expect AI to do.

---

## This Week in AI

### OpenAI Releases o3-mini-high

**What's new:** A new variant of o3 optimized for extended reasoning on complex problems - think 5+ minute deliberation on hard math, coding, or analysis tasks.

**The performance:**
- 96.7% on AIME (math competition) problems
- State-of-the-art on SWE-bench (real-world coding)
- Significant gains on legal and medical reasoning benchmarks

**The cost:** Reasoning tokens are expensive. A single complex query can cost $5-10. This isn't for casual use.

**The use case:** Problems where being right matters more than being fast. Research, analysis, complex debugging, strategic planning.

---

### Anthropic Announces "Deep Research" Mode

**What's new:** Claude can now enter an extended research mode, spending up to 30 minutes exploring a topic before responding.

**How it works:**
- User poses a research question
- Claude searches, reads, and synthesizes information
- Produces a structured report with citations
- User can ask follow-up questions

**The positioning:** Competing with Google's NotebookLM and OpenAI's research assistants. The differentiator is depth - Claude claims to read 50+ sources before responding.

**Our take:** We're entering the era of AI that thinks for hours, not seconds. The interface expectations are shifting.

---

### Google's Gemini 2.5 Pro Emphasizes Multi-Step Reasoning

**What's new:** Google's latest flagship model focuses heavily on planning and multi-step problem decomposition.

**The architecture:** Details are sparse, but Google claims a new training approach that explicitly models step dependencies and self-correction.

**The results:** Strong on benchmarks requiring many-step solutions. Competitive but not leading on single-step tasks.

**The strategy:** Google is betting that reasoning capability becomes the key differentiator as raw language modeling plateaus.

---

## Deep Dive: What's Different About Reasoning Models

### The Old Paradigm

**Standard LLMs:**
- Generate tokens left to right
- "Think" implicitly in hidden states
- Struggle with problems requiring backtracking or exploration
- Fast but often wrong on complex tasks

**The limitation:** Complex problems require trying approaches, recognizing dead ends, and revising strategies. Standard generation doesn't support this naturally.

### The New Paradigm

**Reasoning models:**
- Explicit "thinking" phase before responding
- Can explore multiple approaches
- Self-correct when hitting contradictions
- Trade speed for accuracy

**The mechanisms:**
- **Chain-of-thought training:** Trained on examples showing reasoning steps
- **Search-based reasoning:** Try multiple paths, evaluate, select best
- **Verification loops:** Check answers before committing
- **Compute scaling:** Use more inference-time compute on harder problems

### What They're Good At

**Math and logic:** Problems with clear correct answers and verifiable steps.

**Coding:** Especially debugging, where reasoning about program state matters.

**Analysis:** Complex documents, legal questions, research synthesis.

**Planning:** Multi-step tasks with dependencies and constraints.

### What They're Not (Yet) Good At

**Creativity:** Reasoning models are methodical, not inspired.

**Speed-sensitive tasks:** When you need an answer now, reasoning overhead hurts.

**Common sense:** Surprisingly, extended reasoning can overthink simple questions.

**Ambiguous problems:** Reasoning works best when there's a "right" answer.

---

## The Trend: "Thinking Time" as a Product Feature

**What's emerging:** Products that explicitly advertise how long the AI will think.

**Examples:**
- "Quick mode" (instant response) vs. "Deep mode" (extended reasoning)
- Progress indicators showing "exploring solutions..."
- User control over reasoning budget (think harder = costs more)

**The UX challenge:** Users expect instant responses. Waiting 5 minutes feels wrong, even if the result is better.

**The solution emerging:** Async patterns - submit a question, do other work, get notification when analysis is ready.

---

## Tool of the Week: o1-engineer

An open-source tool that wraps reasoning models for software engineering tasks.

**What it does:**
- Decomposes coding tasks into reasoning steps
- Uses o3 or Claude extended thinking for planning
- Executes with faster models for implementation
- Verifies results and iterates

**The workflow:** Describe what you want -> AI reasons about approach -> AI implements with verification -> You review.

**Who it's for:** Developers tackling complex refactoring, architecture changes, or unfamiliar codebases.

**The limitation:** Slow. Expensive. But surprisingly effective on hard problems.

---

## What We're Reading

**"Scaling Laws for Reasoning"** - Research from Anthropic on how reasoning capability scales with compute. Non-obvious patterns.

**"When More Thinking Hurts"** - Paper documenting cases where reasoning models perform worse than base models. Overthinking is real.

**"The Cost of Being Right"** - Analysis of reasoning model economics. Being 10% more accurate might cost 10x more.

---

## One More Thing

The reasoning wars represent a genuine capability frontier. These models can solve problems that were impossible a year ago.

But capability isn't utility. A model that takes 10 minutes to answer costs real money and real time. The question isn't whether reasoning models are better - it's whether they're better enough to justify the trade-offs.

For some tasks (medical diagnosis, legal analysis, complex coding), the answer is clearly yes. For most tasks (email, summarization, casual queries), the answer is clearly no.

The art is knowing which you're dealing with.

See you next week.

*Zero to One: Tech Frontiers: Understanding AI technology and building the future.*
