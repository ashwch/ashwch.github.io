import { cp, mkdir, rename, rm } from 'node:fs/promises';
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

async function movePathIfItExists(sourcePath, destinationPath) {
  try {
    await rename(sourcePath, destinationPath);
    return true;
  } catch (error) {
    if (error.code === 'ENOENT') {
      return false;
    }
    throw error;
  }
}

async function restoreBackup(backupPath, targetPath, removeOptions) {
  await rm(targetPath, removeOptions);
  try {
    await rename(backupPath, targetPath);
  } catch (error) {
    if (error.code !== 'ENOENT') {
      throw error;
    }
  }
}

async function replacePath(tempPath, targetPath, removeOptions) {
  let lastReplaceError;

  for (let attempt = 0; attempt < 3; attempt += 1) {
    const backupPath = path.join(
      path.dirname(targetPath),
      `.${path.basename(targetPath)}.backup-${process.pid}-${Date.now()}-${attempt}`,
    );
    let movedOriginalTarget = false;

    try {
      movedOriginalTarget = await movePathIfItExists(targetPath, backupPath);
      await rename(tempPath, targetPath);
      await rm(backupPath, removeOptions);
      return;
    } catch (error) {
      lastReplaceError = error;

      if (movedOriginalTarget) {
        await restoreBackup(backupPath, targetPath, removeOptions);
      }

      if (!['EEXIST', 'ENOTEMPTY'].includes(error.code)) {
        break;
      }
    } finally {
      await rm(backupPath, removeOptions);
    }
  }

  const errorDetails = lastReplaceError
    ? ` Last error: ${lastReplaceError.code ?? 'UNKNOWN'}${lastReplaceError.message ? ` - ${lastReplaceError.message}` : ''}`
    : '';
  throw new Error(`Could not replace ${targetPath} after 3 attempts.${errorDetails}`);
}

async function main() {
  await mkdir(PUBLIC_DIR, { recursive: true });

  const tempImagesDir = path.join(PUBLIC_DIR, `.images-sync-${process.pid}-${Date.now()}`);
  const tempCnamePath = path.join(PUBLIC_DIR, `.CNAME-sync-${process.pid}-${Date.now()}`);

  await rm(tempImagesDir, { recursive: true, force: true });
  await rm(tempCnamePath, { force: true });

  try {
    await cp(SOURCE_IMAGES, tempImagesDir, {
      recursive: true,
      force: true,
      filter(source) {
        return !source.endsWith('.DS_Store');
      },
    });
    await cp(SOURCE_CNAME, tempCnamePath, { force: true });

    await replacePath(tempImagesDir, TARGET_IMAGES, { recursive: true, force: true });
    await replacePath(tempCnamePath, TARGET_CNAME, { force: true });

    console.log('Synced static assets into Astro public/.');
  } finally {
    await rm(tempImagesDir, { recursive: true, force: true });
    await rm(tempCnamePath, { force: true });
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
