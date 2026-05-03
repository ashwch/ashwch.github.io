import { getCollection, type CollectionEntry } from 'astro:content';
import readingTime from 'reading-time';

export const ARTICLE_PAGE_SIZE = 5;
export const LEGACY_AUTHOR_SLUGS = [
  'ashwini-chaudhary',
  'ashwini-chaudhary2',
  'ashwini-chaudhary3',
] as const;

export type ArticleEntry = CollectionEntry<'articles'>;
export type PageEntry = CollectionEntry<'pages'>;

export function slugify(value: string) {
  return value
    .toLowerCase()
    .trim()
    .replace(/&/g, ' ')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

const TORONTO_TIME_ZONE = 'America/Toronto';

export function formatDate(date: Date) {
  return new Intl.DateTimeFormat('en', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    timeZone: TORONTO_TIME_ZONE,
  }).format(date);
}

export function formatDateIso(date: Date) {
  return new Intl.DateTimeFormat('en-CA', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    timeZone: TORONTO_TIME_ZONE,
  }).format(date);
}

export function getReadingStats(markdown: string) {
  const stats = readingTime(markdown);
  return {
    text: stats.text,
    minutes: Math.max(1, Math.round(stats.minutes)),
    words: stats.words,
  };
}

export function getTagPath(tag: string) {
  return `/tag/${slugify(tag)}.html`;
}

export function getCategoryPath(category: string) {
  return `/category/${slugify(category)}.html`;
}

export async function getAllArticles() {
  const articles = await getCollection('articles', ({ data }) => !data.draft);
  return articles.sort((left, right) => right.data.date.getTime() - left.data.date.getTime());
}

export async function getAllPages() {
  return getCollection('pages', ({ data }) => !data.draft);
}

export async function getPageBySlug(slug: string) {
  const pages = await getAllPages();
  return pages.find((page) => page.data.slug === slug);
}

export function getArticlesForLegacyPage(articles: ArticleEntry[], pageNumber: number) {
  const start = (pageNumber - 1) * ARTICLE_PAGE_SIZE;
  return articles.slice(start, start + ARTICLE_PAGE_SIZE);
}

export function getTagIndex(articles: ArticleEntry[]) {
  const tags = new Map<
    string,
    { label: string; slug: string; articles: ArticleEntry[] }
  >();

  for (const article of articles) {
    for (const tag of article.data.tags) {
      const slug = slugify(tag);
      const entry = tags.get(slug) || { label: tag, slug, articles: [] };
      entry.articles.push(article);
      tags.set(slug, entry);
    }
  }

  return [...tags.values()].sort((left, right) => left.label.localeCompare(right.label));
}

export function getCategoryIndex(articles: ArticleEntry[]) {
  const categories = new Map<
    string,
    { label: string; slug: string; articles: ArticleEntry[] }
  >();

  for (const article of articles) {
    for (const category of article.data.categories) {
      const slug = slugify(category);
      const entry = categories.get(slug) || { label: category, slug, articles: [] };
      entry.articles.push(article);
      categories.set(slug, entry);
    }
  }

  return [...categories.values()].sort((left, right) => left.label.localeCompare(right.label));
}

export function getRelatedArticles(article: ArticleEntry, allArticles: ArticleEntry[], limit = 3) {
  const articleTags = new Set(article.data.tags.map((tag) => slugify(tag)));

  return allArticles
    .filter((candidate) => candidate.id !== article.id)
    .map((candidate) => ({
      article: candidate,
      score:
        (candidate.data.domain === article.data.domain ? 2 : 0) +
        candidate.data.tags.filter((tag) => articleTags.has(slugify(tag))).length,
    }))
    .sort((left, right) => {
      if (right.score !== left.score) return right.score - left.score;
      return right.article.data.date.getTime() - left.article.data.date.getTime();
    })
    .slice(0, limit)
    .map((entry) => entry.article);
}

export function getArchiveGroups(articles: ArticleEntry[]) {
  const groups = new Map<number, ArticleEntry[]>();

  for (const article of articles) {
    const year = article.data.date.getFullYear();
    groups.set(year, [...(groups.get(year) || []), article]);
  }

  return [...groups.entries()].sort((left, right) => right[0] - left[0]);
}
