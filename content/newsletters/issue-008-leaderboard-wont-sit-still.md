---
title: "The Leaderboard Won't Sit Still"
issue_number: 8
date: March 25, 2026
meta_description: Four flagship models traded the top spot in six weeks. Open weights pulled within the margin of error, prices went up instead of down, and laptops started standing in for the cloud.
subtitle: Perspectives on AI technology and what's next
topics: [open-weights, frontier-models, pricing, local-ai, coding-agents]
---

In one six-week stretch, the title of "best model in the world" changed hands four times. Gemini took the lead. GPT took it back. Claude held the top of the human-preference rankings the whole time anyway. And a 9-billion-parameter open model small enough to run on a laptop quietly beat an OpenAI model more than ten times its size on most language tasks.

If you picked a model in January and wired your entire product around it, the ground has already moved twice. That's the real story this quarter — not which model won, but that "winning" now lasts about three weeks.

---

## What's Moving

### Gemini 3.1 Pro Takes the Lead — and Undercuts on Price

**What happened:** Google's Gemini 3.1 Pro topped Artificial Analysis's Intelligence Index, a weighted average of ten benchmarks built around real-world work. The headline isn't the score. It's the bill. Running the full index reportedly cost around $892 on Gemini 3.1 Pro versus roughly $2,486 on Claude Opus 4.6 and over $2,300 on the GPT-5 line.

**Why it matters:** Google says the gains came from a better model, not from burning more tokens at inference — Gemini 3.1 Pro used about the same token budget as its predecessor while scoring meaningfully higher. That's the efficient kind of progress: more capability per dollar, not just more dollars.

**Our take:** The number worth tracking is score-per-dollar, not score. A model that wins a benchmark at three times the cost loses the only benchmark that matters to a startup — the invoice.

---

### GPT Answers Back: Higher Score, Higher Bill

**What happened:** OpenAI shipped GPT-5.4 and then GPT-5.5 in quick succession, retaking the top of the Intelligence Index. But per-token prices roughly doubled relative to the previous generation, and GPT-5.5 carries a quieter problem: on knowledge benchmarks that penalize confident wrong answers, it hallucinates more than its rivals. It knows more facts and admits ignorance less often.

**Why it matters:** "Knows more" and "trustworthy in production" are not the same property. A model that confidently invents a function signature, a citation, or a refund confirmation is more dangerous than a less capable one that says "I'm not sure."

**Our take:** For anything that touches a customer or a database, we'd rather ship the model that knows its limits. Raw intelligence is cheap to demo and expensive to debug.

---

### Open Weights Pull Within the Margin of Error

The gap between open and closed models used to be measured in years, then months. This quarter it's within rounding distance on several benchmarks:

- **GLM-5** (744B-parameter mixture-of-experts, MIT license) became the strongest open-weights model on the Intelligence Index, trailing the closed leaders by a few points. Its follow-up, **GLM-5.1**, is built to grind on a single task autonomously for hours.
- **Kimi K2.6** (1 trillion parameters) can spin up hundreds of parallel sub-agents on one task and cut its hallucination rate sharply versus the prior release.
- **Qwen3.5** shipped a family where a 9B model outperforms a 120B open competitor on most language tasks — small enough to run on a developer's laptop.
- **Nvidia Nemotron 3** arrived as the first US-built open-weights leader since Meta's Llama 4, fastest in its size class, and shipped with its training datasets and recipes, not just weights.

**The counter-current:** Meta went the other way. Its new Muse Spark model is closed. After being the leading US champion of open weights, that's a real loss for the developer community — though the Chinese labs and Nvidia have more than filled the gap.

---

## Deep Dive: The Cloud Isn't the Only Place to Run AI

A Stanford and Together AI study introduced a metric worth internalizing: **intelligence per watt** — accuracy on a task divided by the power it takes to get there.

The finding: on local hardware, intelligence per watt rose **5.3x between 2023 and 2025**, driven by smaller high-performing models and better chips. In their analysis, laptops running small models answered roughly **88%** of single-turn queries correctly relative to the cloud, while using far less power. Route the easy queries locally and the hard ones to the cloud, and simulated power savings topped **80%**.

Liquid AI made it concrete with **LFM2.5** — a reasoning model that fits in under 900 megabytes and runs on a phone.

**Why it matters if you're building:** Local inference isn't just a privacy story anymore. It's a cost and latency story. A hybrid architecture — small local model for the common case, frontier API for the hard case — can cut both your bill and your tail latency without much accuracy loss.

**The honest caveat:** Small models still hallucinate more, and the frontier still wins the genuinely hard problems. The most capable local model still trails the top closed models by 10–13 points on accuracy. Use local models where instruction-following matters more than encyclopedic recall — agentic glue, data extraction, retrieval — and keep the heavy reasoning in the cloud.

---

## The Trend: The "SaaSpocalypse" Scare

For a few weeks the software market panicked. Anthropic shipped Cowork plus a set of plugins targeting white-collar job functions — calendar management, document search, financial analysis, legal review — and then a security tool that finds and patches vulnerabilities. Investors did the math: if an agent can replicate the software, why pay the subscription? A widely-watched software index shed roughly a quarter of its value.

Then Anthropic turned around and announced integrations *with* the same companies its agents threatened — Docusign, Salesforce, Intuit, and others. The stocks recovered most of the drop.

**Our take:** SaaS isn't dying. It's going AI-native. Large language models dissolve the lock-in that came from "we don't want to learn a new interface." They do not dissolve moats built on proprietary data, regulatory compliance, network effects, or embedded transactions. The lesson for founders is sharper than the headline: a custom internal tool that used to justify a per-seat subscription is now a weekend build. The buy-versus-build math just shifted under everyone.

---

## Tool Worth Knowing: Context Hub (chub)

Coding agents are trained on old data, so they cheerfully call deprecated APIs, hallucinate parameters, or don't know a tool exists. Context Hub is a small CLI built so your *agent* — not you — can fetch current documentation on demand.

```bash
npm install -g @aisuite/chub
chub search openai
chub get openai/chat --lang py
```

You point your agent at it (a prompt or a skill file), and it pulls live docs for LLM providers, databases, payment processors, and more. It even accepts feedback from agents that discover a doc is wrong or incomplete.

**Why we care:** Nearly every team we know has hand-written markdown docs to feed their coding agent the APIs it keeps getting wrong. This standardizes that chore. It's a small tool solving a real, daily papercut.

---

## What We're Reading

**"Score-Per-Dollar Is the Only Benchmark That Ships"** — Why total cost to complete a task, not leaderboard position, should drive model selection. The most-quoted scores and the most-economical choices are diverging.

**"Intelligence Per Watt"** — The Stanford/Together paper arguing that the mainframe-to-PC shift is repeating itself in AI, one efficient small model at a time.

**"The Open-Weights Center of Gravity Moved East"** — A look at how GLM, Qwen, Kimi, and DeepSeek came to define the open frontier, and what Nvidia's Nemotron entry means for it.

---

## One More Thing

We've stopped marrying models. We can't afford to — and neither can you.

In a single quarter, the leader changed four times, prices went *up* instead of down, open weights closed most of the gap, and the cheapest way to answer a query started living on a laptop. The teams that handle this well aren't the ones that bet correctly in January. They're the ones who built so that swapping the underlying model is a config change, not a rewrite.

Treat the model as a dependency, not a foundation. Abstract your prompts, keep your evals model-agnostic, and assume whatever you're using today will be second-best by next month. That's not pessimism. It's just how you build on ground that keeps moving.

Until next time.

*Zero to One: Tech Frontiers*
