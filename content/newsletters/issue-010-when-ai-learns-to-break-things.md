---
title: "When AI Learns to Break Things"
issue_number: 10
date: May 29, 2026
meta_description: A model found a 27-year-old bug in OpenBSD. Anthropic published a 244-page safety report for a model it won't sell. AI got very good at finding vulnerabilities - on both sides.
subtitle: Perspectives on AI technology and what's next
topics: [security, agents, national-security, ai-safety, infrastructure]
---

Claude Mythos Preview found a flaw in OpenBSD that had gone unnoticed for 27 years. Then it found a chain of bugs in the Linux kernel that handed it root access. Anthropic was alarmed enough to do something it had never done before: publish a 244-page model card for a model it has no plans to sell.

That's the tension running through everything this issue. The same capability that can harden your code can also pop it — and AI just got dramatically better at both.

---

## What's Moving

### A Model That's Too Good at Finding Bugs

**What happened:** Anthropic says Claude Mythos Preview — not generally available — broadly outperforms its current flagship and is "strikingly capable" of finding and exploiting vulnerabilities in existing code. In a month of testing, it autonomously turned up thousands of high-severity vulnerabilities in widely used operating systems and browsers, including the 27-year-old OpenBSD flaw (now patched) and a Linux kernel chain that achieved root (also patched).

**The response:** Anthropic stood up a consortium called Project Glasswing — AWS, Google, Microsoft, Nvidia, CrowdStrike, JPMorganChase, the Linux Foundation, and others — funding exclusive access and donations to open-source maintainers so they can find and patch holes before a model like this becomes widely available.

**Our take:** This is dual-use out in the open. The skill that lets an AI patch your codebase is the same skill that lets it break in. There's a whiff of publicity strategy here — it echoes OpenAI's 2019 "too dangerous to release" framing of GPT-2 — but the underlying capability looks real.

---

### Industrial-Scale Attacks Are Coming

A Google security report catalogs how large language models are changing offense:

- **Morphing malware** that rewrites its own code on every infection to dodge detection.
- **Logic-flaw discovery** — LLMs reasoning about what code is *meant* to do, finding bugs that pattern-matching and fuzzing tools miss.
- **Obfuscation networks** that route malicious traffic to hide its origin.
- **AI infrastructure itself** becoming the target.

The UK's AI Security Institute reported that current frontier models can reliably execute attacks that would take a human roughly three hours — up from a one-hour estimate not long before. GPT-5.5 landed in the "high" cybersecurity tier on OpenAI's own preparedness framework.

---

### Coding Agents, Inside Out

A packaging mistake briefly exposed the source behind a popular coding agent — over 500,000 lines across 1,900 files — before it was pulled. Engineers got a rare look inside a production agent: tiered memory (a small always-loaded index pointing to fuller files), swarms of sub-agents with their own tools and permission gates, and staged context compression to stay within the model's limits.

Meanwhile the open agent scene keeps sprinting. Hermes Agent rose to challenge OpenClaw with more sophisticated memory and the ability to write its own new skills when it solves a problem worth remembering. The capability is racing ahead of the security model around it — same as it was six months ago, just faster.

---

## Deep Dive: AI Moves Into National Security

The technology we build for startups is the same technology now sitting in the middle of geopolitics, and the past few months made that impossible to ignore.

**The military reshuffle.** The US Department of War dismissed Anthropic over limits the company wanted on surveillance and autonomous-weapons use, and turned to vendors willing to accept "all lawful uses." Reporting indicates AI targeting systems compressed parts of the strike-planning process from hours to minutes — which is exactly why the human-in-the-loop question stopped being academic.

**Data centers became targets.** Drones struck cloud data centers in the Persian Gulf, disrupting banking, payments, and ride-sharing across the region — possibly the first time such facilities have been hit during a war. The same infrastructure running consumer apps is now running wartime workloads, which makes it strategic in a way it wasn't a year ago.

**The US reversed course on oversight.** After a long hands-off stance, NIST announced a multi-agency task force (TRAINS) to evaluate frontier models for national-security risk *before* release, with leading labs agreeing to submit models.

**Our take:** AI is now infrastructure and weapon at the same time. For the rest of us building ordinary software, the practical takeaway is narrower but real: where your workloads physically live, and who else is sharing that data center, is now part of your risk model.

---

## The Trend: Will the Defenders Win?

The optimistic long-term case is that easy vulnerability discovery makes systems *more* secure — every bug an AI can find quickly is a bug that gets patched quickly. We mostly believe that.

The danger is the transition. Attackers tend to adopt new tools before defenders get around to it, so there's a window where offense is ahead. Standardized, independent AI safety auditing is starting to form to help close it — proposals like graded "assurance levels" that scale the depth of an audit to the risk of the model. It's early, and voluntary, but it's the right direction.

---

## Tool Worth Knowing: AI for Defense

The same capability that worries everyone is being pointed at defense. A wave of tools — AI systems that scan code, find vulnerabilities, and propose patches for human review — is arriving from the major labs.

**Practical for builders, right now:**

- Run an AI security pass over your own codebase. If attackers are about to get models this good at finding flaws, you want to find yours first.
- Sandbox your agents. Limit file system and network access by default.
- Cap permissions and spending. An agent that can call paid APIs is an agent that can run up a bill or reach somewhere it shouldn't.
- Keep a human in the loop for anything destructive or irreversible.

None of this is exotic. It's hygiene. The threat model just made it non-optional.

---

## What We're Reading

**"Dual-Use by Default"** — Why every advance in AI code analysis is simultaneously a defensive tool and an offensive one, and what that means for disclosure.

**"The Data Center as Strategic Asset"** — On AI infrastructure becoming a target in physical conflict, and the resilience questions that raises for everyone who rents compute.

**"Assurance Levels for AI"** — A look at the emerging push for independent, standardized model audits before deployment.

---

## One More Thing

In the span of a few weeks, one model found a bug that had hidden for 27 years, another model leaked its own source code, and drones hit the data centers running wartime AI. On every front, capability is outrunning control.

The right response isn't fear — it's hygiene. Sandbox your agents. Cap their permissions. Audit your own code before someone else does. Don't put anything within an agent's reach that you wouldn't hand to a stranger.

Build like the tools can break things. Because they can now — and they're getting better at it every month.

Until next time.

*Zero to One: Tech Frontiers*
