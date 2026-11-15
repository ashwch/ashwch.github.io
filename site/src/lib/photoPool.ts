/**
 * The photo pool: which of my Unsplash photos the site's rotating placements
 * (homepage hero, homepage mosaic, page photo band, article covers) draw from.
 *
 * WHY A POOL
 *
 *   The rotating placements used to cycle through a short hand-picked list,
 *   which got repetitive fast. The pool is nearly the whole portfolio, so the
 *   site keeps showing different photos.
 *
 * WHAT IS LEFT OUT, AND WHY
 *
 *   These placements crop photos hard (a wide band, a small tile) and often put
 *   text on top, so two kinds of photo are skipped. Both stay on the
 *   photography page, which shows everything uncropped.
 *
 *     Portraits of people   A wide crop of a portrait usually cuts through the
 *                           face. Detected from the photo's description.
 *                           Set INCLUDE_PEOPLE to true to allow them.
 *     Near-black frames     Night skies read as an empty black box behind text.
 *                           Detected from the photo's average colour.
 *
 * WIDE OR NOT
 *
 *   `isWide` photos (landscape orientation) suit the hero, the photo band and
 *   article covers. The mosaic's small tiles can use any orientation.
 */
import { getVisiblePhotos, type Photo } from './photography';

const INCLUDE_PEOPLE = false;
const MINIMUM_BRIGHTNESS = 0.16; // 0 is black, 1 is white
const WIDE_ASPECT_RATIO = 1.3;

const PEOPLE_WORDS =
  /\b(man|men|woman|women|person|people|boy|girl|child|children|kid|kids|baby|couple|bride|groom|family|lady|guy|toddler|infant|portrait|selfie|crowd|face|smiling)\b/i;

export type PoolPhoto = {
  /** Path on images.unsplash.com, without the query string. */
  path: string;
  /** Empty when Unsplash has no description for the photo. */
  title: string;
  color: string | null;
  isWide: boolean;
};

const IMAGE_HOST = 'https://images.unsplash.com/';

function brightness(color: string | null) {
  if (!color || !/^#[0-9a-f]{6}$/i.test(color)) return 1;
  const [red, green, blue] = [1, 3, 5].map((start) => Number.parseInt(color.slice(start, start + 2), 16));
  return (0.299 * red + 0.587 * green + 0.114 * blue) / 255;
}

function describe(photo: Photo) {
  // Photos without a description get a placeholder title like "Photo abc123".
  if (!photo.title || /^Photo \S+$/.test(photo.title)) return '';
  return photo.title.charAt(0).toUpperCase() + photo.title.slice(1).replace(/\.$/, '');
}

let pool: PoolPhoto[] | undefined;

export function getPhotoPool(): PoolPhoto[] {
  pool ??= getVisiblePhotos()
    .filter((photo) => photo.urls.raw.startsWith(IMAGE_HOST))
    .filter((photo) => INCLUDE_PEOPLE || !PEOPLE_WORDS.test(photo.title ?? ''))
    .filter((photo) => brightness(photo.color) > MINIMUM_BRIGHTNESS)
    .map((photo) => ({
      path: photo.urls.raw.slice(IMAGE_HOST.length).split('?')[0],
      title: describe(photo),
      color: photo.color,
      isWide: photo.width / photo.height >= WIDE_ASPECT_RATIO,
    }));
  return pool;
}

export function getWidePoolPhotos() {
  return getPhotoPool().filter((photo) => photo.isWide);
}

/** An Unsplash image URL for a pool photo. Unsplash crops and resizes on request. */
export function poolPhotoUrl(photo: Pick<PoolPhoto, 'path'>, parameters: string) {
  return `${IMAGE_HOST}${photo.path}?${parameters}`;
}
