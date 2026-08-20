# Episode 1: Reading the Contract
**Series:** Building a Reproducible Scholarly Search Toolkit
**Focus:** Architectural Boundaries & The AI Build Loop

---

## Scene 1: What is a Contract?
**[Visual]**  
- Show Slide 1 (Title) then transition to Slide 2 ("What is an Architectural Contract?").

**[Audio / Voiceover]**  
"Before we write a single line of Python, we have to define our boundaries. In software engineering, this is called an Architectural Contract. A contract specifies exactly *what* a component must do—what goes in and what comes out—without worrying about *how* it does it."

---

## Scene 2: The Master Specs
**[Visual]**  
- Show Slide 3 ("The Master Component Specifications").
- Open VSCode. Open `docs/component-specs.md` and scroll through the status tiers.

**[Audio / Voiceover]**  
"We've extracted the core contracts from a reference architecture and compiled them into this Master Specifications document. Everything we build is categorized into tiers: Baseline for what's already done, Lesson Milestone Targets for what we are building, and Reference Architecture for inspiration."

---

## Scene 3: The 8-Step Build Loop
**[Visual]**  
- Show Slide 4 ("The 8-Step AI Build Loop").

**[Audio / Voiceover]**  
"Because we're building this with AI, we enforce a strict 8-step build loop for every lesson. We start with the scientific context, read the contract, look at edge cases, prompt the AI, run tests, review, and record. By doing this, we keep the AI laser-focused on one component at a time."

---

## Scene 4: The Hallucination Trap
**[Visual]**  
- Show Slide 5 ("Why not just prompt for the whole thing?").

**[Audio / Voiceover]**  
"Why not just tell the AI to 'build a literature review tool'? Because you'll fall into the hallucination trap. You'll end up with a monolithic, untestable mess. By providing strict boundaries and writing tests first, we constrain the AI to act as a highly skilled typist rather than a rogue architect. Next time, we'll dive into the package architecture and set up our Python environment."
