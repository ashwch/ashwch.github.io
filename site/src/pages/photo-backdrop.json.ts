import { homepageBanners } from '../data/homepageBanners';
import { getVisiblePhotos } from '../lib/photography';

export const prerender = true;

export function GET() {
  const photos = [
    ...homepageBanners.map((banner) => ({
      src: banner.mobileSrc,
      width: 900,
      height: 1125,
    })),
    ...getVisiblePhotos().map((photo) => ({
      src: photo.urls.small,
      width: photo.width,
      height: photo.height,
    })),
  ];

  return new Response(JSON.stringify(photos), {
    headers: {
      'Cache-Control': 'public, max-age=86400',
      'Content-Type': 'application/json; charset=utf-8',
    },
  });
}
