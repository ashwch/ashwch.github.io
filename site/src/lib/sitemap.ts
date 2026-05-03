import { getAllArticles, getAllPages, getCategoryIndex, getTagIndex } from './content';
import { getVisiblePhotos } from './photography';
import { siteMeta } from '../data/site';

type SitemapEntry = {
  url: string;
  lastmod?: string;
};

function escapeXml(value: string) {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

function toAbsolute(url: string) {
  return new URL(url, siteMeta.siteUrl).toString();
}

function toLastmod(date: Date) {
  return date.toISOString();
}

export async function getCanonicalSitemapEntries(): Promise<SitemapEntry[]> {
  const [articles, pages] = await Promise.all([getAllArticles(), getAllPages()]);
  const tags = getTagIndex(articles);
  const categories = getCategoryIndex(articles);

  const entries: SitemapEntry[] = [
    { url: siteMeta.siteUrl },
    { url: toAbsolute('/writing.html') },
    { url: toAbsolute('/archives.html') },
    { url: toAbsolute('/tags.html') },
    { url: toAbsolute('/categories.html') },
  ];

  const hasVisiblePhotos = getVisiblePhotos().length > 0;

  for (const page of pages) {
    if (page.data.pageType === 'photography' && !hasVisiblePhotos) {
      continue;
    }
    entries.push({ url: page.data.canonicalUrl });
  }

  for (const article of articles) {
    entries.push({
      url: article.data.canonicalUrl,
      lastmod: toLastmod(article.data.modified ?? article.data.date),
    });
  }

  for (const tag of tags) {
    entries.push({ url: toAbsolute(`/tag/${tag.slug}.html`) });
  }

  for (const category of categories) {
    entries.push({ url: toAbsolute(`/category/${category.slug}.html`) });
  }

  return entries;
}

export function renderSitemapUrlset(entries: SitemapEntry[]) {
  const body = entries
    .map((entry) => {
      const lastmod = entry.lastmod ? `<lastmod>${escapeXml(entry.lastmod)}</lastmod>` : '';
      return `<url><loc>${escapeXml(entry.url)}</loc>${lastmod}</url>`;
    })
    .join('');

  return `<?xml version="1.0" encoding="UTF-8"?>` +
    `<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${body}</urlset>`;
}

export function renderSitemapIndex(urls: string[]) {
  const body = urls
    .map((url) => `<sitemap><loc>${escapeXml(url)}</loc></sitemap>`)
    .join('');

  return `<?xml version="1.0" encoding="UTF-8"?>` +
    `<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${body}</sitemapindex>`;
}
