import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SITE_ROOT = path.resolve(__dirname, '..');
const DATA_ROOT = path.join(SITE_ROOT, 'src', 'data', 'photography');
const GENERATED_PATH = path.join(DATA_ROOT, 'generated', 'unsplash-photos.json');
const OVERRIDES_PATH = path.join(DATA_ROOT, 'overrides.json');

const ACCESS_KEY = process.env.UNSPLASH_ACCESS_KEY;
const USERNAME = process.env.UNSPLASH_USERNAME || 'suicide_chewbacca';
const REFERRAL_SOURCE = process.env.UNSPLASH_REFERRAL_SOURCE || 'ashwch.com';

function slugify(value) {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 80);
}

function withReferral(url) {
  if (!url) return url;
  const joiner = url.includes('?') ? '&' : '?';
  return `${url}${joiner}utm_source=${encodeURIComponent(REFERRAL_SOURCE)}&utm_medium=referral`;
}

async function readJson(filePath, fallback) {
  try {
    return JSON.parse(await readFile(filePath, 'utf8'));
  } catch {
    return fallback;
  }
}

async function unsplash(pathname, search = new URLSearchParams()) {
  const url = new URL(`https://api.unsplash.com/${pathname}`);
  search.set('client_id', ACCESS_KEY);
  url.search = search.toString();

  const response = await fetch(url, {
    headers: {
      'Accept-Version': 'v1',
    },
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Unsplash API error ${response.status}: ${body}`);
  }

  return response.json();
}

async function fetchUserPhotos() {
  const photos = [];
  let page = 1;
  const perPage = 30;

  while (true) {
    const batch = await unsplash(`users/${USERNAME}/photos`, new URLSearchParams({
      page: String(page),
      per_page: String(perPage),
      stats: 'true',
    }));

    photos.push(...batch);
    if (batch.length < perPage) {
      break;
    }
    page += 1;
  }

  return photos;
}

async function fetchDetailsForPhotos(photos) {
  return Promise.all(
    photos.map((photo) => unsplash(`photos/${photo.id}`)),
  );
}

function buildStats(detail) {
  return detail.statistics
    ? {
        downloads: detail.statistics.downloads?.total ?? null,
        views: detail.statistics.views?.total ?? null,
        likes: detail.likes ?? null,
      }
    : {
        downloads: null,
        views: null,
        likes: detail.likes ?? null,
      };
}

function applyOverridesToPhoto(photo, override = {}) {
  const baseTitle = override.title || photo.title || `Photo ${photo.id}`;
  const title = baseTitle.length > 120 ? `${baseTitle.slice(0, 117)}...` : baseTitle;

  return {
    ...photo,
    slug: override.slug || slugify(title) || photo.id,
    title,
    description: override.description ?? photo.description ?? null,
    alt: override.alt ?? photo.alt ?? photo.description ?? title,
    featured: Boolean(override.featured),
    hidden: Boolean(override.hidden),
    order: override.order ?? null,
    categories: override.categories || photo.categories || [],
  };
}

function refreshCachedPhoto(photo, listPhoto, override = {}) {
  const refreshed = {
    ...photo,
    color: listPhoto.color ?? photo.color,
    blurHash: listPhoto.blur_hash ?? photo.blurHash,
    width: listPhoto.width ?? photo.width,
    height: listPhoto.height ?? photo.height,
    createdAt: listPhoto.created_at ?? photo.createdAt,
    updatedAt: listPhoto.updated_at ?? photo.updatedAt,
    publishedAt: listPhoto.promoted_at || listPhoto.created_at || photo.publishedAt,
    urls: listPhoto.urls
      ? {
          ...photo.urls,
          raw: listPhoto.urls.raw ?? photo.urls.raw,
          full: listPhoto.urls.full ?? photo.urls.full,
          regular: listPhoto.urls.regular ?? photo.urls.regular,
          small: listPhoto.urls.small ?? photo.urls.small,
          thumb: listPhoto.urls.thumb ?? photo.urls.thumb,
          smallS3: listPhoto.urls.small_s3 ?? photo.urls.smallS3,
        }
      : photo.urls,
    user: {
      username: listPhoto.user?.username ?? photo.user?.username ?? null,
      name: listPhoto.user?.name ?? photo.user?.name ?? null,
    },
    stats: buildStats(listPhoto),
  };

  return applyOverridesToPhoto(refreshed, override);
}

function partitionPhotosForDetails(photos, cachedPhotosById, overrides) {
  const reusedPhotos = [];
  const photosNeedingDetails = [];

  for (const photo of photos) {
    const cachedPhoto = cachedPhotosById.get(photo.id);
    if (cachedPhoto && cachedPhoto.updatedAt === photo.updated_at) {
      reusedPhotos.push(refreshCachedPhoto(cachedPhoto, photo, overrides[photo.id] || {}));
      continue;
    }
    photosNeedingDetails.push(photo);
  }

  return { reusedPhotos, photosNeedingDetails };
}

function normalizePhoto(detail, override = {}) {
  const baseTitle = override.title || detail.alt_description || detail.description || `Photo ${detail.id}`;
  const title = baseTitle.length > 120 ? `${baseTitle.slice(0, 117)}...` : baseTitle;
  const categories = override.categories || detail.topics?.map((topic) => topic.slug) || detail.tags?.map((tag) => tag.title?.toLowerCase()).filter(Boolean) || [];

  return {
    id: detail.id,
    slug: override.slug || slugify(title) || detail.id,
    title,
    description: override.description ?? detail.description ?? detail.alt_description ?? null,
    alt: override.alt ?? detail.alt_description ?? detail.description ?? title,
    featured: Boolean(override.featured),
    hidden: Boolean(override.hidden),
    order: override.order ?? null,
    categories,
    color: detail.color,
    blurHash: detail.blur_hash,
    width: detail.width,
    height: detail.height,
    createdAt: detail.created_at,
    updatedAt: detail.updated_at,
    publishedAt: detail.promoted_at || detail.created_at,
    location: detail.location
      ? {
          title: detail.location.title ?? null,
          name: detail.location.name ?? null,
          city: detail.location.city ?? null,
          country: detail.location.country ?? null,
          position: detail.location.position ?? null,
        }
      : null,
    exif: detail.exif
      ? {
          make: detail.exif.make ?? null,
          model: detail.exif.model ?? null,
          name: detail.exif.name ?? null,
          aperture: detail.exif.aperture ?? null,
          focalLength: detail.exif.focal_length ?? null,
          exposureTime: detail.exif.exposure_time ?? null,
          iso: detail.exif.iso ?? null,
        }
      : null,
    urls: {
      raw: detail.urls.raw,
      full: detail.urls.full,
      regular: detail.urls.regular,
      small: detail.urls.small,
      thumb: detail.urls.thumb,
      smallS3: detail.urls.small_s3,
    },
    links: {
      html: withReferral(detail.links.html),
      download: detail.links.download,
      downloadLocation: detail.links.download_location,
      user: withReferral(detail.user?.links?.html || `https://unsplash.com/@${USERNAME}`),
      portfolio: withReferral(`https://unsplash.com/@${USERNAME}`),
    },
    user: {
      username: detail.user?.username,
      name: detail.user?.name,
    },
    stats: buildStats(detail),
  };
}

function sortPhotos(photos) {
  return [...photos].sort((left, right) => {
    const leftHidden = left.hidden ? 1 : 0;
    const rightHidden = right.hidden ? 1 : 0;
    if (leftHidden !== rightHidden) return leftHidden - rightHidden;

    if (left.order !== null && right.order !== null && left.order !== right.order) {
      return left.order - right.order;
    }

    if (left.order !== null) return -1;
    if (right.order !== null) return 1;

    return new Date(right.publishedAt).getTime() - new Date(left.publishedAt).getTime();
  });
}

async function main() {
  if (!ACCESS_KEY) {
    console.error('UNSPLASH_ACCESS_KEY is required.');
    process.exit(1);
  }

  await mkdir(path.dirname(GENERATED_PATH), { recursive: true });
  const overrides = await readJson(OVERRIDES_PATH, {});
  const existingDataset = await readJson(GENERATED_PATH, { photos: [] });
  const cachedPhotosById = new Map((existingDataset.photos || []).map((photo) => [photo.id, photo]));

  const photos = await fetchUserPhotos();
  const { reusedPhotos, photosNeedingDetails } = partitionPhotosForDetails(photos, cachedPhotosById, overrides);
  const details = await fetchDetailsForPhotos(photosNeedingDetails);
  const fetchedPhotos = details.map((detail) => normalizePhoto(detail, overrides[detail.id] || {}));
  const normalized = sortPhotos([...reusedPhotos, ...fetchedPhotos]);

  await writeFile(
    GENERATED_PATH,
    `${JSON.stringify(
      {
        generatedAt: new Date().toISOString(),
        username: USERNAME,
        source: 'unsplash-api',
        photos: normalized,
      },
      null,
      2,
    )}\n`,
  );

  console.log(
    `Synced ${normalized.length} Unsplash photos into ${path.relative(SITE_ROOT, GENERATED_PATH)} ` +
      `(${reusedPhotos.length} reused, ${fetchedPhotos.length} fetched in detail).`,
  );
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
