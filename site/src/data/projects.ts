/**
 * Projects + open-source credibility data.
 *
 * This file serves two different page surfaces:
 *
 *   Homepage     → uses `projects` and `featuredProjects`
 *   Projects page → uses all three: featured, utility, and highlights
 *
 * TYPE HIERARCHY
 *
 *   Project
 *     A concrete repo, tool, or site I actively maintain.
 *     Rendered as cards with tags, install snippets, and Open / Source buttons.
 *
 *   ProjectHighlight
 *     A broader body of work that spans multiple repos, orgs, or years.
 *     Not a single repo — more like "Python ecosystem" or "Instamojo SDKs".
 *     Rendered as compact cards with a label (category), description, tags,
 *     and a list of clean external links to specific repos, PR lists, or event pages.
 *
 *   ProjectLink
 *     A labeled URL inside a highlight card.  Because highlights cover broad
 *     work, we give the reader multiple entry points instead of one big link.
 *
 * LAYOUT STRATEGY (Projects page)
 *
 *   Section 1  "Current projects"       2 featured cards (Microverse, auto-uv-env)
 *   Section 2  "Selected open source..." 4 highlight cards  (Python, Django, Instamojo, Community)
 *   Section 3  "More tools"              small utility grid  (wt, ew, dotfiles, agent-skills)
 *
 *   This order puts credibility upfront and keeps the smaller personal tools
 *   in a supporting role further down the page.
 */

// ── Types ─────────────────────────────────────────────────────────────────────

export type Project = {
  slug: string;
  name: string;
  category: string;
  description: string;
  tags: string[];
  href: string;
  repo?: string;
  docs?: string;
  featured?: boolean;
  install?: string;
  canonicalExternal?: boolean;
};

export type ProjectLink = {
  label: string;
  href: string;
};

export type ProjectHighlight = {
  slug: string;
  title: string;
  category: string;
  description: string;
  tags: string[];
  links: ProjectLink[];
};

// ── Active projects ──────────────────────────────────────────────────────────

export const projects: Project[] = [
  {
    slug: 'microverse',
    name: 'Microverse',
    category: 'Frameworks',
    description:
      'macOS system monitoring with desktop widgets and low overhead.',
    tags: ['Swift', 'SwiftUI', 'macOS'],
    href: 'https://microverse.ashwch.com',
    repo: 'https://github.com/ashwch/microverse',
    docs: 'https://microverse.ashwch.com',
    featured: true,
    canonicalExternal: true,
  },
  {
    slug: 'auto-uv-env',
    name: 'auto-uv-env',
    category: 'Developer Tooling',
    description:
      'UV-based Python environment management for fast local project switching.',
    tags: ['Shell', 'Python', 'CLI'],
    href: 'https://auto-uv-env.ashwch.com',
    repo: 'https://github.com/ashwch/auto-uv-env',
    docs: 'https://auto-uv-env.ashwch.com',
    featured: true,
    install: 'cargo install auto-uv-env',
    canonicalExternal: true,
  },
  {
    slug: 'wt',
    name: 'wt',
    category: 'CLI Tools',
    description: 'Interactive git worktree dashboard for multi-branch workflows.',
    tags: ['Shell', 'fzf', 'Git'],
    href: 'https://github.com/ashwch/wt',
    repo: 'https://github.com/ashwch/wt',
    install: 'npm i -g @ashwch/wt',
  },
  {
    slug: 'ew',
    name: 'ew',
    category: 'CLI Tools',
    description: 'A shell helper that turns plain English into commands.',
    tags: ['Go', 'CLI', 'AI'],
    href: 'https://github.com/ashwch/ew',
    repo: 'https://github.com/ashwch/ew',
    install: 'brew install ashwch/tap/ew',
  },
  {
    slug: 'dotfiles',
    name: 'dotfiles',
    category: 'Personal Systems',
    description: 'macOS terminal and development environment defaults.',
    tags: ['Shell', 'Zsh', 'Neovim'],
    href: 'https://github.com/ashwch/dotfiles',
    repo: 'https://github.com/ashwch/dotfiles',
  },
  {
    slug: 'agent-skills-marketplace',
    name: 'agent-skills-marketplace',
    category: 'AI Workflows',
    description: 'Reusable coding-agent skills and workflow automation assets.',
    tags: ['Docs', 'Shell', 'Agentic Engineering'],
    href: 'https://github.com/DiversioTeam/agent-skills-marketplace',
    repo: 'https://github.com/DiversioTeam/agent-skills-marketplace',
  },
];

/** The two projects that appear as hero-level cards on the homepage. */
export const featuredProjects = projects.filter((project) => project.featured);

// ── Broader credibility highlights ───────────────────────────────────────────
//
// These are NOT individual repos.  They represent clusters of related public
// work that would be hard to grok from a single link.
//
// Each highlight links to specific repos, PR lists, or community pages so
// readers can verify the claim without hunting through search results.

export const projectHighlights: ProjectHighlight[] = [
  {
    slug: 'python-ecosystem',
    title: 'Python ecosystem',
    category: 'Open Source',
    description:
      'Contributed patches and typing work across CPython, typeshed, and mypy, from accepted fixes to better stub coverage and tooling.',
    tags: ['Python', 'CPython', 'typeshed', 'mypy'],
    links: [
      {
        label: 'typeshed merged PRs',
        href: 'https://github.com/python/typeshed/pulls?q=is%3Apr+author%3Aashwch+is%3Amerged',
      },
      {
        label: 'mypy merged work',
        href: 'https://github.com/python/mypy/pulls?q=is%3Apr+author%3Aashwch+is%3Amerged',
      },
      {
        label: 'CPython',
        href: 'https://github.com/python/cpython',
      },
    ],
  },
  {
    slug: 'django-and-tooling',
    title: 'Django and tooling',
    category: 'Open Source',
    description:
      'Worked on django-debug-toolbar, django-annoying, pep8speaks, pgmpy, and other libraries that improved debugging, compatibility, and daily developer experience.',
    tags: ['Django', 'Tooling', 'Debugging'],
    links: [
      {
        label: 'django-debug-toolbar',
        href: 'https://github.com/django-commons/django-debug-toolbar/pulls?q=is%3Apr+author%3Aashwch+is%3Amerged',
      },
      {
        label: 'pep8speaks',
        href: 'https://github.com/pep8speaks-org/pep8speaks/pulls?q=is%3Apr+author%3Aashwch+is%3Amerged',
      },
      {
        label: 'pgmpy',
        href: 'https://github.com/pgmpy/pgmpy/pulls?q=is%3Apr+author%3Aashwch+is%3Amerged',
      },
    ],
  },
  {
    slug: 'instamojo-sdk-ecosystem',
    title: 'Instamojo SDK ecosystem',
    category: 'Payments',
    description:
      'Built and maintained payment SDKs and commerce plugins across Python, PHP, Ruby, Java, .NET, and several commerce platforms.',
    tags: ['Payments', 'SDKs', 'Commerce'],
    links: [
      // Each of these repos lists ashwch as a contributor,
      // so clicking through proves involvement.
      {
        label: 'instamojo-py',
        href: 'https://github.com/Instamojo/instamojo-py',
      },
      {
        label: 'instamojo-php',
        href: 'https://github.com/Instamojo/instamojo-php',
      },
      {
        label: 'instamojo-csharp',
        href: 'https://github.com/Instamojo/instamojo-csharp',
      },
      {
        label: 'Magento, PrestaShop, OpenCart, Drupal, CS-Cart, and more',
        href: 'https://github.com/orgs/Instamojo/repositories',
      },
    ],
  },
  {
    slug: 'community-and-talks',
    title: 'Community and talks',
    category: 'Community',
    description:
      'Spoke at MUPy 2016 on pdb, coached at Django Girls Bangalore, and contributed enough public code to be included in the GitHub Arctic Code Vault.',
    tags: ['Talks', 'Mentorship', 'Community'],
    links: [
      {
        label: 'MUPy 2016 talk',
        href: 'https://github.com/ashwch/pdb-mupy',
      },
      {
        label: 'Django Girls Bangalore',
        href: 'https://djangogirls.org/en/bangalore2/',
      },
      {
        label: 'Arctic Code Vault',
        href: 'https://archiveprogram.github.com/',
      },
    ],
  },
];
