import { mkdir, readdir, readFile, rm, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SITE_ROOT = path.resolve(__dirname, '..');
const REPO_ROOT = path.resolve(SITE_ROOT, '..');
const SOURCE_ROOT = path.join(REPO_ROOT, 'content');
const TARGET_ROOT = path.join(SITE_ROOT, 'src', 'content');

const ARTICLE_SOURCE = path.join(SOURCE_ROOT, 'articles');
const PAGE_SOURCE = path.join(SOURCE_ROOT, 'pages');
const ARTICLE_TARGET = path.join(TARGET_ROOT, 'articles');
const PAGE_TARGET = path.join(TARGET_ROOT, 'pages');

function splitCsv(value = '') {
  return value
    .split(',')
    .map((part) => part.trim())
    .filter(Boolean);
}

function parseLegacyCategory(value = '') {
  const trimmed = value.trim();
  return trimmed ? [trimmed] : [];
}

function parsePelicanDocument(source) {
  const lines = source.replace(/\r\n/g, '\n').split('\n');
  const metadata = {};
  let index = 0;

  for (; index < lines.length; index += 1) {
    const line = lines[index];
    if (!line.trim()) {
      index += 1;
      break;
    }

    const match = line.match(/^([A-Za-z][A-Za-z0-9 _-]*):\s*(.*)$/);
    if (!match) {
      break;
    }

    metadata[match[1].toLowerCase()] = match[2].trim();
  }

  const body = lines.slice(index).join('\n').replaceAll('{static}/', '/');
  return { metadata, body };
}

function inferDomain(categories, tags) {
  const haystack = [...categories, ...tags].join(' ').toLowerCase();

  if (/(agentic|ai|mcp|claude|copilot|llm|embedding)/.test(haystack)) {
    return 'AI';
  }

  if (/(leadership|management|hiring|onboarding|mentorship|business)/.test(haystack)) {
    return 'Leadership';
  }

  if (/(security|audit|permissions|rls|iam|saas)/.test(haystack)) {
    return 'Security';
  }

  if (/(productivity|self-improvement|life-lessons|history|habits)/.test(haystack)) {
    return 'Growth';
  }

  if (/(photography|portrait|urban|landscape|astronomy)/.test(haystack)) {
    return 'Photography';
  }

  if (/(python|django|programming|development|engineering|architecture|system-design|devops|tooling|terminal|uv)/.test(haystack)) {
    return 'Engineering';
  }

  return 'Writing';
}

function stripHtmlTags(value = '') {
  return value.replace(/<[^>]*>/g, '').replace(/\s+/g, ' ').trim();
}

function torontoOffsetForDate(dateString) {
  const probe = new Date(`${dateString}T12:00:00Z`);
  const parts = new Intl.DateTimeFormat('en-US', {
    timeZone: 'America/Toronto',
    timeZoneName: 'shortOffset',
    hour: '2-digit',
    minute: '2-digit',
  }).formatToParts(probe);
  const timeZoneName = parts.find((part) => part.type === 'timeZoneName')?.value || 'GMT-5';
  const match = timeZoneName.match(/^GMT([+-])(\d{1,2})(?::(\d{2}))?$/);

  if (!match) {
    return '-05:00';
  }

  const [, sign, hours, minutes = '00'] = match;
  return `${sign}${hours.padStart(2, '0')}:${minutes}`;
}

function normalizeDateString(value = '') {
  if (!value) return undefined;
  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    return `${value}T00:00:00${torontoOffsetForDate(value)}`;
  }
  return value;
}

function quote(value) {
  return JSON.stringify(value);
}

function buildFrontmatter(fields) {
  const orderedKeys = [
    'title',
    'slug',
    'titleHtml',
    'legacyUrl',
    'canonicalUrl',
    'date',
    'modified',
    'summary',
    'description',
    'domain',
    'categories',
    'tags',
    'authors',
    'draft',
    'template',
    'pageType',
  ];

  const lines = ['---'];
  for (const key of orderedKeys) {
    if (!(key in fields) || fields[key] === undefined) {
      continue;
    }
    lines.push(`${key}: ${quote(fields[key])}`);
  }
  lines.push('---', '');
  return lines.join('\n');
}

async function ensureCleanDir(dir) {
  await rm(dir, { recursive: true, force: true });
  await mkdir(dir, { recursive: true });
}

async function migrateArticles() {
  const files = (await readdir(ARTICLE_SOURCE)).filter((file) => file.endsWith('.md'));

  for (const file of files.sort()) {
    const source = await readFile(path.join(ARTICLE_SOURCE, file), 'utf8');
    const { metadata, body } = parsePelicanDocument(source);
    const tags = splitCsv(metadata.tags);
    const categories = parseLegacyCategory(metadata.category);
    const slug = metadata.slug || file.replace(/\.md$/i, '');
    const legacyUrl = `/${slug}.html`;
    const rawTitle = metadata.title || slug;
    const title = stripHtmlTags(rawTitle) || slug;
    const titleHtml = rawTitle !== title ? rawTitle : undefined;

    const frontmatter = buildFrontmatter({
      title,
      titleHtml,
      slug,
      legacyUrl,
      canonicalUrl: `https://ashwch.com${legacyUrl}`,
      date: normalizeDateString(metadata.date),
      modified: normalizeDateString(metadata.modified || metadata.date),
      summary: metadata.summary || undefined,
      description: metadata.summary || title,
      domain: inferDomain(categories, tags),
      categories,
      tags,
      authors: splitCsv(metadata.authors || 'Ashwini Chaudhary'),
      draft: (metadata.status || '').toLowerCase() === 'draft',
    });

    const target = path.join(ARTICLE_TARGET, file);
    await writeFile(target, `${frontmatter}${body.trimStart()}\n`);
  }
}

async function migratePages() {
  const files = (await readdir(PAGE_SOURCE)).filter((file) => file.endsWith('.md'));

  for (const file of files.sort()) {
    const source = await readFile(path.join(PAGE_SOURCE, file), 'utf8');
    const { metadata, body } = parsePelicanDocument(source);
    const slug = metadata.slug || metadata.title?.toLowerCase().replace(/\s+/g, '-') || file.replace(/\.md$/i, '');
    const title = metadata.title || slug.replace(/(^|-)\w/g, (match) => match.toUpperCase());
    const pageType = slug === 'about' ? 'about' : slug === 'projects' ? 'projects' : slug === 'photography' ? 'photography' : 'page';
    const legacyUrl = `/pages/${slug}.html`;

    const frontmatter = buildFrontmatter({
      title,
      slug,
      legacyUrl,
      canonicalUrl: `https://ashwch.com${legacyUrl}`,
      description: metadata.summary || title,
      template: metadata.template || undefined,
      pageType,
      draft: (metadata.status || '').toLowerCase() === 'draft',
    });

    const target = path.join(PAGE_TARGET, file);
    await writeFile(target, `${frontmatter}${body.trimStart()}\n`);
  }
}

async function main() {
  await ensureCleanDir(ARTICLE_TARGET);
  await ensureCleanDir(PAGE_TARGET);
  await migrateArticles();
  await migratePages();
  console.log('Migrated Pelican content into Astro collections.');
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
