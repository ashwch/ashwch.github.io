# Article Media: Galleries and the Lightbox

Use this runbook when an article needs several screenshots in one place, or when readers should be able to open an image full size without leaving the page.

## What the site does

`site/src/components/ArticleMedia.astro` runs on every article page (it is included from `site/src/pages/[slug].astro`). Its styles live in `site/src/styles/global.css` under the "Galleries" and "Lightbox" comments. There are no dependencies; it is plain TypeScript bundled by Astro.

- **Gallery:** a `<div class="gallery">` of figures becomes a carousel: one image at a time, swipe or scroll sideways on touch screens, arrow buttons, thumbnails (or dots), a `2 / 5` counter, and the arrow keys plus Home/End when the strip has focus.
- **Lightbox:** in an article body, any `<figure>` image wrapped in a link to an image file (`.webp`, `.png`, `.jpg`, `.jpeg`, `.gif`, `.avif`, `.svg`) opens in a full-screen viewer instead of navigating to the file. It has previous/next buttons, the arrow keys, swipes on touch screens, Esc or a click outside the image to close, and an "Open original" link. The caption is the image's `alt` text (the figure's `<figcaption>` if `alt` is empty).
  - Images in a gallery page through that gallery.
  - Other images page through the article's other single images.
  - Cmd/Ctrl/Shift-click still opens the file the browser's way.
- **Without JavaScript:** a gallery is a plain stack of figures and every link opens the image file. Nothing is hidden.

Both follow the site's light and dark themes.

## Source of truth

Edit root content files only:

- `content/articles/*.md`
- images in `content/images/articles/<article>/`

Do not hand-edit generated Astro content under `site/src/content/**`. `{static}/` in paths becomes `/` when the content is synced.

## Authoring a gallery

Raw HTML in the markdown, with no blank lines inside the block (a blank line ends a markdown HTML block):

```html
<div class="gallery" aria-label="A tour of the app">
<figure><a href="{static}/images/articles/my-post/one.webp"><img src="{static}/images/articles/my-post/one.webp" alt="What the screenshot shows, in a sentence." width="2400" height="1500" loading="lazy"></a><figcaption>Short caption.</figcaption></figure>
<figure><a href="{static}/images/articles/my-post/two.webp"><img src="{static}/images/articles/my-post/two.webp" alt="…" width="2400" height="1500" loading="lazy"></a><figcaption>…</figcaption></figure>
</div>
```

- `aria-label` names the carousel for screen readers.
- Each figure's link should point to the full-size image. The same file for both is fine.
- `alt` is the lightbox caption, so write it as a full description. Keep `<figcaption>` short; it sits under the image in the article.
- `width` and `height` are the image's real pixel size. They reserve space while it loads.
- Add `data-nav="dots"` to the gallery for dots instead of thumbnails (better for long galleries of similar images).
- A gallery needs at least two figures; a single figure is left as it is.
- Slides are framed at 16:10 and letterboxed. Images of mixed shapes are fine.

## Single images

Wrap the image in a link to the file and it gets the lightbox:

```html
<figure><a href="{static}/images/articles/my-post/one.webp"><img src="{static}/images/articles/my-post/one.webp" alt="…" loading="lazy"></a><figcaption>…</figcaption></figure>
```

To keep a link opening the file directly, put `data-no-lightbox` on the figure (or any parent).

## Images

- Use WebP. About 2400 px wide is enough for the lightbox on a retina screen; `cwebp -q 82 -resize 2400 0 in.png -o out.webp`.
- Check every screenshot before publishing: no secrets, tokens, client names, personal paths, account IDs or real branch names.

## Checking it

From `site/`, run `pnpm dev` and open the article. Check:

- desktop and a phone-width window, in light and dark;
- the arrows, thumbnails, keyboard (focus the strip, then arrow keys), and swiping;
- the lightbox: open, next/previous, Esc, click outside, and focus returning to the image;
- the browser console stays clean.

Then `pnpm check` and `pnpm build`.
