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

export const featuredProjects = projects.filter((project) => project.featured);
