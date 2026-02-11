---
title: "The Enterprise AI Reality Check"
issue_number: 3
date: December 23, 2025
meta_description: Only 18% of Salesforce customers use AI features. The gap between demo and deployment is brutal. Here's what's actually happening in enterprise AI.
subtitle: Perspectives on AI technology and what's next
topics: [enterprise, deployment, data-quality, change-management, roi]
---

I've been talking to CTOs. Not the ones on conference stages — the ones in the trenches, actually deploying AI in production.

The gap between demo and deployment is brutal.

Everyone has an AI strategy. Most have pilots. Few have production systems that work reliably at scale. The reasons are consistent, and they're not what the vendors want to talk about.

Here's what's actually happening.

---

## What's Moving

### Salesforce's AI Adoption Problem

**The number:** Only 18% of Salesforce customers actively use their Einstein AI features, despite aggressive bundling into enterprise licenses.

**The reasons cited:**
- Integration complexity with existing workflows
- Training requirements for sales teams
- Unclear ROI measurement
- Data quality prerequisites not met

**Why it matters:** If Salesforce — with its massive installed base and aggressive AI push — sees 18% adoption, what does that suggest about enterprise AI uptake generally?

**The counterpoint:** Early adopters report meaningful productivity gains. The gap is between "works in theory" and "works in our environment."

---

### Usage-Based Pricing for AI Copilots

**The shift:** Major vendors are introducing usage-based pricing alongside per-seat models — an implicit acknowledgment that many seats go unused.

**The math:**
- Per-seat: ~$30/user/month regardless of usage
- Usage-based: pay per interaction, capped at the seat price

**What it signals:** Enterprises pushed back on paying full price for features employees don't use. Vendors responded rather than lose deals.

**Our take:** This is healthy. Pricing that aligns with actual value delivered will accelerate adoption more than aggressive bundling.

---

### Enterprise AI Audits Become a Business

**The trend:** Consulting firms now offer comprehensive audits of enterprise AI deployments, assessing ROI, risks, and optimization opportunities.

**What they're finding:**
- 60% of AI projects don't have clear success metrics
- Data quality issues block 40% of planned use cases
- Most enterprises underinvest in change management
- Security reviews often happen too late

**The irony:** Firms selling consulting to fix problems that rushed AI adoption created. This is a business model.

**The value:** Third-party assessment helps executives understand what's working and what isn't.

---

## Deep Dive: Why Enterprise AI Deployments Fail

### Problem 1: The Data Quality Gap

**The assumption:** "We have lots of data, so AI will work great."

**The reality:** Most enterprise data is:
- Inconsistent across systems
- Full of duplicates and errors
- Poorly documented
- Not structured for AI consumption

**The result:** Models trained on bad data produce bad outputs. Garbage in, garbage out — now at scale.

**The fix:** Data cleanup is boring and expensive. But it's prerequisite, not optional.

### Problem 2: Integration Complexity

**The demo:** AI tool works beautifully in isolation.

**The production environment:**
- Authentication against enterprise identity
- Compliance with data residency requirements
- Integration with legacy systems
- Audit logging for regulated industries
- Graceful degradation when the AI service is down

**The gap:** Vendors sell the demo. Enterprises buy the production system. The difference is 10x the effort.

### Problem 3: Change Management Failure

**The pattern:**
1. Deploy AI tool
2. Announce it to employees
3. Wait for adoption
4. Wonder why adoption doesn't happen

**What's missing:**
- Training on when and how to use the tool
- Workflow redesign to incorporate AI naturally
- Incentive alignment (are employees rewarded for using AI?)
- Feedback loops to improve the deployment

**The truth:** Technology deployment is 20% technology, 80% people.

### Problem 4: Unclear Success Metrics

**The question nobody asks upfront:** How will we know if this worked?

**Common anti-patterns:**
- "We'll measure productivity" (How? Compared to what baseline?)
- "Users will tell us if they like it" (Users adapt to whatever you give them)
- "We'll see cost savings" (In which budget? When?)

**The fix:** Define measurable outcomes before deployment. Accept that some projects will fail the metrics.

---

## The Trend: "AI Readiness" Becomes a Job

**What's emerging:** A new role focused on preparing organizations for AI adoption.

**The responsibilities:**
- Data quality assessment and remediation
- Process documentation and redesign
- Change management planning
- Vendor evaluation and integration design
- Success metric definition

**Who's hiring:** Large enterprises, consulting firms, and increasingly mid-market companies recognizing they're not ready.

**The skills:** Mix of data engineering, business analysis, change management, and AI literacy. Full-stack organizational capability.

---

## Tool Worth Knowing: LangSmith

LangChain's observability platform for LLM applications.

**What it does:**
- Traces every LLM call with inputs, outputs, and latency
- Identifies which prompts perform poorly
- Enables A/B testing of prompt variations
- Captures production data for fine-tuning

**Why it matters:** You can't improve what you can't measure. Most AI deployments lack basic observability.

**The limitation:** Adds another vendor to the stack. Some teams build equivalent functionality in-house.

---

## What We're Reading

**"The AI Productivity Paradox"** — Harvard Business Review analysis of why measured productivity gains from AI lag expectations. Measurement is harder than it looks.

**"When AI Projects Fail"** — McKinsey's post-mortem analysis of failed enterprise AI initiatives. Patterns are consistent and avoidable.

**"Building AI Products, Not Features"** — Product management perspective on why bolted-on AI often disappoints.

---

## One More Thing

There's a version of enterprise AI that's inevitable: automation of genuinely repetitive tasks, assistance for genuinely complex analysis, augmentation of genuinely valuable work.

And there's a version that's hype: AI as magic pixie dust sprinkled on broken processes, AI as replacement for thinking, AI as checkbox on a strategy deck.

The difference isn't the technology. It's the implementation.

The enterprises that win will be the ones that treat AI deployment like any other complex change initiative — with clear goals, realistic timelines, proper investment, and willingness to course-correct.

That's less exciting than "AI will transform everything overnight." It's also true.

Until next time.

*Zero to One: Tech Frontiers*
