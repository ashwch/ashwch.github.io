import { readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SITE_ROOT = path.resolve(__dirname, '..');
const REPO_ROOT = path.resolve(SITE_ROOT, '..');
const SOURCE_METADATA = path.join(REPO_ROOT, 'content', 'images', 'photography', 'gallery_metadata.json');
const TARGET_DATASET = path.join(SITE_ROOT, 'src', 'data', 'photography', 'generated', 'unsplash-photos.json');

const REFERRAL = 'https://unsplash.com/@suicide_chewbacca?utm_source=ashwch.com&utm_medium=referral';

function slugify(value) {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

function pickDescription(item) {
  return item.ai_analysis?.descriptions?.find((value) => value && value.length > 80)
    || item.description
    || item.ai_analysis?.caption
    || item.title;
}

function mapPhoto([filename, item], index) {
  const stem = filename.replace(/\.[^.]+$/, '');
  const title = (item.title || stem).replace(/\bS\b/g, 's');
  const date = item.exif?.datetime || item.processed || null;
  const coords = item.exif?.gps;
  const camera = item.exif?.camera || {};
  const settings = item.exif?.settings || {};

  return {
    id: `local-preview-${slugify(stem)}`,
    slug: slugify(title) || slugify(stem),
    title,
    description: pickDescription(item),
    alt: title,
    featured: index < 6,
    hidden: false,
    order: index + 1,
    categories: item.category ? [item.category] : [],
    color: null,
    blurHash: null,
    width: item.original_size?.[0] || 1600,
    height: item.original_size?.[1] || 1200,
    createdAt: date,
    updatedAt: date,
    publishedAt: date,
    location: coords
      ? {
          title: coords.location || coords.coordinates,
          name: coords.location || coords.coordinates,
          city: null,
          country: null,
          position: {
            latitude: coords.latitude ?? null,
            longitude: coords.longitude ?? null,
          },
        }
      : null,
    exif: {
      make: camera.make || null,
      model: camera.model || null,
      name: camera.lens || null,
      aperture: settings.aperture || null,
      focalLength: settings.focal_length || null,
      exposureTime: settings.shutter || null,
      iso: settings.iso ? Number(String(settings.iso).replace(/[^0-9]/g, '')) || null : null,
    },
    urls: {
      raw: `/images/photography/${filename}`,
      full: `/images/photography/${filename}`,
      regular: `/images/photography/thumbnails/${stem}_large.jpg`,
      small: `/images/photography/thumbnails/${stem}_medium.jpg`,
      thumb: `/images/photography/thumbnails/${stem}_small.jpg`,
      smallS3: `/images/photography/thumbnails/${stem}_small.jpg`,
    },
    links: {
      html: REFERRAL,
      download: REFERRAL,
      downloadLocation: REFERRAL,
      user: REFERRAL,
      portfolio: REFERRAL,
    },
    user: {
      username: 'suicide_chewbacca',
      name: 'Ashwini Chaudhary',
    },
  };
}

const preferredOrder = [
  'MON02051 1.jpg',
  'MON01845.jpg',
  'MON02014 1.jpg',
  'MON02022 1.jpg',
  'MON03841.jpg',
  'dji_fly_20241223_230636_633_1735013793485_photo.jpg',
  'IMG_3197.JPG',
  'IMG_3760.JPG',
  'carved-wooden-door.jpg',
  'portrait-pink-hat.jpg',
];

async function main() {
  const metadata = JSON.parse(await readFile(SOURCE_METADATA, 'utf8'));
  const entries = preferredOrder
    .filter((filename) => metadata[filename])
    .map((filename) => [filename, metadata[filename]]);

  const photos = entries.map(mapPhoto);
  const dataset = {
    generatedAt: new Date().toISOString(),
    username: 'suicide_chewbacca',
    source: 'local-preview-seed',
    photos,
  };

  await writeFile(TARGET_DATASET, `${JSON.stringify(dataset, null, 2)}\n`);
  console.log(`Seeded ${photos.length} temporary preview photos into ${path.relative(SITE_ROOT, TARGET_DATASET)}.`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
