import type { APIContext } from 'astro';
import { getAllArticles, getCategoryIndex } from '../../lib/content';
import { createFeed } from '../../lib/feeds';

export async function getStaticPaths() {
  const articles = await getAllArticles();
  const categories = getCategoryIndex(articles);
  return categories.map((category) => ({
    params: { slug: category.slug },
    props: { category },
  }));
}

export async function GET({ props }: APIContext) {
  const { category } = props as {
    category: {
      label: string;
      slug: string;
      articles: Awaited<ReturnType<typeof getAllArticles>>;
    };
  };
  const feed = createFeed({
    title: `${category.label} · ashwch Atom Feed`,
    description: `Articles in the ${category.label} category.`,
    id: `https://ashwch.com/category/${category.slug}.html`,
    feedUrl: `https://ashwch.com/feeds/${category.slug}.atom.xml`,
    articles: category.articles,
  });

  return new Response(feed.atom1(), {
    headers: {
      'Content-Type': 'application/atom+xml; charset=utf-8',
    },
  });
}
