import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const articles = defineCollection({
  loader: glob({
    base: './src/content/articles',
    pattern: '**/*.md',
  }),
  schema: z.object({
    title: z.string(),
    slug: z.string(),
    titleHtml: z.string().optional(),
    legacyUrl: z.string(),
    canonicalUrl: z.url(),
    date: z.coerce.date(),
    modified: z.coerce.date().optional(),
    summary: z.string().optional(),
    description: z.string(),
    domain: z.string(),
    categories: z.array(z.string()).default([]),
    tags: z.array(z.string()).default([]),
    authors: z.array(z.string()).default([]),
    draft: z.boolean().default(false),
  }),
});

const pages = defineCollection({
  loader: glob({
    base: './src/content/pages',
    pattern: '**/*.md',
  }),
  schema: z.object({
    title: z.string(),
    slug: z.string(),
    legacyUrl: z.string(),
    canonicalUrl: z.url(),
    description: z.string(),
    template: z.string().optional(),
    pageType: z.string(),
    draft: z.boolean().default(false),
  }),
});

export const collections = { articles, pages };
