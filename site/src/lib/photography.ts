import rawDataset from '../data/photography/generated/unsplash-photos.json';

export type Photo = {
  id: string;
  slug: string;
  title: string;
  description: string | null;
  alt: string;
  featured: boolean;
  hidden: boolean;
  order: number | null;
  categories: string[];
  color: string | null;
  blurHash: string | null;
  width: number;
  height: number;
  createdAt: string;
  updatedAt: string;
  publishedAt: string;
  location: {
    title: string | null;
    name: string | null;
    city: string | null;
    country: string | null;
    position: {
      latitude: number | null;
      longitude: number | null;
    } | null;
  } | null;
  exif: {
    make: string | null;
    model: string | null;
    name: string | null;
    aperture: string | null;
    focalLength: string | null;
    exposureTime: string | null;
    iso: number | null;
  } | null;
  urls: {
    raw: string;
    full: string;
    regular: string;
    small: string;
    thumb: string;
    smallS3: string;
  };
  links: {
    html: string;
    download: string;
    downloadLocation: string;
    user: string;
    portfolio: string;
  };
  user: {
    username: string | null;
    name: string | null;
  };
};

export type PhotographyDataset = {
  generatedAt: string | null;
  username: string;
  source: string;
  photos: Photo[];
};

const dataset = rawDataset as PhotographyDataset;

export function getPhotographyDataset() {
  return dataset;
}

export function getVisiblePhotos() {
  return dataset.photos.filter((photo) => !photo.hidden);
}

export function getFeaturedPhotos(limit = 6) {
  const featured = getVisiblePhotos().filter((photo) => photo.featured);
  return (featured.length ? featured : getVisiblePhotos()).slice(0, limit);
}

export function getPhotographyCategories() {
  const categories = new Map<string, number>();

  for (const photo of getVisiblePhotos()) {
    for (const category of photo.categories || []) {
      categories.set(category, (categories.get(category) || 0) + 1);
    }
  }

  return [...categories.entries()]
    .map(([slug, count]) => ({ slug, label: slug.replace(/-/g, ' '), count }))
    .sort((left, right) => left.label.localeCompare(right.label));
}
