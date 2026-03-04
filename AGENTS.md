# AGENTS.md

This repository is the source for `https://ashwch.com`, generated with Pelican and published to GitHub Pages.

## Critical Deployment Rule

Pushing to `master` does **not** update the live site.

GitHub Pages is configured to serve from:

- Branch: `gh-pages`
- Path: `/`

Any content or theme change must be published to `gh-pages` after it is committed on `master`.

## Safe Publish Workflow

1. Commit and push source changes to `master`.
2. Build production output:
   - `./blog.sh build production`
   - or `uvx --with markdown --from pelican pelican content -o output -s publishconf.py -t theme`
3. Deploy output to `gh-pages`:
   - `./blog.sh deploy`
   - or `ghp-import -m "Deploy site YYYY-MM-DD HH:MM" -b gh-pages output && git push origin gh-pages`
4. Verify GitHub Pages build status:
   - `gh api repos/ashwch/ashwch.github.io/pages`
   - `gh api 'repos/ashwch/ashwch.github.io/pages/builds?per_page=1'`
5. Verify live page content with a cache-busting query string:
   - `curl -sL 'https://ashwch.com/pages/about.html?cb=YYYYMMDDHHMM'`

## Fast Checklist Before Marking Done

- [ ] Source branch (`master`) contains the intended commit(s)
- [ ] `gh-pages` has a new deploy commit
- [ ] Pages build status is `built` for that deploy commit
- [ ] Live HTML reflects the expected change

## Known Gotchas

- `make publish` only builds output; it does not deploy to GitHub Pages.
- `make github` deploy branch is controlled by `GITHUB_PAGES_BRANCH` in `Makefile`.
- GitHub Pages and CDN cache may delay visible updates for several minutes.
