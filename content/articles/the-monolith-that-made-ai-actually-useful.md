Title: The Monolith That Made AI Actually Useful
Date: 2025-08-07
Category: Development
Tags: git-worktrees, development-workflow, ai-tools, monorepo, claude-code, mcp, devops, productivity, bruno
Slug: the-monolith-that-made-ai-actually-useful
Authors: Ashwini Chaudhary
Summary: How we solved context switching across multiple repositories by building a monolith using git submodules, making both humans and AI 10x more effective with our codebase.

> Picture this: You're debugging an issue that spans your React frontend, Django backend, and Terraform infrastructure. Three terminal windows. Three different repos. Three different contexts. By the time you trace the bug from UI to API to database, you've lost half your morning just to context switching.

We solved this at Diversio. The solution made both humans and AI 10x more effective with our codebase.

---

[TOC]

---

## What you'll learn

- **Structure a monolith** repository with git submodules for maximum efficiency
- **Master git worktrees** for parallel development without context switching  
- **Automate worktree creation** with our Python scripts (links included!)
- **Reduce context switching** by 90% and watch productivity soar
- **Supercharge AI tools** with complete codebase context—making them actually useful
- **Implement immediately** with practical tips and working code

If you're tired of juggling multiple repos and losing context between features, this guide shows you exactly how we solved it. If you're already using git submodules, you'll learn how to level up with worktrees and automation.

---

## The Problem We Were Facing

Every feature we built touched multiple repositories:

- Clone three separate repos
- Keep versions in sync
- Jump between directories constantly  
- Lose context when debugging cross-service issues

But here's the real kicker. AI tools like Claude Code couldn't see our full system. They'd suggest fixes that made sense for one service but broke two others. They had fragments, not the full picture.

## Our Solution: Git Submodules Done Right

We built a monolith using git submodules that gives us the best of both worlds:

```
diversio-monolith/
├── frontend/              # React application
├── backend/               # Django API
├── design-system/         # Shared UI components
├── optimo-frontend/       # Optimo product app
├── diversio-serverless/   # AWS Lambda functions
├── infrastructure/        # Terraform definitions
├── terraform-modules/     # Reusable infrastructure
└── scripts/               # Development automation
```

Each directory is its own git repository. But they all live in one workspace. One clone gets you everything.

## From Hours to Minutes

Our product managers now redesign features in minutes, not hours. They pull the latest code, run migrations, and have AI analyze our Bruno API collections. Remember when we [migrated from Postman to Bruno]({filename}/articles/from-postman-to-bruno-how-ai-changed-our-api-workflow.md)? That decision pays huge dividends in a monolith.

The workflow looks like this:

1. Pull latest commits across all services
2. Run migrations with full database context
3. AI reads organized API documentation
4. Create comprehensive designs with complete system understanding
5. Implement changes knowing exactly what will be affected

What used to take hours of repository hopping now happens in a single flow.

## The AI Advantage

Here's where it gets interesting. By giving AI tools complete system context, we unlocked capabilities that were impossible before:

- **Cross-repository analysis**: Claude Code traces API calls from frontend to backend to infrastructure
- **Better architectural decisions**: Suggestions consider the entire stack
- **System-wide debugging**: Issues that span services become traceable
- **Smarter refactoring**: Changes account for all dependencies

The AI isn't guessing anymore. It knows.

## Git Worktrees: The Secret Sauce

The real magic happens with git worktrees. Instead of switching branches and losing context, we work on multiple features simultaneously:

```bash
# Create a new worktree for a feature
uv run scripts/create_worktree.py
```

Our automation handles everything:

- Interactive branch selection across all repositories
- Smart filtering for hundreds of branches
- Automatic submodule initialization
- Proper conflict resolution
- Copies .env files (because git worktrees don't do this by default, and nobody wants to debug missing environment variables)

Check out our automation scripts:

- [**create_worktree.py**](https://gist.github.com/ashwch/79177b4af7f2ea482418d6e9934d4787) - Interactive worktree creator with submodule support
- [**update_submodules.py**](https://gist.github.com/ashwch/909ea473250e8c8a937a8a4aa4a4dc72) - Automated submodule updater with branch configuration

Each developer can have multiple features in progress, each in its own directory, with full system context preserved.

## Custom AI Agents: Specialized Tools for Every Task

We built specialized Claude Code agents that understand our codebase deeply:

- **Frontend PR Specialist**: Analyzes React/TypeScript changes with component architecture visualizations
- **Backend PR Specialist**: Reviews Django changes with database schema analysis
- **Infrastructure PR Specialist**: Validates Terraform changes with cost and security impact assessments  
- **Integration Specialist**: Traces data flows across frontend, backend, and infrastructure
- **Data Migration Specialist**: Handles complex data transformations and migrations
- **Testing Automation Specialist**: Writes comprehensive test suites following our patterns

Each agent has deep knowledge of its domain. They don't just suggest generic fixes. They understand our specific patterns, our conventions, our tech stack.

We even built meta agents that manage other agents:

- **Subagent Creator**: Designs new focused agents with clear boundaries
- **Subagent Reviewer**: Reviews and optimizes agent definitions to prevent overlaps

These meta agents save hours when adding or updating agents. No more manual agent configuration. The AI helps manage the AI.

The best part? These agents are shared across the entire team through the monolith. When one engineer creates an agent, everyone benefits immediately.

## MCP Integration: Supercharging AI Tools

We integrated Model Context Protocol (MCP) servers that give Claude Code direct access to:

- **CircleCI**: Build status, test results, deployment logs
- **Context7**: Up-to-date documentation for any library
- **Gemini AI**: Research and code analysis
- **Playwright**: Browser automation for testing

These integrations work seamlessly across the entire monolith, giving AI unprecedented visibility into our development pipeline.

## Benefits Across the Team

**Product Managers** get complete system visibility for rapid prototyping. API documentation and database schemas always accessible.

**New Engineers** get a single command setup. Clone one repo, get everything with working examples.

**Senior Engineers** can do system-wide refactoring. Make changes across repos with full context.

**AI Tools** get complete codebase analysis. Suggestions that actually work.

**DevOps teams** see infrastructure definitions alongside the code they deploy.

## The Technical Details

**Submodule Management**: Each submodule points to a specific commit. Changes need commits in both the submodule and the monolith. This preserves atomicity while enabling coordination.

**Branch Independence**: Work on different branches in each submodule simultaneously. Perfect for features that need coordinated changes. And crucially, pull requests still go to individual repositories, maintaining our existing review processes and CI/CD pipelines.

**Automated Tooling**: Our Python scripts handle branch management, worktree creation, and submodule updates. No manual coordination needed.

**API Documentation as Code**: Bruno's file-based approach means API collections live with the code they test. They're discoverable, version-controlled, and immediately accessible to both humans and AI. The AI can read, understand, and even suggest API changes based on the actual implementation.

## Why This Matters Now

AI tools are becoming primary development partners. But these tools are only as good as the context you give them. 

By structuring our codebase for maximum AI comprehension, we created an environment where both humans and AI work at their full potential.

The results: 10x faster feature development, 90% fewer integration bugs, and architectural decisions that consider the full system impact.

## Getting Started

If you're working with multiple related repositories, you can implement this:

1. Create a monolith repository
2. Add existing repos as git submodules
3. Build automation scripts for common workflows
4. Configure MCP servers for your tools
5. Train your team on git worktrees
6. Move API documentation to file-based tools like Bruno

The investment pays off immediately. No more context switching, better AI assistance, and a development experience that scales with complexity.

## The Bottom Line

This isn't just about tooling. It's about creating an environment where high-quality work happens quickly and naturally.

When your product managers can redesign systems confidently, your engineers can refactor safely across services, and your AI tools provide system-aware suggestions, you've built more than a development environment.

You've built a competitive advantage.

---

Want to dive deeper into Git worktrees? Check out my comprehensive guide: [Git Worktrees: From Zero to Hero](https://gist.github.com/ashwch/946ad983977c9107db7ee9abafeb95bd). It covers everything from first principles to advanced workflows with submodules.

*Thanks to [Samuel Bonin](https://www.linkedin.com/in/samuel-bonin/) and [Amal Raj](https://www.linkedin.com/in/amalraj-offl/) for reviewing this post.*