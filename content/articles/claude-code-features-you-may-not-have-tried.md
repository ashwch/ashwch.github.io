Title: Claude Code features you may not have tried yet
Date: 2026-11-03
Modified: 2026-11-03
Category: Engineering
Tags: engineering, ai, developer-experience, workflow, claude-code, pi, agents
Slug: claude-code-features-you-may-not-have-tried
Authors: Ashwini Chaudhary
Summary: A few Claude Code features that have changed how we work at Diversio: letting Claude babysit things after a push, letting sessions talk to each other, moving workflows off people's laptops into cloud environments, and the built-in browser in the desktop app.

Most of the conversations I'm having about Claude Code are still about the model: which one is smarter, which one writes better code, which one is more token efficient, which one has higher tokens/s. Fair enough. But a lot of what has changed how we work at Diversio is in the harness around the model, and in the Claude Desktop and web apps, and I rarely see people using or mentioning those parts. We've moved around a fair bit ourselves: we [started with Claude Code](/the-monolith-that-made-ai-actually-useful.html), [mixed in Codex](/no-code-by-hand-agentic-platform-acceleration.html), [moved a lot of our workflow to Codex CLI and Pi](/how-we-use-ai-like-engineers.html), and [are now mostly back on Claude Code](/all-tools-should-now-have-two-users.html).

This post covers four of those parts: letting the agent babysit things after a push, letting sessions and subagents talk to each other, moving workflows that used to live on people's laptops into Claude Code's cloud environments, and the built-in browser in the desktop app, which has been really useful for the non-technical folks.

<figure><video src="{static}/images/articles/claude-code-features-you-may-not-have-tried/video/claude-features.mp4" poster="{static}/images/articles/claude-code-features-you-may-not-have-tried/video/claude-features.poster.jpg" controls playsinline preload="none" style="width:100%;height:auto;display:block;border-radius:12px"></video><figcaption>TL;Watch Video</figcaption></figure>

## Asking Claude to babysit for you

This one sounds small. Once I've pushed something, I ask Claude to keep watching it: has the review come in, did CI fail, are there conflicts with the base branch now, is the deployment done, are the various PRs in the GH stack up to date.

Claude is extremely good at spinning up these watches in the background while it keeps working on whatever else it was doing. When something happens, it comes back to life in the main thread. A failing test gets fixed, a review comment gets answered, a conflict gets rebased, all PRs in a stack are kept up to date, and when the deploy is out I get told. It doesn't spin in a polling loop eating context, and in most cases it doesn't break. It also works from subagents, so each one can watch its own thing.

<figure>
  <img
    src="{static}/images/articles/claude-code-features-you-may-not-have-tried/monitor-after-push.svg"
    alt="After a push, the agent starts background watches for review, CI, merge conflicts and deploys, keeps working, and only reacts when one of them reports something."
    style="width:100%;height:auto;display:block;"
  />
  <figcaption>What Claude keeps an eye on after I push a branch.</figcaption>
</figure>

Honestly, it felt so smooth that I wanted the same thing in the other tools we use. So we built [pi-monitor](https://github.com/DiversioTeam/agent-skills-marketplace/tree/main/pi-packages/pi-monitor), a Pi extension that runs an approved background script and feeds its output back to the model while it keeps working, which means we get it with Codex and other models through [Pi](https://pi.dev/) as well. I used [rea](https://github.com/morluto/rea) to build it, and then went through several iterations, letting Codex and Claude look at past sessions where it behaved poorly and fix those cases.

A disclaimer though: while pi-monitor works, it is still nowhere near as good as what you get out of the box in the Claude Code harness, especially with Opus 5.5. Claude seems to know when to start a watch, what to watch for and what to do with what comes back, without being told.

Part of it is the watch scripts themselves. When I ask Opus 5.5 to babysit something, it reaches for a short Bash command by default, and it's very rare that the command itself is wrong. When I use Pi with Codex models like Sol 6.1 or Astra, they often write a Python script for the same job, and it's not unusual for that script to be wrong. The monitor gets set up fine, nothing useful comes back, and only later does the model realise the problem was its own script and not the thing it was watching. So with pi-monitor we still end up nudging more. Armin Ronacher [noticed the same thing with Astra](https://lucumr.pocoo.org/2026/9/7/astra-why/): it really loves Python, even when working on TypeScript code in Pi. I wonder if OpenAI [acquiring Astral](https://openai.com/index/openai-to-acquire-astral/), the folks behind uv and Ruff, has something to do with it.

### I rarely babysit anymore

The bigger change for me is how little I have to watch over it now. With Opus 5.5 and the Claude Code harness, I really rarely babysit a session. When I use Pi or Codex CLI with Astra or Sol 6.1, I still have to keep checking in on them constantly, or queue up messages for when they finish.

It wasn't always like this. In the past I used to despise the Claude Code CLI. It lagged, message queuing was very much needed, and it used to get stuck. So I set up [cmux](https://cmux.com/) and a bunch of hooks just to get notified when Claude was stuck and needed my attention, same for Codex and Pi. cmux gave us those notifications out of the box for some of them, and for Pi we built [pi-cmux](https://github.com/DiversioTeam/pi-cmux).
Someone also built [peon-ping](https://github.com/PeonPing/peon-ping), which plays Warcraft peon voice lines from Claude Code's hooks whenever a session finishes or needs you. I still use it, even though the people sitting next to me are always confused :D

Now, with Opus 5.5 and whatever black magic they did with the harness, message queuing is pretty much not needed anymore. I just send the message. The model reads it, tells me what it's going to do with it, and decides on its own whether it belongs to the task it's already on or should go to one of its subagents. In rare cases I press Escape to let a message through right away, but that's rarely needed. Theo said something similar on X recently, and I fully agree: queuing messages in these harnesses isn't really needed if the model is smart enough to know what to do with an incoming message.

> Hot take: I don't like queueing messages.
>
> Modern models are smart enough to take a "steer" message and not get distracted by it
>
> — [Theo (@theo) on X, Oct 10, 2026](https://x.com/theo/status/2109072708495655051)

Unfortunately, it's still a pain with Pi and Codex CLI.

## Let sessions talk to each other

Every Claude Code session gets a name, a small slug like `product-d6`, and every subagent it spawns gets one as well. None of this is new. The part I didn't expect is that any session or subagent can find the other Claude sessions running on the same machine, in another terminal or anywhere else, and send them a message. They reply the same way. You can also ask to be told once another session goes idle, instead of staring at its terminal. To see which sessions it can reach, run [`/list-agents`](https://code.claude.com/docs/en/cross-session-messaging#see-which-sessions-claude-can-reach).

Since I accidentally discovered this, it has completely changed the way I multitask across projects.

You can ask for it in plain words ("ask the infra session whether that change shipped"), but for anything long running they also do it on their own, once they realise what you asked for needs someone else.

Here is roughly how my machine looks on a normal day. One session handles infrastructure. It has been taking instructions for weeks on how we plan changes, how we test them and how we apply them, so it knows that work really well without me re-explaining any of it. Another session looks after security across all of our projects. Then there's a long-running product session where features get built, and usually a shell or two with something experimental going on.

When a feature in the product session needs an infrastructure change, I don't explain our Terraform setup to it. I ask it to get in touch with the infrastructure session. Increasingly it does that by itself the moment it notices it is about to touch infrastructure: it sends over what it needs, the infra session reviews it, tests it properly and applies it (with my approval, of course), and replies that it's done. Then the product session can deploy its own change knowing the infrastructure side won't fall over.

Security works the same way. If I'm trying to merge something and a security check fails in CI, the product session doesn't have to become a security expert. It messages the security session, which knows how we fix these, gets the fix into `dev`, and tells the product session to pull in the latest base branch. Then the product session carries on.

You may be wondering why we don't just use skills that know how our infrastructure and security work, or guides in each project explaining how-tos and best practices, all linked from AGENTS.md. We still use them. But things change often, and updating a skill means pushing it to a repo and asking the other agents to pick it up (if the harness even supports hot reloading it), and even then a lot of the newer practices and features are missing from those files. A session that has been running for a while already knows those practices, plus everything it has learned since it started, from me and from other sessions, and it can apply all of that right away. When we're ready, we still fold it back into our skills and AGENTS.md files, but while a session is running it makes more sense to use what it already knows as soon as possible.

The browser is another one I use a lot. I keep one session that owns a Chrome window with a debug port and its own profile, so I know it's always the same browser with my logins for a few services, and it does the computer-use work there. When another agent needs something done in that browser, it asks that session instead of taking over the window itself. Otherwise I'd have to tell every agent to be careful with it: don't close it, don't log me out of anything, and so on. The session that manages that Chrome window already knows how to deal with all of that, does the work, and reports back to whoever asked.

<figure>
  <img
    src="{static}/images/articles/claude-code-features-you-may-not-have-tried/sessions-talking.svg"
    alt="A long-running product session with subagents in separate worktrees messages an infrastructure session and a security session, each of which already knows its area. A human approves infra, production and merges."
    style="width:100%;height:auto;display:block;"
  />
  <figcaption>The product session hands infra and security work to the sessions that already know how we do it.</figcaption>
</figure>

You can watch these conversations happen in real time, which is a bit surreal the first few times. Subagents can talk to other subagents across sessions too.

### Broadcasting to every session

The other thing I do a lot is broadcast. From any random session, I ask it to send a message to every agent and subagent running on my machine, and they each take care of it end to end.

Disk space is the usual one. Between Claude Code and Codex, caches, worktrees and build output take up a lot of space, and my laptop fills up faster than I'd like. So I tell one session to ask everyone to free up the space they created themselves, and every session cleans up its own scratch files, caches and merged worktrees and replies with roughly how much it freed. None of them touch what isn't theirs.

The same works for reports. If I need to know what security fixes went out in the past two weeks, which PRs got merged or which features shipped, I blast one message. Every session replies to whichever agent I asked, and I get one aggregated report back without digging through each session myself.

I also use it to find out which session can do something. If an agent needs something done in a web app, it can ask everyone whether they have that app open in their Chrome on the debug port through Playwright, and then hand the job to the session that says yes.

<figure>
  <img
    src="{static}/images/articles/claude-code-features-you-may-not-have-tried/broadcast.svg"
    alt="One session broadcasts a request to every other session and subagent, such as freeing disk space or listing security fixes shipped in the last two weeks. Each replies to the session that asked, which combines the replies into one report."
    style="width:100%;height:auto;display:block;"
  />
  <figcaption>One session sends the request out, and the replies come back to it as one report.</figcaption>
</figure>

A few examples from the last couple of weeks:

- A security session asked 11 other sessions what security fixes they had shipped since a given date. 10 came back within minutes with verified lists. Two of them disagreed about one change, and it got settled from the actual PR before anything was posted. That saved digging through about 15 PRs across 6 repos, and saved me from posting one wrong claim to the whole company.
- I wanted to restart my Mac after a recent macOS update and a bunch of cmux updates, but I wasn't sure what every agent was doing in its session. So I broadcast a message to all sessions saying I wanted to restart once they were done with their work. Each one logged its work first, so that after the reboot it would know where to resume from and that the system had restarted, and could pick its monitors and background tasks back up cleanly.
- A session asked a reviewer session to look at two frontend PRs at their latest commit. It found a build step that would crash and a setting that would have failed the production check.
- While I was doing the research for this post in a session of its own, three broadcasts sent a ping: the disk space one, one saying the debug Chrome instances had been restarted for a security update so everyone should reconnect, and one asking for a checkpoint note before a macOS restart.

### Fewer terminal tabs

Between subagents and messaging, we rarely open a new shell per task anymore. We have a foundation called [Dev Center](/all-tools-should-now-have-two-users.html) that can spin up any number of worktrees wherever we want. So inside one long-running product session, every subagent gets one job (a feature, an improvement, a bug fix) in its own worktree. It reports back to the main agent, and either of them can talk to the infra or security sessions when needed.

### Strict rules to follow

None of this means agents approve things for each other. The rules we work with:

- Agents can message each other, but approvals still come from a person. If one agent tells another that something was "approved", that's treated as information and nothing more.
- If one session has access to something and another doesn't, the work goes to the session with access. Credentials are never passed between sessions.
- When a session says it's done, we ask for the commit SHAs and CI run IDs so we can check.
- And of course, you can always go full YOLO on tasks that have no impact on anything in your company. In that case Claude will get shit done without asking for any approval or waiting on any decisions.

## Moving workflows off people's laptops

The third one is less about engineers. Some of our automation needs credentials and API keys that we don't want sitting on everyone's computer, and we want everything that happens to be visible.

For those, we use Claude Code's cloud environments. Each environment is set up once with the repo, its instructions and skills, the tools and MCP servers it needs, and secrets that are added outside the session so neither the person nor Claude ever sees them. Anyone on the team opens Claude in the browser, picks the environment, and asks for what they need. No Homebrew, no Claude Code install, no MCP setup.

<figure>
  <img
    src="{static}/images/articles/claude-code-features-you-may-not-have-tried/cloud-workflows.svg"
    alt="A teammate opens Claude in the browser and picks an environment. The QC flow produces a validation report, and the design system flow goes from questions to before and after pages to a draft pull request. Improving either is a push to main."
    style="width:100%;height:auto;display:block;"
  />
  <figcaption>Two of our cloud workflows: QC checks and design system changes.</figcaption>
</figure>

### QC checks against a third-party service

Our team does a lot of QC work: before anything goes out, someone has to check every page and every question in a third-party service against our own rules. For a long time that was done by hand. Then it became a skill that people had to run on their own machines, which meant installing things, keeping them updated, and storing API keys for that service on everyone's laptop. We even tried wiring those skills up to 1Password so the keys didn't sit in plain files, but honestly the experience was quite poor.

Now it's a cloud environment. Someone types "QC" followed by the ID or name of what they want checked, and a few minutes later there's a validation report in their Artifacts. Every rule gets a FAIL, WARN, PASS or SKIP, and every finding says where it is, what's different, why it matters and how to fix it. It is read-only, and that's enforced in code as well as in the instructions, so it can only read from the service. Claude also isn't allowed to soften results, so a FAIL stays a FAIL. In the first two weeks it produced around a dozen reports.

<figure><a href="{static}/images/articles/claude-code-features-you-may-not-have-tried/survey-qc-report.webp"><img src="{static}/images/articles/claude-code-features-you-may-not-have-tried/survey-qc-report.webp" alt="A validation report artifact for our survey template: 0 failed, 4 warnings, 100 passed and 2 skipped checks across 26 questions, followed by a manual checklist of conditions a person still has to verify by hand." width="2400" height="1720" loading="lazy"></a><figcaption>A real report, run against one of our templates rather than client data.</figcaption></figure>

### Design system changes without Lovable

Getting design changes from non-engineers used to go through [Lovable](https://lovable.dev/), and that was always a pain, mostly because whatever came out of it had nothing to do with our actual components and an engineer had to rebuild it. An honorary mention to the [Figma MCP server](https://www.figma.com/) as well: we tried it, used it for a while, and kept running into issues with it too. Having something built on top of our own design system has been a real blessing.

Now there's a "Design system" environment that works directly on our design system repo. Claude will initially ask one simple question at a time with 2–4 choices, never about files, props or anything technical. Within about three minutes the person gets clickable before and after pages as artifacts, and each tweak updates the same "after" link in about a minute. When they're happy and say "save it", Claude adds a test, runs the checks, deploys a private preview and opens a draft PR for an engineer to take over from there.

<div class="gallery" aria-label="Welcome banner, before and after">
<figure><a href="{static}/images/articles/claude-code-features-you-may-not-have-tried/welcome-banner-before.webp"><img src="{static}/images/articles/claude-code-features-you-may-not-have-tried/welcome-banner-before.webp" alt="Before: the manager dashboard's welcome banner, a gradient card with a paragraph of text and three feature tiles." width="2560" height="700" loading="lazy"></a><figcaption>Before: the welcome banner as it was.</figcaption></figure>
<figure><a href="{static}/images/articles/claude-code-features-you-may-not-have-tried/welcome-banner-after.webp"><img src="{static}/images/articles/claude-code-features-you-may-not-have-tried/welcome-banner-after.webp" alt="After: the same banner reworked into three numbered steps, each with a link, and a small preview of the dashboard on the right." width="2560" height="700" loading="lazy"></a><figcaption>After: three numbered steps with a small preview of the dashboard, built from our real components.</figcaption></figure>
</div>

This didn't come for free. We had to put a lot of work into making the design system ready for it. The foundational piece was building compositions on top of the existing components: every page, every interaction and every variant. Without them, Claude only knows components in isolation and has to guess what a page actually looks like. With them, when someone says "I want to change the home page a manager sees when they land on the dashboard for the very first time", it knows exactly which variant to pull instead of figuring it out on the fly. It makes far fewer mistakes, and it wastes fewer tokens getting there. A lot of the foundational work was done with GPT Astra when it came out. It's good at design work at high or higher thinking levels, and the limits on it were quite relaxed back then with all the resets, so it did a lot of the work that now lets us use our design system this way.

<figure>
  <img
    src="{static}/images/articles/claude-code-features-you-may-not-have-tried/compositions.svg"
    alt="Without compositions, Claude sees buttons, cards and banners in isolation and has to guess the page. With compositions for every page, interaction and variant, a request like the manager's first visit to the home page maps straight to one known variant."
    style="width:100%;height:auto;display:block;"
  />
  <figcaption>With compositions, Claude can pick the exact page and variant someone is talking about.</figcaption>
</figure>

### Updating these workflows

We used to install and update these things on everyone's machine. Now we maintain one repo per workflow. When something doesn't behave the way we want, we fix the instructions or the skill, push to `main`, and the next cloud session picks it up and does better. Now I don't have to worry about giving people access to GitHub, figuring out how to distribute the skill and keep it up to date, or managing secure credentials on their machines.

## The built-in browser in the desktop app

The last one is mostly for the non-technical folks. Engineers have it easy here: we can start Chrome with a debug port from the CLI and then do pretty much anything on it with computer use or Playwright. Nobody outside engineering is going to do that.

The Claude desktop app gives them the same thing without any of that setup. The Code tab in the desktop app has a built-in browser. They open a tab, log into whatever they need in that browser, and can keep those cookies so they don't have to sign in every time.

Then they just tell Claude what they need. "I have our analytics dashboard open, help me understand what changed this week." "Check my email and find the contract we got from this vendor." It doesn't really matter whether that app has an API or an MCP server, as long as it opens in a browser.

<figure>
  <img
    src="{static}/images/articles/claude-code-features-you-may-not-have-tried/desktop-browser.svg"
    alt="Engineers drive a debug Chrome from the CLI with Playwright or computer use. Non-technical teammates use the built-in browser in the Claude desktop app's Code tab, log in there, and ask Claude to work with any web app, with or without an API."
    style="width:100%;height:auto;display:block;"
  />
  <figcaption>How engineers drive a browser today, and how everyone else can do it from the desktop app.</figcaption>
</figure>

That alone saves a lot of clicking around and copy-pasting.

The other thing people don't expect is how good it is at capturing what it did. Claude takes screenshots in the desktop app's browser as it checks its work, and with Playwright on a local Chrome running on the debug port we can capture a whole session end to end: Playwright captures the frames, ffmpeg stitches them together, and we add transcripts and audio on top. We use this a lot to prove in a PR that a feature works, to show how a feature works, and to build product demos. It lets us prove a feature works end to end much better than a unit test would, and we can get the clanker to do it for any amount of sample or synthetic data.

## Related reading

- [All tools should now have two users](/all-tools-should-now-have-two-users.html)
- [How we use AI like engineers](/how-we-use-ai-like-engineers.html)
- [The Shared Workspace That Made AI Actually Useful](/the-monolith-that-made-ai-actually-useful.html)

<div class="article-subtext article-subtext--ai">
  <p class="article-subtext-label">AI writing disclaimer</p>
  <ul>
    <li>The diagrams and video were generated with Claude Code.</li>
  </ul>
</div>
