Title: <del>No Code</del> by Hand
Date: 2026-02-28
Modified: 2026-02-28
Status: published
Category: Engineering
Tags: ai, agentic-engineering, ci-cd, developer-experience, platform-engineering, team-learning, security, testing, workflow
Slug: no-code-by-hand-agentic-platform-acceleration
Authors: Ashwini Chaudhary
Summary: CI dropped from 37 minutes to 9, at 35% lower cost. What we learned about mixing Claude and Codex, clearing the hidden queue, and where the real multiplier came from.

*CI dropped from 37 minutes to 9, at 35% lower cost. Here is what we learned about the hidden queue, mixing Claude and Codex, and where the real multiplier came from.*

---

## The hidden queue

Every engineering team has a version of this story.

Your roadmap looks healthy. Feature velocity looks fine. Sprint retros are tolerable. But your engineers are still losing chunks of every day to things that were never planned: waiting 16 minutes for CI to tell them a typo failed linting. Manually running six database commands because the snapshot process lives in someone's Slack history. Bumping a dependency because Dependabot fired another alert at 3pm on a Friday.

That is the hidden queue. It is not on your roadmap, it is not in your sprints, and it is costing you more than most feature work.

Most teams do not ignore this queue on purpose. It just keeps losing in prioritization because each item feels small in isolation. "Fix the flaky test" is never going to beat "Ship the dashboard redesign" in a planning meeting. But those small items compound. A 16-minute CI wait happens 20 times a day across 5 engineers, and that adds up to over 26 hours of dead time per week - time where nobody is building anything or even thinking about the problem, just staring at a spinner.

Late last year, we changed one rule: **if something keeps burning team time, it is roadmap work** - not "tech debt we'll get to someday," but prioritized work with owners and metrics.

In the 90-day window from **December 1, 2025** through **February 28, 2026**, that rule turned into **57 major non-product changesets** across backend, frontend, and monolith tooling repos: **56 major PRs and 1 major direct commit**, touching **1,303 files** with **120,929 additions** and **31,170 deletions**.

<figure>
  <img src="{static}/images/articles/no-code-by-hand/changeset-mix.svg" alt="Bar chart showing major non-product changesets by repo type: backend, frontend, monolith, and direct commits.">
  <figcaption>Non-product engineering changesets in the 90-day window, broken down by repo type.</figcaption>
</figure>

The point of those numbers is that a whole class of work moved from "someday" to "done" - and we did it without pausing product delivery.

---

## What we shipped this quarter

Here is the breadth of what moved in those 90 days, all in parallel:

- **CI architecture** - Rewired how we decide what checks to run, when, and at what cost
- **Testing platform** - Built E2E and integration test coverage in phases, replaced flaky waits with deterministic ones
- **Local development** - Made git worktrees reliable so agents and engineers can run multiple branches in parallel without collisions
- **Operations safety** - Took processes that lived in people's heads (snapshots, support shells, admin actions) and gave them proper guardrails and audit trails
- **Security remediation** - Closed CVEs and Dependabot alerts in planned waves instead of random fire-drills
- **Debt retirement** - Squashed tangled migration graphs, removed dead Slack/Teams integrations
- **Open-source skills** - Turned repeating engineering patterns into reusable agent skills and open-sourced them

<figure>
  <img src="{static}/images/articles/no-code-by-hand/workstream-coverage.svg" alt="Horizontal bar chart showing major non-product changesets split across multiple workstreams.">
  <figcaption>CI was one stream inside a much broader platform quarter.</figcaption>
</figure>

Most teams can point to one thing they improved. "We made CI faster." "We added more tests." Seven high-friction systems in parallel while keeping review quality, rollback safety, and product delivery intact is a different kind of claim. So the obvious question is: how?

---

## Why this was possible now and not a year ago

[Karpathy put it bluntly](https://x.com/karpathy/status/2026731645169185220): coding agents basically did not work before December 2025, and they basically work now. He described giving an agent a full system setup task - SSH keys, vLLM, web dashboard, systemd services - and it came back 30 minutes later with everything working. He did not touch anything.

That matched what we were seeing. As recently as October 2025, the same tools felt like expensive autocomplete. By December, a new generation of models had shipped and changed that completely. [Mitchell Hashimoto](https://mitchellh.com/writing/my-ai-adoption-journey) went through the same arc - from skeptic to building his entire Ghostty workflow around agents, with the key insight that you have to separate planning from execution and let the agent self-correct. [Paul Graham](https://x.com/paulg/status/2022604692178522562) framed the implication: "In the AI age, taste will become even more important. When anyone can make anything, the big differentiator is what you choose to make." [Simon Willison](https://simonwillison.net/guides/agentic-engineering-patterns/hoard-things-you-know-how-to-do/) figured out the compounding angle: "Coding agents mean we only ever need to figure out a useful trick once."

They were all talking about the same shift from different angles, but none of them say loudly enough what actually caused it: **the models got qualitatively better.**

Claude Opus 4.5, Opus 4.6, Codex 5.2, Codex 5.3 - these are not incremental improvements. They can hold entire systems in context, reason about architectural tradeoffs, catch multi-tenant security patterns, and produce code that is reviewable on the first pass. That kind of jump is what made No Code by Hand our default working mode since December.

Our team learned the differences through daily use, not benchmarks. We got opinionated fast, and our honest assessment does not look like any vendor's marketing page:

**Claude models** (Opus 4.5, Opus 4.6, Sonnet) are our workhorse for execution. They are fast - genuinely fast, even at high thinking levels. They are great at quick fixes, running skills that require less deliberation, verifying and formatting large numbers of files, and chewing through well-scoped tasks at speed. The [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python) (available in both Python and TypeScript) is mature and well-designed - it gives you the full agent runtime with tools, subagent orchestration, MCP support, and granular permissions out of the box. If you are building custom workflows, that SDK matters a lot.

The tradeoff: Claude models can be eager. They will take shortcuts on medium to large features, skip files, and miss critical business logic if you are not watching. They also consume tokens fast - you can burn through a significant budget in a short session. You get results quickly, but you end up verifying more.

**Codex models** (Codex 5.2, Codex 5.3) are where we go for depth. Planning, architectural reasoning, thorough code review, anything where you need the model to actually think through the full problem before writing code. Execution is slower, but the output is more satisfying - it will not skip critical business logic or take shortcuts the way Claude sometimes does. It respects the complexity of what you are asking it to do.

The tradeoff: Codex is weaker with tool use compared to Claude models. The SDK story is thinner - there is a [Codex SDK](https://developers.openai.com/codex/sdk/) (TypeScript only), but it is an orchestration wrapper for controlling a local Codex agent, not a general-purpose agent-building runtime like Claude's. No Python equivalent. Token limits, on the other hand, are very hard to hit - you can run long, deep sessions without worrying about context exhaustion.

**In practice, we mix both.** A lot of our best work comes from running Claude and Codex together, or multiple instances of the same model, each with a clean context scoped to a specific piece of the problem. One model plans while another executes, or one reviews what the other wrote. We split large tasks across separate sessions so no single context gets polluted with too much state.

With Codex specifically, we use **steer mode** and **queue mode** very tactically depending on the task:

- **Steer mode for ambiguous work.** Anything that involves architectural decisions, multi-tenant security logic, or unfamiliar parts of the codebase - we steer. Example: when building the admin safety model (the system that prevents admins from locking themselves out), we started Codex in steer mode, pointed it at the permission hierarchy, course-corrected twice when it tried to flatten the role graph, and guided it through the edge cases where a superadmin demotes themselves. The final implementation was clean because we were in the loop at every decision point instead of reviewing a finished mess.
- **Queue mode for well-scoped, parallelizable work.** When the task is clear and the scope is bounded, queue mode lets us fire off multiple Codex tasks and review them as they land. Example: during the CI migration, we queued separate tasks for each workflow file rewrite - linting pipeline, test matrix, deployment gates - each with its own clean context. Five tasks running in parallel, each one scoped tightly enough that the model did not need steering.
- **The tactical switch.** We start most sessions in steer mode. If the first few interactions show the model understands the problem and the scope is narrowing, we switch to queue mode and let it run. If it starts drifting, we pull it back to steer. We re-evaluate steer vs queue mode throughout the session based on drift, clarity, and risk.

Picking the right model for the right task - and knowing when to combine them - is itself a skill that takes time to develop, and teams that treat all models as interchangeable are missing most of the value.

**The biggest shift is how these models want to be used.** Earlier generations worked best when you gave them a prompt and left them alone. The current generation is different - they are built for interactive steering. You set direction, check in as it works, course-correct when it drifts, and guide it through the ambiguous parts rather than hoping it guesses right. OpenAI made this explicit with [Codex 5.3](https://openai.com/index/introducing-gpt-5-3-codex/): steer mode - where you interact with the model while it works without losing context - shipped as a [stable feature](https://github.com/openai/codex/pull/10690), enabled by default. Anthropic's [Claude Opus 4.6](https://www.anthropic.com/news/claude-opus-4-6) moved in the same direction with adaptive thinking, where the model adjusts its reasoning depth based on what you are asking and responds to mid-turn guidance.

This matters more than it sounds. [AmpCode put it well](https://ampcode.com/news/gpt-5.3-codex): "the agent is no longer the bottleneck. Our ability to tell it what to do is." A year ago the workflow was write a prompt, wait, review what comes back. Now it is closer to pair programming - you stay in the loop, steer the model toward the right answer as it works, and course-correct in real time rather than filtering through wrong answers afterward. Teams that still treat agents as black boxes they throw tasks at are working against how these models are actually designed.

Our team has taken this to its logical conclusion: we have pretty much ditched our IDEs entirely. We work strictly in terminals - Claude Code, Codex CLI, git, and shell scripts. The models are better at navigating codebases than any file tree sidebar ever was, and the terminal is where steering actually happens - no GUI layer sitting between you and the agent. [Karpathy put it bluntly](https://the-decoder.com/andrej-karpathy-says-programming-is-unrecognizable-now-that-ai-agents-actually-work/): "You're not typing computer code into an editor like the way things were since computers were invented. That era is over." What replaced it is spinning up agents, giving them tasks in English, and managing their work in parallel - but with what he calls "high-level direction, judgement, taste, oversight, iteration, and hints and ideas." That is steering, not autopilot.

None of this means the models write perfect code or replace engineering judgment. What changed is how cheap it became to try something, evaluate it, and try again. When a rewrite takes 20 minutes instead of a day, you can try three approaches and pick the best one. You can afford to be thorough instead of cutting corners because iteration itself got cheap.

That context matters for everything that follows. The hidden queue shrank because each iteration got about 10x cheaper, so we could clear items that used to stay deferred. So we started with the one system where we could prove it.

---

## CI: the system we could actually measure

We started with CI because it was the one system where we had clean telemetry and clear before/after boundaries. You can argue about whether a refactor "improved code quality." You cannot argue about whether a workflow went from 942 seconds to 675 seconds. The numbers are right there.

### The real problem was architectural

Before the redesign, our CI pipeline had a fundamental coupling problem. One heavy workflow path tried to answer two completely different questions at the same time:

1. *Should expensive checks even run on this change?* (A typo in a README does not need database-level integration tests.)
2. *Is this change safe to ship?* (A migration change absolutely does.)

When those two questions are coupled, you get the worst of both worlds. Low-risk changes overpay - a CSS fix waits 16 minutes for checks it does not need. High-risk changes wait behind noise - a database migration sits in the same queue as a copy change.

### What we actually changed

The fix was separating qualification from execution - figuring out which checks should run before actually running them:

- **Fast checks moved earlier.** Linting, type checking, import validation, and test placement checks all moved into a GitHub Actions workflow that runs in under 45 seconds. If these fail, nothing downstream even starts.
- **Scope classification.** A file-change classifier now evaluates every PR: does this change touch backend code? Database schemas? Frontend only? Docs only? Changes that are irrelevant to deep checks skip them entirely.
- **Content-aware caching.** Instead of time-based cache invalidation, caches are now keyed on actual content hashes. Same code = same cache, regardless of when you last ran.
- **Runtime image optimization.** The CircleCI runtime image was rebuilt to eliminate bootstrap overhead - the time between "job starts" and "your code actually runs."

### The numbers

On the heavy path (CircleCI test-and-check workflow), the broad pre/post window around the runtime-image milestone gave the strongest signal:

- **Median workflow wall time**: 942.5s → 675.0s, a **28.4% reduction** (`n=218` before, `n=149` after)
- **Deepest check lane** (Deep DB/RLS checks): 332.0s → 95.5s, a **71.2% reduction**

<figure>
  <img src="{static}/images/articles/no-code-by-hand/ci-heavy-lane-pre-post.svg" alt="Bar chart comparing heavy CI workflow median runtime before and after the runtime image shift.">
  <figcaption>Heavy validation median runtime: 942.5s → 675.0s, a 28.4% reduction.</figcaption>
</figure>

Those are the headline numbers, but they are only half the story - because the first win came with an uncomfortable tradeoff.

---

## Why we kept going after the first win

After the first round of CI improvements, we had an intermediate phase where runtime improved but credit consumption actually got *worse*. We were running more things in parallel, which made the wall clock faster, but the total compute bill went up.

Most blog posts would stop here, post the runtime chart, and declare victory. We did not, and honestly this next part matters more than the numbers above.

We kept running the loop: **hypothesis → implementation → measurement → tradeoff review → tune or rollback → standardize**. That loop is where cheap correction cycles made the real difference. When rewriting a CI configuration takes 20 minutes instead of a day, you can afford to try three approaches and pick the best one.

### Three phases of tradeoff

The three-phase view shows the full path, including the uncomfortable middle:

- **Baseline**: 37.91 min critical path, 359 mean credits per paired run
- **Parallel phase**: 10.63 min critical path (great!), 456 credits (worse - more parallel jobs)
- **Current phase**: 9.08 min critical path, 232 credits (both better than baseline)

Relative to baseline, the current mode is **76% faster** and **35% cheaper**. The current sample in this phase comparison is still early (`n=6`), so we treat it as directional and use the larger pre/post windows for stronger claims.

<figure>
  <img src="{static}/images/articles/no-code-by-hand/ci-three-phases-runtime-credits.svg" alt="Two-panel chart comparing critical-path runtime and combined credits across baseline, parallel, and current CI phases.">
  <figcaption>Three CI phases: faster runtime and lower compute cost in the current mode.</figcaption>
</figure>

### Modeled time savings

The waiting-time model across this window estimates **21.39 hours** of developer waiting time recovered, broken into three categories:

- **11.07h** from faster heavy lanes (every CI run finishes sooner)
- **6.38h** from early-stop on failed fast checks (if linting fails in 30 seconds, you do not wait 15 minutes for full tests to also fail)
- **3.94h** from skipping irrelevant deep runs (a docs-only change skips database checks entirely)

This is a model, not direct causal proof. But 21 hours of waiting time eliminated over a few weeks is a meaningful quality-of-life improvement for a small team.

<figure>
  <img src="{static}/images/articles/no-code-by-hand/ci-waiting-time-model.svg" alt="Stacked bar chart showing modeled waiting-time reductions from three CI improvements.">
  <figcaption>Modeled waiting-time reduction: 21.39 hours across three improvement categories.</figcaption>
</figure>

---

## Every CI job, not just the workflow

The workflow-level numbers tell one story. The job-level numbers tell a more interesting one.

The "Deep DB/RLS checks" job - the single most expensive check in our pipeline, the one that spins up a full database and runs row-level security validations - went from **332s to 95.5s**. That is a **71% reduction** on the job that matters most for safety confidence.

<figure>
  <img src="{static}/images/articles/no-code-by-hand/ci-deep-check-lane.svg" alt="Paired horizontal bars showing before/after runtimes for each CI job.">
  <figcaption>Job-level improvements after the runtime image shift. The deepest check lane dropped 71%.</figcaption>
</figure>

That improvement came primarily from the runtime image rebuild. The old image was doing expensive setup work (installing system packages, configuring database connections, bootstrapping test fixtures) on every single run. The new image bakes all of that into the image layer, so the job starts with everything already in place.

It sounds boring, but it changes daily life. At 5.5 minutes you context-switch to something else and lose focus. At 1.5 minutes you just wait for it and stay in the flow. And then we looked at the trigger configuration and found something we should have caught months ago.

---

## We were running the same checks twice

Here is a problem that is embarrassingly common and embarrassingly wasteful: GitHub fires both a `push` event and a `pull_request` event when you push to a branch with an open PR. If your CI triggers on both, you run the same checks twice on the same code.

Before we fixed this, the ratio was absurd: **399 push-triggered runs** vs **22 PR-triggered runs** on non-deploy branches. An 18:1 ratio of redundant work.

After dedup (`#2713`): **9 push runs** vs **36 PR runs**. A 0.25:1 ratio. Only meaningful work runs.

<figure>
  <img src="{static}/images/articles/no-code-by-hand/ci-dedup-effect.svg" alt="Before and after comparison of push vs PR triggered CI runs showing dramatic reduction in redundant runs.">
  <figcaption>Before dedup: 18x more push runs than PR runs. After: only meaningful runs execute.</figcaption>
</figure>

A few hours of investigation, hundreds of compute-hours saved over a quarter. And it is exactly the kind of thing that never gets prioritized because "CI is working fine" - as long as nobody looks at the bill.

With CI finally fast and honest, we could tackle the thing it depends on most: whether the tests themselves were worth trusting.

---

## The test suite we could not trust

The testing work this quarter was about building a testing *system* that could be trusted by default and maintained without heroics, not just adding more test files.

### Why phased rollout matters

The most common failure mode for test initiatives is the big-bang rewrite: someone decides "we need 80% coverage," writes hundreds of tests in a week, and three months later half of them are flaky, ignored, or commented out. We did the opposite.

<figure>
  <img src="{static}/images/articles/no-code-by-hand/testing-platform-phases.svg" alt="Phased testing platform diagram showing progression from infrastructure to deterministic stabilization.">
  <figcaption>Testing rolled out in phases instead of one risky rewrite.</figcaption>
</figure>

The sequence:

1. **Infrastructure first.** Test runner configuration, fixture management, database seeding, environment isolation - the kind of work nobody wants to do but everything else depends on.
2. **Role-based E2E flows.** Tests organized by user role - HR admin, manager, employee - because that is how our permission model works. Testing by role catches the bugs that actually happen in production: "this works for admins but breaks for regular users."
3. **Unit and integration depth.** Once the E2E skeleton was stable, we filled in unit and integration tests underneath. The E2E tests act as a safety net while you add lower-level coverage.
4. **Deterministic stabilization.** The final phase was eliminating flakiness. And that brings us to one of the most universally hated problems in software engineering.

### The `sleep(2000)` problem

If you have ever maintained E2E tests, you know this pain intimately. The test clicks a button, then waits. How long should it wait?

```javascript
// This is a guess
await page.click('#submit');
await sleep(2000);
expect(page.url()).toBe('/dashboard');
```

Two seconds works on your laptop. It fails on CI because the server is slower. You bump it to 3 seconds. Now the test passes but the suite takes 40 minutes. Someone adds `sleep(5000)` "just to be safe." Now it takes an hour. And it still flakes on Mondays when the CI machines are loaded.

The fix is simple to explain and tedious to actually do: go through every test and replace fixed waits with waits that check whether the thing actually happened.

```javascript
// This is an assertion about behavior
await page.click('#submit');
await page.waitForURL('/dashboard');
```

The second version waits exactly as long as needed - 200ms on a fast run, 3 seconds on a slow one - and fails immediately with a clear error if the URL never changes. That one shift improved reliability, review trust, and debugging speed because failures started telling you what actually went wrong instead of "timeout after 5000ms."

A few of the replaced waits started failing consistently rather than flaking - which turned out to be a gift, because the generous sleeps had been hiding genuine performance issues in the application. Fixing the tests ended up fixing the app.

None of that would have mattered, though, if the environment running those tests kept colliding with itself.

---

## Why two agents could not run at the same time

If you are doing agentic coding seriously, Worktrees are the base layer for agentic coding; without isolated checkouts, parallel execution breaks down.

An AI coding agent needs its own isolated checkout to work in. It cannot share your working directory - it would stomp on your files, your running servers, your local state. Git worktrees solve this cleanly: each worktree is a separate working copy of the repo with its own branch, its own file state, and its own index. You can have an agent working on a refactor in one worktree while you are reviewing a PR in another and a second agent is writing tests in a third.

But worktrees only deliver that promise if your local development setup is worktree-aware. Ours was not. And until we fixed it, every other improvement in this post would have been bottlenecked by a broken local environment.

### What was actually breaking

Every worktree tries to spin up its own local dev environment. Without isolation, that means:

- Branch A starts Docker with the default port mapping: `localhost:8000` for the API, `localhost:3000` for the frontend.
- An agent opens a worktree for Branch B. It also wants `localhost:8000` and `localhost:3000`.
- Port collision. One of them fails silently or grabs a random port. The agent's frontend is now talking to your backend running different code. Or your server crashes because the port is taken. Either way, someone wastes 20 minutes debugging a port-conflict issue that looks like an app bug and burns 20 minutes of debugging.
- Meanwhile, Branch A's `.env` file says `API_URL=http://localhost:8000`. Branch B's `.env` says the same thing. The frontend in one worktree makes API calls to a server that is running code from a completely different branch.

This blocked the entire agentic workflow. If worktrees are unreliable, agents cannot work in parallel, and the speed advantage you are counting on just collapses.

<figure>
  <img src="{static}/images/articles/no-code-by-hand/local-dev-isolation.svg" alt="Before and after diagram of local development showing worktree port collisions replaced by deterministic port isolation.">
  <figcaption>Before: shared ports collide across worktrees. After: deterministic isolation per worktree.</figcaption>
</figure>

### The fix

The primary checkout behaves exactly like before - same ports, same config, no surprises for the human developer. But every non-primary worktree gets **deterministic port isolation**: ports are derived from the worktree path, so they are stable (the same worktree always gets the same ports) and unique (no two worktrees ever collide).

We added root-level wrappers - `just up`, `just down`, `just sync-api-env` - so that starting, stopping, and syncing environment state became a single predictable command regardless of which worktree you are in. The frontend environment file automatically picks up the correct backend URL for whichever worktree is running. An agent can `just up` in its worktree and get a fully working, fully isolated local environment without any human intervention.

This unlocked everything else. Once worktrees were reliable, we could run multiple agents in parallel on different tasks, each with its own branch, its own server, its own test environment. Most of the speedup came from running three or four agents in parallel without collisions.

But that speed advantage hits a wall the first time one of those agents needs to run a database snapshot.

---

## Operations: when the process lives in someone's head

Every engineering team has critical processes that work perfectly as long as the right person is online and remembers the exact sequence of commands - which is really just a single point of failure wearing a human costume.

This quarter we found three of these in our own stack and rebuilt them.

### Database snapshots

Before: creating a database snapshot for a customer or for staging required running six commands in exact order. Dump the SQL. Package it. Upload to the right bucket. Restore on the target. Create the snapshot record. Notify the team in Slack. Miss a step and you get a corrupt snapshot. Run them out of order and you overwrite something. The whole process lived in one engineer's head and a Slack message from eight months ago.

<figure>
  <img src="{static}/images/articles/no-code-by-hand/snapshot-automation.svg" alt="Before: 6 manual steps in a chain. After: one command with built-in error handling.">
  <figcaption>Snapshot creation went from 6 manual steps to one command with preflight checks and Slack notification.</figcaption>
</figure>

After: `./manage.sh snapshot create`. One command. It runs preflight checks (is the source database accessible? Is there enough disk space?), executes the full pipeline with error handling at every step, and posts a Slack notification when it is done or if it fails. Any engineer can run it. No tribal knowledge required.

### Admin actions

Before: high-impact admin actions (think: merging two user accounts, resetting organization data, modifying subscription state) were one-click operations with no confirmation step. Click the button, the mutation happens immediately, no undo. One accidental click on the wrong row in a moment of pressure = irreversible data loss.

<figure>
  <img src="{static}/images/articles/no-code-by-hand/admin-safety-model.svg" alt="Before: click and pray. After: plan, confirm, execute with eligibility checks.">
  <figcaption>Admin actions moved from one-click mutations to a plan → confirm → execute model with eligibility checks.</figcaption>
</figure>

After: high-impact actions follow a three-step model. First, **review the impact** - the system shows you exactly what will change and who is affected. Second, **confirm the scope** - you explicitly acknowledge what you are about to do. Third, **execute** - only after passing eligibility checks and risk assessment. Going from "click and pray" to "plan, confirm, execute" is how you turn potential incidents into boring Tuesdays.

### Support shell workflows

Support shells - the tools your team uses to diagnose and fix customer issues in production - got a significant upgrade. Instead of an engineer manually running queries and eyeballing results, the shell now surfaces relevant context, suggests likely fixes, and handles the common reconciliation patterns automatically. The shell keeps engineering judgment in the loop while shortening the path from incident report to root-cause diagnosis.

<figure>
  <img src="{static}/images/articles/no-code-by-hand/ops-safety-surfaces.svg" alt="Grid showing operational surfaces moved from person-dependent choreography to guarded control planes.">
  <figcaption>Operations power paths rebuilt as safer, repeatable, auditable surfaces.</figcaption>
</figure>

There is no product launch here and nobody is going to tweet about it, but this is the work that keeps incidents smaller, response times tighter, and makes sure the process still works when the person who "knows how snapshots work" is on vacation. It also removed the last excuse for not touching the security backlog.

---

## Security: from random interrupts to planned waves

Here is how security and dependency work usually goes: Dependabot opens an alert. Someone sees it, maybe today, maybe next week. They bump the version, run the tests, fix whatever breaks, open a PR. It gets reviewed between other work. Meanwhile three more alerts have fired. The PRs conflict with each other. Merge churn increases. Review quality drops because everyone is context-switching.

We replaced that pattern with a **wave-based remediation model**:

- **Wave 1**: Patch-level security updates. Django, Pillow, SimpleJWT, pyasn1. Low-risk, high-confidence bumps.
- **Wave 2**: Cryptography chain. `cryptography` and `weasyprint` updates that cascade through the dependency tree. Medium risk, needs careful testing.
- **Wave 3**: Deep transitive dependencies. Refreshing the protobuf chain through Google's dependency graph. Higher complexity, so we isolated it into its own review cycle.

<figure>
  <img src="{static}/images/articles/no-code-by-hand/security-dependabot-program.svg" alt="Layered security remediation diagram showing staged dependency waves, workflow hardening, and release-integrated closure checks.">
  <figcaption>Security moved from reactive interrupts to a layered, wave-based remediation program.</figcaption>
</figure>

The security work went beyond dependency bumping. In the same window, we also:

- **Hardened CI input handling.** GitHub Actions workflows can receive untrusted input from PR titles, branch names, and commit messages. If those inputs flow unsanitized into shell commands, that is a command injection vulnerability *in your CI pipeline*. We audited and hardened those paths.
- **Reduced PII exposure in telemetry.** Logging and error tracking payloads were carrying more personally identifiable information than they needed to. We scrubbed those payloads down to what is actually useful for debugging without exposing user data.

The practical result is that security and dependency work stopped being an interrupt. We close issues faster, in planned batches with proper review scope, and the rest of the team can actually plan their week without random fire-drills derailing it.

The security waves also forced us to confront what we had been putting off: the migration graph and a pile of dead integration code that had been making every other change harder than it needed to be.

---

## Debt: the art of safe subtraction

Deleting code is easy. Deleting the *right* code without breaking something in production takes a lot more care.

### Migration topology

Our Django migration graph had accumulated cruft over time - the way they always do. Branches, merges, dependencies that used to make sense but now just add confusion. New developers would look at the migration graph and have no idea what was load-bearing and what was historical accident.

<figure>
  <img src="{static}/images/articles/no-code-by-hand/migration-squash.svg" alt="Before: tangled migration graph with cross-dependencies. After: clean, linear migration chain.">
  <figcaption>Migration topology simplified from a tangled graph to clean lineage.</figcaption>
</figure>

We used a two-step squash strategy:

1. **Introduce replacement lineage.** New squashed migrations replace the old chain, but the old migrations stay around for compatibility. Both paths work.
2. **Archive and prune.** Once the new lineage is stable and deployed, remove the old chain. The graph is clean.

This approach respects the reality that migrations are one of the scariest parts of a Django application. You do not yolo a migration squash. You prove the new path works while the old path is still available as a fallback.

### Dead integration code

We also retired deprecated Slack and Teams integration paths - but only after proving they were genuinely unused or had working replacements. "Dead" integration code is never truly dead. It still shows up in code reviews ("is this still used?"), expands the upgrade surface ("this import broke after the SDK update"), and confuses new contributors ("should I be using this API or the other one?").

Removing it deliberately - with evidence that nothing was actually using it - means every future engineer who touches that part of the codebase has one less thing to be confused about.

By this point we had noticed a pattern: the cleanup workflows, the review checklists, the remediation sequences - we kept solving similar problems the same way. Why were we still rebuilding them from scratch each time?

---

## The biggest multiplier was not a model

If I had to pick the single biggest multiplier from this quarter, it would be this section, and it connects directly to why model selection matters.

Here is what kept happening: an engineer figures out a really effective way to use Opus for a thorough code review, or they discover that Codex handles Dependabot triage perfectly if you give it the right structure. It works great for them. Then it lives in their head, or in a DM, or in a prompt they copy-paste from a notes app. That is useful for one person, but it does not spread.

We took a different approach: we turned those patterns into reusable agent skills and commands, and open-sourced the whole layer in [DiversioTeam/agent-skills-marketplace](https://github.com/DiversioTeam/agent-skills-marketplace). Right now that repo includes **15 plugins, 17 skills, and 37 commands** covering:

- **Code review** - Hyper-pedantic Django review skills that check for multi-tenant safety, migration correctness, and security patterns
- **Commit and PR hygiene** - Atomic commit helpers that enforce pre-commit hooks, lint gates, and clean commit messages
- **Dependabot remediation** - Wave-based triage and execution for both frontend and backend dependency management
- **Release operations** - PR creation, version bumping, merge conflict resolution, and release publishing
- **Docs generation** - Repository documentation, API docs from Bruno files, AGENTS.md canonical formats

<figure>
  <img src="{static}/images/articles/no-code-by-hand/skills-compounding-flywheel.svg" alt="Compounding flywheel diagram for open-source skills: pattern discovery, codification, team reuse, and baseline uplift.">
  <figcaption>Open-source skills turn individual technique into team-level memory.</figcaption>
</figure>

This is where [Simon Willison's insight](https://simonwillison.net/guides/agentic-engineering-patterns/hoard-things-you-know-how-to-do/) lands hardest: "Coding agents mean we only ever need to figure out a useful trick once." That is exactly what skills do. Someone figures out the best way to run a security audit with Opus. It becomes a skill. Now every engineer on the team runs security audits at that level, automatically.

Instead of "someone has a strong prompt in a DM," these became shared tools that anyone on the team can run, inspect, and improve. They live in version control with clear entry points, not in someone's clipboard.

This matters for two reasons:

1. **Reviews stop depending on who is doing them.** When every code review uses the same skill with the same guardrails, the floor rises. You stop getting thorough reviews from one person and surface-level reviews from another.
2. **Onboarding gets faster.** New engineers do not need to discover the team's workflow through osmosis. They install the skills and inherit months of accumulated process knowledge on day one.

This is why I keep saying agentic coding is an execution multiplier, but also a **learning multiplier**. The model's capability matters, but what decides whether gains stick across the team or disappear when one person goes on vacation is whether you have a skill system.

We are not the only ones who figured this out. The ecosystem is moving fast - [Anthropic ships official plugins for Claude Code](https://github.com/anthropics/claude-code/tree/main/plugins), [Vercel published a library of agent skills](https://github.com/vercel-labs/agent-skills/), and individual developers are releasing genuinely useful tools like [visual-explainer](https://github.com/nicobailon/visual-explainer) that solve problems we would have built ourselves. More and more companies and individuals are open-sourcing skills that slot right into existing agent workflows, and our team is actively pulling the best ones into how we work. The value of a skill system goes up the more people contribute to it - not just inside your team, but across the industry.

We did not see what the skills layer had actually done until we stepped back and looked at the quarter as a whole.

---

## How it all compounded

What makes this quarter more than a list of separate improvements is that the workstreams were not independent. They fed into each other, and each one made the next one easier to pull off.

<figure>
  <img src="{static}/images/articles/no-code-by-hand/reinforcement-system-map.svg" alt="System map showing how CI, testing, local development, ops safety, security, and skills codification reinforce each other.">
  <figcaption>Direct and indirect reinforcement loops across the quarter's workstreams.</figcaption>
</figure>

Here is how the loops worked:

- **CI speed → testing velocity.** Faster CI feedback meant testing improvements were cheaper to validate. You could iterate on a test three times in an hour instead of once.
- **Testing quality → CI signal.** Better tests with deterministic waits produced cleaner CI signal. Fewer flaky failures meant the CI results were actually trustworthy, which made scope-aware gating and cost optimization possible.
- **Worktree isolation → everything.** Reliable worktrees meant agents and engineers could iterate on every other stream in parallel without breaking each other's environments.
- **Skills codification → all of the above.** Once patterns were encoded into reusable skills, we stopped relearning the same lessons. New contributors inherited the workflow directly.

We did not just do many things in one quarter - we ended up building a system where the improvements reinforced each other. Better CI feedback made testing more productive, which made CI signal more trustworthy, which made it safe to skip unnecessary checks, which freed up time to codify the patterns, which meant the next improvement started from a higher baseline.

If you are looking at this and thinking "we have the same hidden queue," here is where to start.

---

## What you can actually copy

If you want to apply this without copying our stack, copy the mechanics:

1. **Make the hidden queue visible and measure it.** Track every time an engineer waits, context-switches, or does manual repetitive work for one week. Add up the hours. Then pick one loop, instrument it, fix it, and measure the before and after. Start wherever your data is cleanest.

2. **Separate qualification from execution.** In any expensive system - CI, deployments, data pipelines - cheap checks should decide whether expensive checks run. A 30-second linter should gate a 15-minute integration test, not run alongside it.

3. **Ship in phases, not big bangs.** Every improvement in this post was shipped incrementally. If Phase 2 breaks, you roll back Phase 2. Phase 1 still works.

4. **Make worktrees work.** If your team is using AI coding agents, fix your local dev setup first. Deterministic port isolation, environment syncing, single-command startup. Without this, you are bottlenecking every other improvement.

5. **Learn the models and mix them.** Claude is fast and great for execution but will take shortcuts on complex work. Codex is slower but more thorough. Run them together - one plans, one executes, one reviews.

6. **Turn prompts into skills.** When someone on your team figures out an effective AI-assisted workflow, do not let it stay in their head. Encode it. Version it. Share it. The gap between "one person is fast" and "the whole team is fast" is a skill system.

These patterns are general-purpose and work whether you are running a monolith, microservices, or something in between. The models make it cheaper to try things and iterate. The patterns are what make the results last.

---

## Attention is still the bottleneck

If you take one thing from this post, do not let it be "they wrote less code." We wrote and deleted a lot of code - 120,929 lines added, 31,170 deleted.

What changed is where we **spent our attention**.

The repetitive plumbing - CI configuration, test infrastructure, environment wiring, dependency management, snapshot steps - is now cheaper to do. That frees up the team to focus on boundaries, failure modes, control surfaces, and review quality.

We still write code and still need engineers; we are just spending more of that scarce attention on work that actually needs human judgment.
