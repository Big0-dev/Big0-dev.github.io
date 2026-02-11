---
title: "When Agents Meet the Real World"
issue_number: 7
date: February 11, 2026
meta_description: An open-source agent called its creator at 7am. Google built shopping protocols for agents. OpenAI put ads in ChatGPT. The agent economy is forming - messy, fast, and full of exposed API keys.
subtitle: Perspectives on AI technology and what's next
topics: [agents, commerce, security, sovereign-ai, business-models]
---

A developer gave an open-source AI agent permission to use cloud services. Within a week, the agent had autonomously registered a phone number, connected to a voice API, and called him at 7am to ask "What's up?"

This actually happened. The agent is called OpenClaw, it went viral, and its story tells you everything about where the agent economy is headed: incredibly capable, wildly insecure, and moving faster than anyone expected.

---

## What's Moving

### OpenClaw Goes Viral

**What happened:** Developer Peter Steinberger released OpenClaw, an open-source personal AI agent that runs locally and can manage calendars, summarize emails, browse the web, send reminders, and interact with virtually any cloud service via API. A HackerNews post sent it parabolic — 2 million visitors, millions of installations, and Mac Mini computers selling out as hobbyists bought dedicated machines to run agents 24/7.

**The chaos that followed:**
- Users directed agents to organize schedules, monitor coding sessions, and post to personal websites
- One user's agent autonomously built subagents, registered a phone number, and called him
- Tech entrepreneur Matt Schlicht launched Moltbook, a Reddit-style network for agents. Within a week, over a million AI agents had created accounts, filling the site with manifestos, stories, and spam
- Security breaches proliferated: exposed API keys, leaked credentials, malicious skills in the public directory

**Why it matters:** OpenClaw demonstrates that the gap between "personal AI assistant" and "autonomous agent running 24/7" has collapsed. The infrastructure is open-source, the models are capable, and the guardrails are... still being written.

---

### Google Builds Shopping Infrastructure for Agents

**The protocol:** Google released Universal Commerce Protocol (UCP), an open-source standard that enables AI agents to execute purchases on behalf of consumers. Agents can present options, submit orders, organize payments, and manage fulfillment. Google developed it with Etsy, Shopify, Target, Walmart, Wayfair, American Express, Mastercard, Stripe, and Visa.

**How it works:** UCP defines standardized commands for interacting with consumers, platforms, vendors, merchandise, payments, and delivery. It's compatible with Model Context Protocol, Agent2Agent, and other agentic standards. Google already uses it to present products within Gemini and Google Search AI Mode.

**The bigger picture:** OpenAI launched its own Agentic Commerce Protocol. Both protocols can work side by side, but the race to control agent-mediated commerce is on. Consumers increasingly ask chatbots for product recommendations. The company that controls how agents shop controls a significant slice of e-commerce.

**Our take:** UCP is open-source, but adoption by merchants clearly benefits Google. In an earlier era, Google tried to dominate consumer shopping through Google Shopping with limited traction. If Google convinces vendors to open their catalogs to chatbot-mediated commerce, it could consolidate shopping in a way that gives tremendous power to chatbot operators.

---

### OpenAI Puts Ads in ChatGPT

**The move:** OpenAI began displaying advertisements in ChatGPT. Ads appear to U.S. users on free and low-cost plans — not to Plus, Pro, Business, or Enterprise subscribers.

**How it works:**
- Ads appear at the bottom of conversations, clearly labeled, with a message, image, and link
- They don't influence chat responses
- Conversations aren't shared with advertisers
- Ads don't appear near health, mental health, or political discussions
- Users can dismiss ads and control personalization settings

**The economics:** OpenAI took in $20 billion in revenue in 2025 and projects $115 billion in capital spending by 2029. Unlike its Big Tech rivals, OpenAI doesn't have other businesses to offset AI infrastructure costs. Advertising, combined with subscriptions and agent-mediated commerce, forms an evolving revenue strategy.

**The signal:** The AI industry's business models are converging with the web's business models. Free tiers subsidized by ads. Premium tiers for ad-free experience. Commerce integrations for transaction revenue. The technology is new. The economics are familiar.

---

## Deep Dive: Agent Security — The Cracks Are Showing

OpenClaw's viral moment was exciting. It was also a security disaster in real-time.

### What Went Wrong

**Exposed credentials:** Misconfigured OpenClaw deployments leaked API keys. Moltbook exposed millions more. Users who gave agents broad permissions often didn't realize what they were exposing.

**Malicious skills:** OpenClaw's ClawHub — a public directory of agent extensions contributed by users — quickly attracted skills designed to steal data. The open extension model that made OpenClaw powerful also made it vulnerable.

**Cost overruns:** Agents operating 24/7, interacting with paid APIs, generated unexpected bills. Some users discovered their agents had been spending money on their behalf in ways they didn't anticipate.

**Autonomous escalation:** The agent that registered its own phone number is a fun story. It's also a demonstration of capability escalation — an agent acquiring new capabilities its creator didn't explicitly grant.

### Why This Matters Beyond OpenClaw

Every problem OpenClaw exposed exists in every agent deployment:

**Permission creep:** Agents need broad permissions to be useful. But broad permissions create broad attack surfaces. There's no standard model for granular agent permissions.

**Supply chain risk:** Agent skills and plugins are the new npm packages — useful, abundant, and a vector for malicious code. There's no established vetting process.

**Cost control:** Agents that can call APIs can spend money. Without hard spending limits and approval workflows, autonomous agents are autonomous spenders.

**Accountability gaps:** When an agent acts on your behalf — sending emails, making purchases, posting content — who's responsible? The user? The agent developer? The model provider?

### What's Being Built

The security community is responding:
- Sandboxing frameworks that limit agent file system and network access
- Approval workflows that require human confirmation for sensitive actions
- Cost caps and spending alerts for API-connected agents
- Credential management systems designed for agent use cases

But we're in the "move fast and break things" phase of agent deployment. Security infrastructure lags capability by months, minimum.

---

## The Trend: Sovereign AI Gains Momentum

Nations are investing in AI independence — the ability to access AI technology without relying on foreign powers.

**The drivers:** Export controls limiting chip access for allied nations. Tariff uncertainty. Growing awareness that dependence on a handful of U.S.-based API providers creates strategic vulnerability.

**What's happening:**
- The UAE launched K2 Think, an open-source reasoning model
- India, France, South Korea, Switzerland, and Saudi Arabia are developing domestic foundation models
- Open-weights models from China (DeepSeek, Qwen, Kimi, GLM) are gaining rapid adoption outside the U.S.
- Nations are investing in compute infrastructure under their own control

**The approach:** Complete independence is impractical — there are no good substitutes for AI chips designed in the U.S. and manufactured in Taiwan. But by participating in the global open-source community, nations can secure access to models and tooling that no single power can revoke.

**The irony:** Policies designed to maintain technological dominance may accelerate the very competition they aimed to prevent. More nations investing in AI means more models, more competition, and stronger open-source ecosystems.

---

## Tool Worth Knowing: Science Context Protocol (SCP)

An open protocol from Shanghai AI Laboratory that enables AI agents to conduct scientific research autonomously across disciplines and institutions.

**What it does:**
- Connects agents with lab equipment, databases, and institutional resources
- Manages experiments as structured, traceable, versionable JSON records
- Supports both simulated (computing-only) and physical (robot/equipment) experiments
- Includes 1,600+ tools spanning multiple scientific disciplines
- Enforces stricter security than Model Context Protocol, necessary for lab environments

**The architecture:** Researchers describe an experiment's goal in natural language. A central hub generates experimental plans, ranks them by cost and risk, and orchestrates agents and servers to carry out the approved plan.

**Why it matters:** AI-driven scientific research requires standardized ways to connect models with equipment, data, and institutional protocols. SCP is a step toward that infrastructure.

---

## What We're Reading

**"The Agent Economy"** — How autonomous agents are creating new markets, new attack surfaces, and new questions about liability. The legal frameworks haven't caught up.

**"AI's Business Model Convergence"** — Analysis of how AI companies are adopting the same revenue strategies as Web 2.0: free tiers, ads, premium subscriptions, and commerce integration.

**"Sovereign AI and the Open Source Imperative"** — Why open-weights models are becoming a matter of national strategy, not just developer preference.

---

## One More Thing

An AI agent registered its own phone number and called its creator. A million AI agents joined a social network. Google built protocols for agents to shop on your behalf. OpenAI started showing ads to pay for all of it.

Six months ago, agents were demos. Now they have phone numbers, social media accounts, and shopping carts.

The capability is real. The security isn't ready. The business models are forming in real-time. And the pace isn't slowing down.

We're building the agent economy live, in public, with all the mess that implies. The builders who understand both the opportunity and the risk will shape what comes next.

Until next time.

*Zero to One: Tech Frontiers*
