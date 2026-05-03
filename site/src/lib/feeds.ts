import { Feed } from 'feed';
import type { ArticleEntry } from './content';
import { siteMeta } from '../data/site';

type FeedOptions = {
  title: string;
  description: string;
  id: string;
  feedUrl: string;
  articles: ArticleEntry[];
};

function absoluteUrl(url: string) {
  return new URL(url, siteMeta.siteUrl).toString();
}

function sanitizeFeedHtml(html: string) {
  return html
    .replace(/<a class="heading-anchor"[^>]*>#[^<]*<\/a>/g, '')
    .replace(/(src|href)="\/(?!\/)/g, `$1="${siteMeta.siteUrl}/`);
}

function feedItemId(article: ArticleEntry) {
  const date = article.data.date.toISOString().slice(0, 10);
  return `tag:ashwch.com,${date}:${article.data.legacyUrl}`;
}

function htmlSummary(article: ArticleEntry) {
  const summary = article.data.summary ?? article.data.description;
  return `<p>${summary}</p><p><a href="${article.data.canonicalUrl}">Read the full article</a>.</p>`;
}

function articleContent(article: ArticleEntry) {
  const html = article.rendered?.html?.trim();
  return sanitizeFeedHtml(html || htmlSummary(article));
}

export function createFeed({ title, description, id, feedUrl, articles }: FeedOptions) {
  const feed = new Feed({
    id,
    link: id,
    feed: feedUrl,
    title,
    description,
    language: 'en',
    favicon: absoluteUrl('/favicon.ico'),
    copyright: `© ${new Date().getFullYear()} ${siteMeta.author}`,
    updated: articles[0]?.data.modified ?? articles[0]?.data.date ?? new Date(),
    generator: 'Astro',
    feedLinks: {
      atom: absoluteUrl('/feeds/all.atom.xml'),
      rss2: absoluteUrl('/rss.xml'),
    },
    author: {
      name: siteMeta.author,
      link: absoluteUrl('/pages/about.html'),
    },
  });

  for (const article of articles) {
    feed.addItem({
      id: feedItemId(article),
      guid: feedItemId(article),
      title: article.data.title,
      link: article.data.canonicalUrl,
      description: article.data.summary ?? article.data.description,
      content: articleContent(article),
      author: article.data.authors.map((name) => ({ name })),
      date: article.data.modified ?? article.data.date,
      published: article.data.date,
      category: article.data.tags.map((tag) => ({ name: tag })),
    });
  }

  return feed;
}
