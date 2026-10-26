# Blog overview diagram

`dev-center-overview.svg` is the single, editable diagram embedded in the root article. It combines the article's main idea with the technical architecture: the GPUI window and owner-checked CLI socket call shared engines; the app owns PTYs, status and URL routing; monolith configuration, 1Password and Crafting feed separate worktree stacks. The landscape layout keeps these details in one figure rather than enlarging a handful of boxes. It needs no JavaScript, iframe or rendering library. Click the image in the article to open it at full size.

The five detailed diagrams now belong to the Dev Center repository:

- `docs/architecture/dev-center.html`
- `docs/architecture/overview.md`
- `scripts/test-architecture-diagrams.mjs`

They explain startup ordering, lifecycle safety and preview deployment step by step. The blog diagram shows how those components fit together without reproducing every workflow.

Edit the SVG directly, then run `pnpm check` and `pnpm build` from `site/`. Check the article at `/all-tools-should-now-have-two-users.html` on desktop and phone widths. The source facts were checked against Dev Center commit `f031fc7`; see its architecture overview and server runbook.
