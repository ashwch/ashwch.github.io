import { cp, mkdir, rm } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SITE_ROOT = path.resolve(__dirname, '..');
const REPO_ROOT = path.resolve(SITE_ROOT, '..');

const PUBLIC_DIR = path.join(SITE_ROOT, 'public');
const SOURCE_IMAGES = path.join(REPO_ROOT, 'content', 'images');
const SOURCE_CNAME = path.join(REPO_ROOT, 'content', 'extra', 'CNAME');
const TARGET_IMAGES = path.join(PUBLIC_DIR, 'images');
const TARGET_CNAME = path.join(PUBLIC_DIR, 'CNAME');

async function main() {
  await mkdir(PUBLIC_DIR, { recursive: true });
  await rm(TARGET_IMAGES, { recursive: true, force: true });
  await cp(SOURCE_IMAGES, TARGET_IMAGES, {
    recursive: true,
    force: true,
    filter(source) {
      return !source.endsWith('.DS_Store');
    },
  });
  await cp(SOURCE_CNAME, TARGET_CNAME, { force: true });
  console.log('Synced static assets into Astro public/.');
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
