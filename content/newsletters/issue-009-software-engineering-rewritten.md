---
title: "Software Engineering, Rewritten"
issue_number: 9
date: May 13, 2026
meta_description: Coding agents don't accelerate all work equally. The bottleneck moved from building to deciding what to build. And the jobpocalypse everyone predicted isn't showing up in the data.
subtitle: Perspectives on AI technology and what's next
topics: [software-engineering, ai-native-teams, jobs, coding-agents, product]
---

We build software for a living, so we pay close attention when the way software gets built changes underneath us. Right now it's changing fast — but not evenly, and not in the direction the doom headlines predicted.

The short version: coding agents have made some work dramatically faster and barely touched other work. The hard part of the job moved from *typing the code* to *deciding what to type*. And the mass-unemployment story everyone keeps forecasting still isn't visible in the actual numbers.

---

## What's Moving

### Coding Agents Speed Up Some Work, Not All

A useful mental model making the rounds, from Andrew Ng: rank software work by how much agents accelerate it, and you get **frontend > backend > infrastructure > research**.

- **Frontend** is dramatically faster. Agents are fluent in TypeScript, React, and the rest, and they can open a browser, look at what they built, and iterate. The loop closes itself.
- **Backend** is harder. It takes real steering to make a model think through the corner cases that cause subtle bugs, security holes, and the kind of data-corruption issue that's miserable to trace.
- **Infrastructure** is harder still. Models know less about the messy tradeoffs of scaling and reliability, and infra bugs — a quiet network misconfiguration — can take deep expertise to find.
- **Research** moves the least. Most of the work is forming hypotheses and interpreting experiments, not writing the code that runs them.

**Our take:** This matches our experience exactly. We push our frontend work hard now and expect output that would have taken weeks a year ago. On backend and infra, we deliberately slow down and think. Anyone selling you "AI builds the whole system" is selling you the frontend demo and hoping you don't ask about the database migration.

---

### The Bottleneck Moved to "What to Build"

When building gets cheap, the constraint becomes deciding what's worth building. Teams are responding by pushing the engineer-to-product-manager ratio down — in some cases from 8:1 toward 1:1 — and the fastest teams go further: engineers who can do product work directly, with no handoff in between.

And the bottleneck keeps moving downstream. We've watched a team ship a feature so fast that marketing scrambled to explain it and legal hadn't finished its review. Speed up coding 10x and everything around it — design, marketing, compliance — suddenly looks slow.

---

### Small Teams of Generalists Win

The teams getting the most out of agents are small — roughly 2 to 10 people — and staffed with generalists who can cross functions. One person might be a strong engineer and another a strong PM, but both can step into design, talk to users, and reason about the business. Co-location helps: when everyone's in the room, the communication bottleneck nearly disappears.

**Our take:** This is the bet Big0 was built on. A small senior team, the CEO still writing code, the CTO reviewing every PR, no account managers relaying messages between people who never talk. We didn't adopt this structure because of AI — but AI is what makes it outperform a department three times its size.

---

### The Jobpocalypse Isn't in the Data

Software engineering is the field most exposed to coding agents. If AI were going to gut a profession, this is where you'd see it first. Instead, software job postings are rising, and overall unemployment is sitting at a healthy level.

So why does the collapse narrative persist? Two reasons worth naming:

- **AI washing.** Companies that over-hired during the cheap-capital years would rather attribute layoffs to a powerful new technology than to a hiring mistake. "We're more productive with AI" sounds better than "we over-built."
- **Incentives.** Labs and vendors benefit from the story that their technology is powerful enough to replace people — it justifies the valuations and the price tags.

Meanwhile, a Gallup survey found about half of US workers used AI at work last year, and most of them said it made them more productive — a tool that helps people do their jobs, not one doing the jobs for them.

**Our take:** AI is changing work, not erasing it. The new roles are already appearing — AI Engineers who build with prompts, agents, and evals, and "X Engineers" embedded in a function (think Recruiting Engineer or Marketing Engineer) who build the software that function needs.

---

## Deep Dive: The Product-Management Bottleneck Is Real — Here's What We Do About It

When you can build almost anything in a day, "what should we build?" becomes the expensive question. Here's how we handle it in practice:

**Tighten the feedback loop.** We show working software every two weeks, not status decks. A demo a user can click surfaces the wrong assumptions a roadmap never will.

**Kill features fast.** The cost of paying down technical debt has dropped — an agent can refactor for you — so the penalty for building the wrong thing is lower than it used to be. That argues for shipping, watching, and cutting quickly. With one caveat: that bias toward speed applies to frontend and product surface area, *not* to the backend and infrastructure decisions that are painful to reverse.

**Use synthetic users as a thinking aid, not a verdict.** Recent work on AI persona generators can produce a diverse panel of simulated users to pressure-test an idea before you build it. We treat that as a way to find blind spots early. Real users still cast the deciding vote.

The throughput problem isn't engineering anymore. It's judgment. And judgment doesn't come from a faster model.

---

## The Trend: The AI-Native Software Business

The "SaaSpocalypse" panic — investors fearing that agents would replicate paid software — already came and went (we covered it last issue). The durable lesson for builders is this: small teams can now stand up a credible alternative to an established tool startlingly fast. The products that survive are the ones whose moat isn't the UI but the proprietary data, the compliance work, the network effects, or the embedded transactions underneath it.

**For founders:** A custom internal tool that used to justify a per-seat subscription is now a weekend project. Re-run your buy-versus-build math. A lot of "we'll just pay for it" decisions are now "we'll just build it" decisions — and a lot of "build it" decisions are now things a two-person team can actually finish.

---

## Tool Worth Knowing: The Agentic Coding Stack

The stack that's emerging around serious agent-assisted development:

- **Coding agents** — Claude Code, Codex, and similar — that plan, write, run, and debug across a whole codebase.
- **Agent skills** — reusable instruction files (the `SKILL.md` pattern) that move workflow logic out of one-off prompts and into something you can version and share.
- **Spec-driven workflows** — write the spec first, let the agent implement against it step by step, stay in control of what gets built.

**Our note:** Treat agents like talented junior engineers. Give them a clear spec, review their output, and don't let them touch infrastructure unsupervised. The leverage is real; so is the damage when you skip the review.

---

## What We're Reading

**"The Product-Management Bottleneck"** — On why deciding what to build, not building it, is now the scarce skill — and what that does to how teams are staffed.

**"Frontend, Backend, Infra, Research"** — A breakdown of where coding agents actually save time and where the savings quietly evaporate.

**"There Will Be No Jobpocalypse"** — The contrarian case that AI is creating more engineering work than it destroys, backed by hiring data rather than vibes.

---

## One More Thing

We've said this before and the last few months have only made it truer: the value was never in the typing.

Agents can write the function, scaffold the page, and refactor the module. What they can't do is decide which of those things is worth doing, recognize when the output is subtly wrong, or hold the architecture in their head while talking to the customer who'll actually use it. That's judgment, and the tools getting faster doesn't move it an inch.

It's the whole reason we still run Big0 the way we do — the CEO in the code, the CTO on every PR, the engineers talking straight to the people they're building for. The tools changed. The hard parts didn't.

Until next time.

*Zero to One: Tech Frontiers*
