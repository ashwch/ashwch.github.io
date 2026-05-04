/**
 * Homepage hero banner data.
 *
 * Each banner represents a photography frame that rotates on the homepage hero.
 * We keep separate desktop and mobile crops so the important part of each photo
 * stays visible on both wide and tall screens.
 *
 *                              desktop (16:9)
 *  ┌────────────────────────────────────────────┐
 *  │                                            │
 *  │     full landscape photo                   │
 *  │     cropped at desktopPosition              │
 *  │                                            │
 *  └────────────────────────────────────────────┘
 *
 *                              mobile (4:3)
 *           ┌──────────────────────────┐
 *           │                          │
 *           │  narrower crop           │
 *           │  at mobilePosition       │
 *           │                          │
 *           └──────────────────────────┘
 *
 * desktopPosition / mobilePosition
 *   CSS object-position value that tells the browser which part of the image
 *   to keep in frame when the image is cropped by object-fit: cover.
 *   Example: "center 42%" means "horizontally centered, vertically 42% from top".
 *
 *   Bump the vertical % up to show more sky; push it down to show more foreground.
 */
export type HomepageBanner = {
  slug: string;
  title: string;
  desktopSrc: string;
  mobileSrc: string;
  desktopPosition?: string;
  mobilePosition?: string;
};

export const homepageBanners: HomepageBanner[] = [
  {
    slug: 'misty-fjord',
    title: 'Misty fjord at blue hour',
    desktopSrc: '/images/home-banners/misty-fjord-desktop.jpg',
    mobileSrc: '/images/home-banners/misty-fjord-mobile.jpg',
    desktopPosition: 'center 58%',
    mobilePosition: 'center 54%',
  },
  {
    slug: 'heritage-flight',
    title: 'Heritage flight over open sky',
    desktopSrc: '/images/home-banners/heritage-flight-desktop.jpg',
    mobileSrc: '/images/home-banners/heritage-flight-mobile.jpg',
    desktopPosition: 'center 42%',
    mobilePosition: '62% 42%',
  },
  {
    slug: 'comet-over-field',
    title: 'A comet cutting through the night',
    desktopSrc: '/images/home-banners/comet-over-field-desktop.jpg',
    mobileSrc: '/images/home-banners/comet-over-field-mobile.jpg',
    desktopPosition: 'center 44%',
    mobilePosition: 'center 38%',
  },
  {
    slug: 'toronto-at-dusk',
    title: 'Toronto under a violet dusk',
    desktopSrc: '/images/home-banners/toronto-at-dusk-desktop.jpg',
    mobileSrc: '/images/home-banners/toronto-at-dusk-mobile.jpg',
    desktopPosition: 'center 52%',
    mobilePosition: 'center 46%',
  },
  {
    slug: 'road-to-the-rockies',
    title: 'An open road into the Rockies',
    desktopSrc: '/images/home-banners/road-to-the-rockies-desktop.jpg',
    mobileSrc: '/images/home-banners/road-to-the-rockies-mobile.jpg',
    desktopPosition: 'center 52%',
    mobilePosition: 'center 50%',
  },
  {
    slug: 'dawn-centerline',
    title: 'Centerline at first light',
    desktopSrc: '/images/home-banners/dawn-centerline-desktop.jpg',
    mobileSrc: '/images/home-banners/dawn-centerline-mobile.jpg',
    desktopPosition: 'center 58%',
    mobilePosition: 'center 55%',
  },
  {
    slug: 'glacial-horizon',
    title: 'A glacial horizon over still water',
    desktopSrc: '/images/home-banners/glacial-horizon-desktop.jpg',
    mobileSrc: '/images/home-banners/glacial-horizon-mobile.jpg',
    desktopPosition: 'center 48%',
    mobilePosition: 'center 44%',
  },
  {
    slug: 'alpine-sweep',
    title: 'Clouds sliding across alpine ridges',
    desktopSrc: '/images/home-banners/alpine-sweep-desktop.jpg',
    mobileSrc: '/images/home-banners/alpine-sweep-mobile.jpg',
    desktopPosition: 'center 45%',
    mobilePosition: 'center 44%',
  },
  {
    slug: 'last-light-water',
    title: 'Last light settling over the water',
    desktopSrc: '/images/home-banners/last-light-water-desktop.jpg',
    mobileSrc: '/images/home-banners/last-light-water-mobile.jpg',
    desktopPosition: 'center 56%',
    mobilePosition: 'center 52%',
  },
  {
    slug: 'winter-switchbacks',
    title: 'Winter switchbacks from above',
    desktopSrc: '/images/home-banners/winter-switchbacks-desktop.jpg',
    mobileSrc: '/images/home-banners/winter-switchbacks-mobile.jpg',
    desktopPosition: 'center 48%',
    mobilePosition: 'center 46%',
  },
  {
    slug: 'cold-valley',
    title: 'A cold valley under mountain shadow',
    desktopSrc: '/images/home-banners/cold-valley-desktop.jpg',
    mobileSrc: '/images/home-banners/cold-valley-mobile.jpg',
    desktopPosition: 'center 46%',
    mobilePosition: 'center 46%',
  },
  {
    slug: 'starlit-ridge',
    title: 'A ridge lit only by stars',
    desktopSrc: '/images/home-banners/starlit-ridge-desktop.jpg',
    mobileSrc: '/images/home-banners/starlit-ridge-mobile.jpg',
    desktopPosition: 'center 42%',
    mobilePosition: 'center 40%',
  },
];
