/**
 * /photo-pool.json
 *
 * The photo pool (see lib/photoPool.ts) in a compact form, for the scripts
 * that rotate photos in the browser: the homepage hero and mosaic, and the
 * page photo band. Pages render their first photos on the server and fetch
 * this file afterwards, so the long list never slows the first paint.
 *
 * Each entry is [path, title, isWide (1 or 0), colour]. Short arrays keep the
 * file small; there are well over a thousand entries.
 */
import { getPhotoPool } from '../lib/photoPool';

export const prerender = true;

export function GET() {
  const entries = getPhotoPool().map((photo) => [photo.path, photo.title, photo.isWide ? 1 : 0, photo.color]);

  return new Response(JSON.stringify(entries), {
    headers: {
      'Cache-Control': 'public, max-age=86400',
      'Content-Type': 'application/json; charset=utf-8',
    },
  });
}
