---
title: "Engineering Audio Without Blocking Your Ears"
subtitle: A conversation between two hardware product managers
meta_description: Two hardware product managers discuss Big0's bone conduction earpiece project — from transducer selection through PCB design to production-ready prototype.
category: Hardware Engineering
intro: "Raj Patel, Product Director at an industrial safety equipment company, meets Sarah Chen, Head of Product at a wearable technology firm, at a hardware engineering conference to discuss audio solutions for industrial environments."
date: 2025-10-12
tags: hardware, bone conduction, PCB design, prototyping, wearable technology
---

## The Conference Meeting

**Raj Patel:** Sarah, I keep running into the same problem. Our field teams need comms audio, but they also need to hear what's happening around them. Earbuds are a safety hazard on an active site.

**Sarah Chen:** We dealt with the exact same tension. Audio quality versus situational awareness — pick one. That was the tradeoff until we found a team that could actually engineer bone conduction properly.

**Raj Patel:** You went the bone conduction route? The commercial products I've tested are... underwhelming. Thin audio, uncomfortable after an hour, too fragile for real work environments.

**Sarah Chen:** That's why we didn't use a commercial product. We had Big0 engineer one from scratch.

---

## The Technical Requirements

**Raj Patel:** From scratch — meaning custom electronics, custom enclosure, everything?

**Sarah Chen:** Everything. The transducer, the amplifier circuit, the PCB, the enclosure, the firmware. When you need specific performance in a specific form factor, off-the-shelf modules don't cut it.

**Raj Patel:** What drove that decision? Custom hardware is expensive.

**Sarah Chen:** We tried adapting existing products first. Consumer bone conduction headsets are designed for jogging — they're optimized for music, not voice intelligibility. And they fall apart in industrial conditions. We spent months trying to make modifications work before accepting that the foundation was wrong.

**Raj Patel:** So you needed voice-optimized audio in a form factor that fits under a hard hat?

**Sarah Chen:** Under a hard hat, under a tactical helmet, inside hearing protection. The form factor constraints were strict. And the audio had to be clear in environments above 85 decibels.

---

## The Development Process

**Raj Patel:** Walk me through how they approached it.

**Sarah Chen:** They started with the transducer — which bone conduction driver, at what frequency response, driven by what amplifier profile. That's the core physics. Get that wrong and nothing else matters.

**Raj Patel:** How do you optimize for speech versus music?

**Sarah Chen:** Different frequency emphasis. Speech intelligibility peaks in a narrower band than music reproduction. Big0 tuned the amplifier and firmware DSP to prioritize voice frequencies. The result sounds worse for music and better for understanding someone talking to you — which is exactly the right tradeoff.

**Raj Patel:** What about the PCB?

**Sarah Chen:** Custom board integrating the amplifier, Bluetooth module, battery management, and microphone. They got it small enough to sit behind the ear without feeling like you're wearing a brick. Multiple revision cycles to get the layout right — component placement affects both electrical performance and thermal management in something that small.

---

## The Prototyping Approach

**Raj Patel:** How many prototype iterations?

**Sarah Chen:** Several for the enclosure. 3D printing let them test a new form factor every few days. The critical variable was contact pressure — how firmly the transducer presses against the temporal bone. Too light and you lose audio. Too heavy and it's uncomfortable within thirty minutes.

**Raj Patel:** That's a narrow window.

**Sarah Chen:** Very narrow. And it has to work across different head sizes and shapes. The mounting mechanism went through its own iteration cycle independent of the enclosure shape.

**Raj Patel:** What about environmental testing?

**Sarah Chen:** Noise testing at different dB levels, Bluetooth range testing, battery life characterization, drop testing. They built a structured test protocol and ran every prototype revision through it. No guessing about whether a change actually improved things.

---

## The Deliverable

**Raj Patel:** What did they hand over at the end?

**Sarah Chen:** Complete engineering package. Schematics, PCB layouts, bill of materials with specific part numbers and suppliers, 3D models ready for injection molding tooling, firmware source code, test reports. Everything a contract manufacturer needs to produce units.

**Raj Patel:** So you could take that package to any CM and get production units made?

**Sarah Chen:** That was the point. Big0 handled the engineering. We choose the manufacturing partner. No vendor lock-in, no proprietary dependencies. We own every file.

**Raj Patel:** How long from kick-off to that deliverable?

**Sarah Chen:** Faster than our previous hardware projects, and those used more conventional technology. The 3D printing approach for enclosure iteration saved significant time compared to traditional tooling cycles.

---

## The Recommendation

**Raj Patel:** Sarah, I've been evaluating three approaches — adapt a commercial product, license a reference design, or custom engineer. You're telling me custom was the right call?

**Sarah Chen:** For our requirements, absolutely. If you need standard consumer specs, buy off the shelf. If you need specific performance in a specific form factor for a specific environment — custom engineering pays for itself because you don't spend months trying to make the wrong product work.

**Raj Patel:** And Big0 handles the full stack — electronics, mechanical, firmware?

**Sarah Chen:** One team, one integration. No finger-pointing between an electronics vendor and a mechanical vendor and a firmware contractor when something doesn't work. They own the whole problem.

**Raj Patel:** That's what I need. Our field teams deserve better than consumer products duct-taped into industrial service.

**Sarah Chen:** Get your requirements documented — form factor constraints, audio specs, environmental conditions, target cost. The clearer your brief, the faster they can move.
