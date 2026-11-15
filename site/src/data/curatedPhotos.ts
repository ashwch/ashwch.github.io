/**
 * Hand-picked Unsplash photos for the homepage and the page photo band.
 *
 * WHY A HAND-PICKED LIST
 *
 *   Sorting by views alone surfaces portraits, hotel corridors and near-black
 *   night skies next to each other. These lists are chosen to work together:
 *   landscapes, night lights, architecture and small details, with a mix of
 *   warm and cool colours and no portraits of people.
 *
 * To change what shows up, add or remove Unsplash photo ids here. An id that is
 * no longer in the generated dataset is skipped.
 */
import { getVisiblePhotos, type Photo } from '../lib/photography';

/** Homepage mosaic. The first five are shown on load; the rest rotate in. */
const mosaicPhotoIds = [
  '75mmGvxnTzA', // green pine trees near river during daytime
  'gkIXFjDRyDc', // snow covered mountain under gray sky
  'O971R1OH4RU', // lighted candle in black round bowl
  'ng-jV5Etz3c', // brown wooden window on brown brick wall
  'oFesGhLE6HU', // person standing on snow covered ground during daytime
  'S6pJEsabbDw', // a mountain covered in snow and clouds under a gray sky
  '-32lKp1bi9k', // white round light on brown wooden table
  'w6enTLK1RFQ', // gray staidum
  'bsVt1_On_gk', // black bell on arch gate
  'EEsqZyA8b0E', // river in the middle of forest during daytime
  '0XNU5B9zwYY', // black and silver pendant lamp
  'q0jm87RaMR0', // red and white bokeh lights
  '1XygWzlmVB8', // selective focus photography of tower
  '7Hp4NAMDh-Y', // grey metal door close
  'hRp8OlHfZ9U', // person walking on snow covered ground
  'fUHkDnmXq1Q', // full moon at night
  '4SqmKiyeXbE', // bell hanging on rod
  'egeN7GYoONs', // red tractor on brown grass field during daytime
  'FM51Izc26xA', // a couple of cars that are sitting in the snow
  'fNkhcgZvv5I', // photo of stars during nighttime
];

/** Wide landscapes that crop well into the hero and the page photo band. */
const landscapePhotoIds = [
  '75mmGvxnTzA', // green pine trees near river during daytime
  'gkIXFjDRyDc', // snow covered mountain under gray sky
  'EEsqZyA8b0E', // river in the middle of forest during daytime
  'S6pJEsabbDw', // a mountain covered in snow and clouds under a gray sky
  'oFesGhLE6HU', // person standing on snow covered ground during daytime
  'bsVt1_On_gk', // black bell on arch gate
];

function findPhotos(ids: string[]): Photo[] {
  const photosById = new Map(getVisiblePhotos().map((photo) => [photo.id, photo]));
  return ids.flatMap((id) => {
    const photo = photosById.get(id);
    return photo ? [photo] : [];
  });
}

export function getMosaicPhotos() {
  return findPhotos(mosaicPhotoIds);
}

export function getLandscapePhotos() {
  return findPhotos(landscapePhotoIds);
}
