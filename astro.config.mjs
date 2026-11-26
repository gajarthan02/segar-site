import { defineConfig } from 'astro/config';
import vue from '@astrojs/vue';

// Same shape as the reference site: static HTML from Astro, with small Vue
// "islands" that hydrate only where interactivity is needed.
export default defineConfig({
  integrations: [vue({ template: { compilerOptions: { isCustomElement: (tag) => tag === 'model-viewer' } } })],
});
