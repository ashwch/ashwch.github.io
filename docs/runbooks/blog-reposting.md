# Blog Reposting Runbook

Use this runbook when one article needs to appear in two places:

- the **full article** should live on `ashwch.com`
- a **short discovery stub** should live on `engineering.diversio.com`

## Why this runbook exists

We now have two public writing surfaces:

- `ashwch.com` — Ashwini's personal site
- `engineering.diversio.com` — Diversio's engineering site

A cross-post only works well if one place clearly owns the full article.
Without that rule, we quickly create avoidable problems:

- two full copies that drift apart
- unclear canonical ownership for search engines
- internal links that point at the wrong site shape
- image paths that work in one repo but break in the other

This runbook exists to keep the workflow simple and repeatable.

## First principles

1. **One article should have one canonical home.**
   Search engines and future editors both need a single source of truth.

2. **The personal site is source-driven from root `content/`.**
   Generated files under `site/src/content/**` are build artifacts, not authoring files.

3. **The engineering site already has a repost model.**
   That repo understands `sourceType: repost`, `sourceUrl`, and `canonicalUrl`.

4. **The personal site does not have repost metadata yet.**
   It always treats articles as local canonical pages.

Because of those constraints, the supported direction today is:

```text
ashwch.com owns the full article
           ↓
engineering.diversio.com carries a short repost stub
```

If product requirements change, change the code model first. Do not fake a reverse
workflow in content.

## Mental model

Think of the two repos like this:

```text
ashwch.github.io                         engineering-website
-----------------                        -------------------
content/articles/<slug>.md              src/content/blog/<slug>.md
        │                                       │
        │ full article                          │ short repost stub
        ▼                                       ▼
site/src/content/articles/<slug>.md     /blog/<slug>/
(generated)                             on engineering.diversio.com
        │
        ▼
/<slug>.html
on ashwch.com
```

And article assets flow like this on the personal site:

```text
content/images/articles/<slug>/diagram.svg
        │
        │ pnpm sync:assets
        ▼
site/public/images/articles/<slug>/diagram.svg
        │
        ▼
/images/articles/<slug>/diagram.svg
in the built site
```

## When to use this workflow

Use this workflow when all of these are true:

- the article is authored for Ashwini's personal site
- the full body should keep its long-term canonical home on `ashwch.com`
- the engineering site should still surface it to engineering readers

## Personal-site workflow

### Step 1: Add the full article source file

Create:

- `content/articles/<slug>.md`

Use the legacy metadata format this repo already expects:

```md
Title: My Article Title
Date: 2026-05-20
Modified: 2026-05-20
Category: Engineering
Tags: engineering, ai, workflow
Slug: my-article-title
Authors: Ashwini Chaudhary
Summary: One-sentence summary.
```

### Why this format exists

This repo still uses a migration script that reads the old metadata style and
rewrites it into Astro frontmatter during sync.

So:

- edit `content/articles/*.md`
- do **not** hand-edit `site/src/content/articles/*.md`
- do **not** switch one article to YAML frontmatter unless the pipeline changes

### Step 2: Add article images in the right place

Create:

- `content/images/articles/<slug>/`

Reference them from the article like this:

```html
<img src="{static}/images/articles/<slug>/diagram.svg" alt="...">
```

### Why this path shape exists

The personal-site sync pipeline rewrites `{static}/images/...` into a public site
path during build.

That means:

- **source markdown** should use `{static}/images/...`
- **built HTML** will use `/images/...`

### Step 3: Rewrite links for the personal-site URL model

The personal site does **not** use `/blog/<slug>/` article URLs.
It uses `/<slug>.html`.

So when you port a full article into this repo, rewrite links like this:

```text
Before: /blog/the-monolith-that-made-ai-actually-useful/
After:  /the-monolith-that-made-ai-actually-useful.html
```

If the article needs to link back to engineering-site docs or skills pages, use
absolute URLs instead of local `/docs/...` paths:

```text
Before: /docs/code-review-digest-writer
After:  https://engineering.diversio.com/docs/code-review-digest-writer/
```

### Why this matters

Relative route shapes are different across the two repos.
What works on the engineering site can silently become a broken or misleading link
on the personal site.

### Step 4: Validate locally

From `site/` run:

```bash
pnpm check
pnpm build
```

If you stay inside `site/`, useful spot checks are:

```bash
rg -n 'canonical' dist/<slug>.html
rg -n '/images/articles/<slug>/' dist/<slug>.html
```

Expected result:

- canonical URL is `https://ashwch.com/<slug>.html`
- article images resolve from `/images/articles/<slug>/...`

## Engineering-site follow-up

After the personal site is correct, update your `engineering-website` checkout.

Create or convert:

- `src/content/blog/<slug>.md`

Use a short repost stub with these fields:

```yaml
sourceType: repost
sourceSiteName: ashwch.com
sourceUrl: https://ashwch.com/<slug>.html
canonicalUrl: https://ashwch.com/<slug>.html
```

Body shape:

- one line saying it was originally published on `ashwch.com`
- one short excerpt or setup paragraph
- one “Read the full post on ashwch.com →” link

### Why the engineering copy should stay short

The engineering repo is not the canonical owner in this workflow.
Keeping a short stub prevents drift and makes the ownership obvious to both readers
and future editors.

### Editorial recommendation

Repost stubs usually should **not** keep `featured: true` unless there is a
specific editorial reason to feature a link-out card.

### Validate the engineering-side stub too

From your `engineering-website` checkout run:

```bash
npm run build
```

Useful spot checks there:

```bash
rg -n 'canonical' dist/blog/<slug>/index.html
rg -n 'ashwch.com/<slug>.html' dist/blog/<slug>/index.html
```

Expected result:

- the engineering blog page builds successfully
- the canonical URL points to `https://ashwch.com/<slug>.html`
- the page body stays short and links to the canonical article

## Common mistakes to avoid

### Do not do this

```text
✗ Edit site/src/content/articles/<slug>.md directly
✓ Edit content/articles/<slug>.md
```

```text
✗ Leave /blog/<slug>/ links inside the personal canonical copy
✓ Rewrite them to /<slug>.html
```

```text
✗ Use local /docs/... links in the personal article when the target lives on the engineering site
✓ Use absolute https://engineering.diversio.com/docs/... URLs
```

```text
✗ Keep two full article bodies in both repos without a clear reason
✓ Keep one full body and one short repost stub
```

## If requirements change

If you want this instead:

```text
engineering.diversio.com owns the full article
           ↓
ashwch.com carries a repost or external canonical
```

stop and add product/code support first.

Today the personal-site repo always emits local `ashwch.com` canonicals for
articles and does not have a repost content model.

That is a code-model limitation, not an editorial preference.
