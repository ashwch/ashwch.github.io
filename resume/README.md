# Resume

Source of truth for the LaTeX resume lives here.

Template: [AltaCV](https://github.com/liantze/AltaCV)

## Published file

- Public PDF: `site/public/files/ashwini-chaudhary-resume.pdf`

## Files in this directory

- `ashwini-chaudhary-resume.tex` — the actual resume source
- `altacv.cls` — a vendored copy of the AltaCV class with small repository-specific patches
- `preview-altacv.html` — a simple local preview page that shows rendered images of the PDF
- `preview-assets/page-*.png` — page images generated from the latest PDF

## Why this setup exists

This repository intentionally keeps the resume flow simple.

First principles:

- the website should not depend on LaTeX to build
- the resume changes rarely
- the public site only needs the finished PDF
- local editing should stay understandable for future readers

So the repo stores both:

1. the editable LaTeX source
2. the generated PDF that the website links to

## Why `altacv.cls` is patched here

The vendored `altacv.cls` differs slightly from upstream.

We added small comments and patches for two practical reasons:

1. **Build reliability**
   - upstream AltaCV uses `pdfx`
   - that failed in this repository's XeLaTeX/Tectonic-based generation flow
   - we load `hyperref` directly instead, because reliable clickable PDFs matter more here than PDF/A features

2. **Cleaner PDF link hitboxes**
   - PDF viewers work with rectangular link annotations, not visual layout
   - if spacing is included inside the same box as a link, Preview.app can show confusing oversized hover/focus outlines
   - we moved spacing outside those boxes to keep link regions tighter and easier to reason about

## Workflow

The site does not build the resume automatically.

When the resume changes:

1. edit `resume/ashwini-chaudhary-resume.tex`
2. generate `site/public/files/ashwini-chaudhary-resume.pdf`
3. regenerate the local preview images/HTML if you want to visually inspect the result
4. commit the LaTeX source, PDF, and preview updates together

## Useful commands

### Open the generated PDF

```bash
open site/public/files/ashwini-chaudhary-resume.pdf
```

### Open the HTML preview

```bash
open resume/preview-altacv.html
```

### Rebuild the PDF and preview assets

This is the command used during recent editing sessions:

```bash
docker run --rm --platform linux/amd64 -v "$PWD":/work -w /work/resume ghcr.io/xu-cheng/texlive-full:latest \
  xelatex -interaction=nonstopmode -halt-on-error -output-directory=/work/site/public/files ashwini-chaudhary-resume.tex

docker run --rm --platform linux/amd64 -v "$PWD":/work -w /work/resume ghcr.io/xu-cheng/texlive-full:latest \
  xelatex -interaction=nonstopmode -halt-on-error -output-directory=/work/site/public/files ashwini-chaudhary-resume.tex

pdftoppm -png -r 160 site/public/files/ashwini-chaudhary-resume.pdf resume/preview-assets/page
```

Why two XeLaTeX runs?

- first pass builds the document and link metadata
- second pass resolves cross-document layout/link details cleanly

## Notes for future editors

- If the PDF page count changes, update `resume/preview-altacv.html` so it includes all `page-*.png` files.
- If link hover boxes look strange in Preview.app, inspect whether spacing has accidentally been moved back inside the clickable content.
- Prefer small, explicit layout structures over clever macros when debugging PDF annotation behavior.
