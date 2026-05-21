# Article End Matter

Use this runbook when an article needs standardized footer-style notes at the end of the post.

Current supported blocks:

- review acknowledgements
- AI writing disclaimers

## Why this exists

These notes were starting to show up in different formats across posts.

The goal is to keep them:

- visually consistent
- easy to paste into future posts
- separate from the main article body
- subtle enough to read like end matter, not like a giant callout

## Source of truth

Edit root content files only:

- `content/articles/*.md`

Do not hand-edit generated Astro content under:

- `site/src/content/articles/*.md`

## Styling

Shared styling lives in:

- `site/src/styles/global.css`

The shared wrapper class is:

- `article-subtext`

Current modifiers are:

- `article-subtext--review`
- `article-subtext--ai`

## Standard snippets

### Review acknowledgement

Use raw HTML here so links are explicit and the block keeps one consistent structure.

```html
<div class="article-subtext article-subtext--review">
  <p class="article-subtext-label">Review</p>
  <p>Thanks to <a href="https://www.linkedin.com/in/person-one/">Person One</a> and <a href="https://www.linkedin.com/in/person-two/">Person Two</a> for reviewing this post.</p>
</div>
```

If only one reviewer is involved, keep the same structure and remove the second name.

If the acknowledgement needs one short extra clause, keep it practical and concise, for example:

```html
<div class="article-subtext article-subtext--review">
  <p class="article-subtext-label">Review</p>
  <p>Thanks to <a href="https://www.linkedin.com/in/person-one/">Person One</a> for reviewing this post and helping solidify the implementation.</p>
</div>
```

### AI writing disclaimer

```html
<div class="article-subtext article-subtext--ai">
  <p class="article-subtext-label">AI writing disclaimer</p>
  <ul>
    <li>The article was verified for typos and basic grammatical mistakes using ...</li>
    <li>References or supporting links were gathered with the help of ...</li>
    <li>Images, SVGs, or diagrams were generated using ...</li>
  </ul>
</div>
```

## Placement rules

Place these blocks near the end of the article, after the main content.

Good placements:

- after a `Related reading` section
- after a short closing paragraph
- before footnotes only when the acknowledgement is directly tied to the article body

## Tone rules

Keep these sections simple.

- no hype
- no long thank-you speeches
- no marketing phrasing
- no apology tone
- no over-explaining AI usage

These are end notes, not a second conclusion.

## Validation

From `site/` run:

```bash
pnpm check
pnpm build
```
