Title: How we use AI like engineers
Date: 2026-05-20
Modified: 2026-05-21
Category: Engineering
Tags: engineering, ai, developer-experience, workflow
Slug: how-we-use-ai-like-engineers
Authors: Ashwini Chaudhary
Summary: Using AI to recover context in large codebases and take repetitive work off engineers' plates without compromising on code and review quality or operational safety.

Context engineering and management is a hard problem and is the highest priority even before a single line of code is written.

> Note: The article uses the term AI and LLM interchangeably. What I mean is a mix of chat-based AI tools, autocomplete, and agentic tools like [Claude Code](https://www.anthropic.com/claude-code), [Cursor](https://cursor.com/), [Codex CLI](https://github.com/openai/codex), [Pi](https://pi.dev/), and even newer desktop apps like Claude CoWork and Codex.

It's very common for a person operating on LLMs to ask for too much in one pass. This often results in a gigantic diff that leaves the engineer doing the hard part afterward: figuring out what the change actually means and whether it even includes everything they asked for to begin with. The second problem is that the resulting code review often does not give either the engineer or the LLM enough reasoning to produce a high-quality review that really addresses the diff from a business-logic and code-quality point of view.

What has worked for us over time is to create narrower contexts for AI and allow AI to recover context faster without being married to the same LLM session where we actually started the discussion with the AI. We also do not want the workflow married to one provider or one UI. The durable part has to be the repo context, scripts, skills, tests, review gates, and the human habits around them. Having a workflow built around this significantly helps with producing high quality work and work is broken down into small chunks that are easier to review and catch mistakes early.

At a high level, the shape of the work matters more than the amount of output:

<figure>
  <img
    src="{static}/images/articles/how-we-use-ai-like-engineers/big-diff-vs-small-drafts.svg"
    alt="Comparison between one large AI-generated change and several smaller reviewable drafts."
    style="width:100%;height:auto;display:block;"
  />
  <figcaption>Smaller drafts are easier to review and easier to reason about.</figcaption>
</figure>

## Where it actually helps

The current models are ridiculously good at discovering code related to logic that spans various repos, and our [switching to a mono-repo last year](/the-monolith-that-made-ai-actually-useful.html) when Claude Code was starting to pick up has made a huge difference for us.

Saying AI is good at this doesn't mean an engineer isn't able to do the same. The difference is that assembling all of those files, conventions, blast-radius clues, and related pieces is simply faster than starting from zero and jumping around in code manually. That itself saves significant time upfront and lets us guide the AI if it's looking in the wrong places. Sometimes it points to old dead code, which is not what we want. AI also loves to ignore existing utilities and redefine them every chance it gets, which is why it still requires steering from the engineer.

Additionally, AI helps with the skeleton tests and docs that will be needed, along with any renaming that is supposed to happen and stay consistent across many files. And if the task is broken down into small enough subtasks, those guardrails are even easier for AI to follow.

## Context matters more than prompting

While we were discovering these patterns ourselves as we got more familiar with Anthropic's Sonnet/Opus and OpenAI's Codex, the final clarity we needed to apply them across all of our repos came from this blog from [OpenAI Engineering](https://openai.com/index/harness-engineering/). Boris Cherny has also talked publicly about why the concept of an index (used by GitHub Copilot and Cursor) does not hold up as well for these more powerful LLMs anymore: they prefer to explore code every time, and indexing breaks down if you have hundreds of feature branches because you effectively need a different index for each branch.

Since then we have made significant changes to our AGENTS.md and CLAUDE.md files. We also built skills to keep that shape repeatable when a new project or directory shows up, instead of hoping someone remembers the pattern.

The bigger gains usually come from giving the model a structure it can work inside:

- table of contents under each project
- role of each project relative to other projects in the monorepo
- stable project instructions
- clear repository conventions
- useful ignore pattern (but not too many)
- obvious quality gates
- enough architectural context to make the connections obvious

Configuration shape matters too. Reusable rules should stay reusable (branching conventions, deployment, CI checks, etc.). Project-specific context should stay close to the project (this includes subfolders with their own AGENTS.md/CLAUDE.md). Technical controls like tool restrictions or ignore behavior should stay out of narrative guidance. We have since moved a lot of the repeated operational work to skills, and those skills know when to execute a certain script and why.

Skills have become the place where repeated workflow goes. Not product logic. Workflow. Planning, implementation checkpoints, code review, PR review comments, CI debugging, release prep, PR descriptions, and doc generation should not be tribal memory or a giant prompt pasted into every session.

This also changed shape over time. We started with [slash commands](https://docs.anthropic.com/en/docs/claude-code/slash-commands) because that was the fastest way to stop repeating ourselves. Then the useful pieces moved into skills so they were not trapped in one command surface. Now a lot of it lives in our [agent-skills-marketplace repo](https://github.com/DiversioTeam/agent-skills-marketplace), and the newer [Pi dev-workflow extension](https://engineering.diversio.com/pi/dev-workflow/) is just the next version of the same idea.

These might sound boring because they sometimes require telling the LLM about things here and there, but the upsides are much higher. It also works naturally for humans. Dense documentation with everything dumped into it is hard for us to follow too; a clean split between shared standards and project-specific setup is easier for humans to maintain and easier for models to use effectively.

The split we try to preserve looks roughly like this:

<figure>
  <img
    src="{static}/images/articles/how-we-use-ai-like-engineers/context-belongs-in-different-places.svg"
    alt="Diagram showing that shared standards, project docs, and skills or controls belong in different places instead of being mixed together."
    style="width:100%;height:auto;display:block;"
  />
  <figcaption>Shared standards, project docs, and operational controls should not be mixed together.</figcaption>
</figure>

## The workflow still has to hold up

For a workflow to hold up, it needs to have very clear and specific guidelines for that workflow and these should be very easy to review and maintain for humans.

A big feature is still broken down into smaller releases and stacked PRs as much as possible. We really believe and take pride in building systems that do not keep us up at night at 3AM, late heroics when a bug is identified (worse if identified by a client) and solved are much less appreciated.

Any bug identified is still first proven by adding that missing test that did not catch it earlier and then the fix is implemented to make the test pass. This practice has worked really well for us the last 8 years.

Anything that touches the core of our system and has direct implications for our clients is still thoroughly tested manually on external sandboxes with production-like data to give us extra confirmation that we are not relying solely on automated tests. This often also includes testing non-happy-path flows.

It's very easy to waste time asking AI for too much at once. The output can look productive for a bit because it has generated a lot of text, but now we have to pay in engineer time to validate the draft and ensure the intent is spot on.

Hence, our focus nowadays is heavily on narrower and more practical planning and that is made possible by faster context recovery, smaller drafts, quicker iteration cycle when something looks off.

## What still stays human

Some work should stay obviously human.

If the change touches existing data, authorization, or production infrastructure, someone has to reason about it and test it first in environments where we are fine experimenting. AI's assistance is helpful, but we cannot trust it with everything. One example for us is that we build a lot of internal tools for our team, and it is easy for AI to confuse those with client-facing features, so we need to steer it back in the right direction when that happens.

This applies to architecture as well. Difficult calls around coupling, isolation, and long-term maintenance belong to engineers because they understand the wider system, know about upcoming business decisions, and are the ones who will have to live with the consequences. A simple example of this was when we were building SMS-based pulse surveys. We really wanted a backend like Django's local console email backend that would let us test SMS without ever sending a real message, but the configuration still needed to be plug-and-play so the functionality stayed the same for our team. An LLM cannot plan for that, nor can you write it once in your AGENTS.md and assume it will do it correctly for each feature.

Final approval stays human too. Anything we ship is the engineer's responsibility at the end of the day. Saying the LLM missed it does not work for us, and it will not work for our clients either.

This boundary matters more than any model benchmark:

<figure>
  <img
    src="{static}/images/articles/how-we-use-ai-like-engineers/ai-accelerates-humans-own-risk.svg"
    alt="Diagram showing that AI accelerates drafting and context recovery while humans keep responsibility for risk, architecture, and final approval."
    style="width:100%;height:auto;display:block;"
  />
  <figcaption>AI can accelerate drafting, but risk, architecture, and approval still stay human.</figcaption>
</figure>

## Evaluating AI like infrastructure

There is a second layer to this beyond coding workflow: choosing the right AI stack.

What I have found useful about these systems is thinking about them the way we think about infrastructure. While the model is definitely important, the surrounding ecosystem matters a lot as well.

The things I care about:

- developer experience (DX)
- how well the ecosystem is supported across the world
- how easy it is to onboard engineers to it (is it too overwhelming?)
- how easily engineers can build on top of it
- what it changes about data handling and compliance
- what this decision will cost over time, not just in a demo. The cost is both engineer time and company cost.

DX is a big deal for me, more than the model itself.

None of this has been a straight line. Before any of this felt structured, a lot of it was just copying and pasting code and plans out of [ChatGPT](https://chatgpt.com/) and [Claude](https://claude.ai/). Then came [GitHub Copilot](https://github.com/features/copilot) in 2024, mostly autocomplete and comment-driven code generation in VS Code. Then came agentic IDEs, mostly VS Code, while some of us were trying [Cursor](https://cursor.com/) as well. Later, VS Code got agent mode too. We jumped onto [Claude Code](https://www.anthropic.com/claude-code) very early because it fit the repo-exploration style better. Now the stack is more mixed and we are fine with that.

This does not mean we have not made mistakes. We have tried a lot of different things, but thanks to the team we were able to switch away from them when we realized something was not working for us. The important part is that the workflow is not tightly coupled to that tool history. The tools changed. The durable part stayed the same: repo instructions, skills, scripts, tests, review gates, and human habits. A recent example for us was moving a lot of the Claude Code-specific workflow into [Codex CLI](https://github.com/openai/codex) and [Pi](https://pi.dev/) within a week, without throwing away that layer.

<figure>
  <img
    src="{static}/images/articles/how-we-use-ai-like-engineers/tool-history-vs-durable-workflow.svg"
    alt="Diagram comparing tool history to a durable workflow layer."
    style="width:100%;height:auto;display:block;"
  />
  <figcaption>The workflow is not tightly coupled to the tool history.</figcaption>
</figure>

## What changed for us

- We now recover context much faster and avoid the dumb zone.
- We turn repeated friction into instructions, tools, or guardrails more often. The goal is to always spend less time on low-leverage repetition and more time on design, review, and testing.

A lot of that progress came from engineers comparing notes ([`/insights` in CLAUDE.md](https://x.com/trq212/status/2019173731042750509) was helpful, and we also started doing monthly [code review discussions](https://engineering.diversio.com/docs/code-review-digest-writer/) to avoid common and repeated mistakes), tightening instructions, and writing down what actually worked. The primary reason for our success with these systems, though, is our team (and this includes all teams across Diversio), who have kept feeding their learning back into it.

## The part that matters most

AI acts as a force multiplier when it sits on top of a culture with strong engineering habits. The fact that we had already built that culture well before LLMs were a thing has worked in our favour.

If you're wondering where to start to make the most of it with your own team, start by working on planning, scoping, instructions, code-quality and testing guardrails, and review loops. Build systems and workflows that can be maintained and owned by the whole team, and spend less time on model comparison.

## Related reading

- [The Monolith That Made AI Actually Useful](/the-monolith-that-made-ai-actually-useful.html)
- [No Code by Hand](/no-code-by-hand-agentic-platform-acceleration.html)
- [Postman to Bruno: A Weekend Migration That Transformed Our API Workflow](/from-postman-to-bruno-how-ai-changed-our-api-workflow.html)

<div class="article-subtext article-subtext--review">
  <p class="article-subtext-label">Review</p>
  <p>Thanks to <a href="https://www.linkedin.com/in/ashishsiwal/">Ashish Siwal</a> and <a href="https://www.linkedin.com/in/umanga-bhattarai-579b68158/">Umanga Bhattarai</a> for reviewing this post.</p>
</div>

<div class="article-subtext article-subtext--ai">
  <p class="article-subtext-label">AI writing disclaimer</p>
  <ul>
    <li>The article was verified for typos and basic grammatical mistakes using Codex 5.4.</li>
    <li>The references to our existing blog posts were included with the help of Codex 5.4 (we left comments for it).</li>
    <li>The SVGs were generated using Codex 5.4 and Excalidraw MCP.</li>
  </ul>
</div>
