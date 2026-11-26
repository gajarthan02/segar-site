<script setup lang="ts">
import { ref, watch, onBeforeUnmount } from 'vue';

const props = defineProps<{ items: { label: string; href: string }[]; brand: string }>();
const open = ref(false);
const closeBtn = ref<HTMLButtonElement | null>(null);

function onKey(e: KeyboardEvent) {
  if (e.key === 'Escape') open.value = false;
}
watch(open, (v) => {
  document.body.style.overflow = v ? 'hidden' : '';
  if (v) {
    window.addEventListener('keydown', onKey);
    requestAnimationFrame(() => closeBtn.value?.focus());
  } else {
    window.removeEventListener('keydown', onKey);
  }
});
onBeforeUnmount(() => window.removeEventListener('keydown', onKey));
</script>

<template>
  <div>
    <button class="burger" type="button" :aria-expanded="open" aria-controls="site-menu" @click="open = true">
      <span class="lines" aria-hidden="true"><i /><i /><i /></span>
      <span class="label">Menu</span>
    </button>
    <Transition name="fade"><div v-if="open" class="backdrop" @click="open = false" /></Transition>
    <Transition name="slide">
      <nav v-if="open" id="site-menu" class="drawer" :aria-label="`${props.brand} menu`">
        <button ref="closeBtn" class="close" type="button" aria-label="Close menu" @click="open = false">✕</button>
        <a class="feature" href="/segar-cobra/" @click="open = false">
          <img src="/img/palms-bw-800.jpg" alt="" />
          <span>Segar Cobra <small>Discover the car →</small></span>
        </a>
        <ul>
          <li v-for="item in props.items" :key="item.label">
            <a :href="item.href" @click="open = false">{{ item.label }}</a>
          </li>
        </ul>
      </nav>
    </Transition>
  </div>
</template>

<style scoped>
.burger { display: inline-flex; align-items: center; gap: 10px; background: none; border: 0; color: inherit; font: inherit; font-size: 1rem; cursor: pointer; padding: 6px; border-radius: var(--radius-s); }
.burger:hover { background: color-mix(in srgb, currentColor 14%, transparent); }
@media (max-width: 480px) { .label { display: none; } }
.lines { display: grid; gap: 4px; width: 16px; }
.lines i { display: block; height: 1.5px; background: currentColor; }
.backdrop { position: fixed; inset: 0; background: rgba(0, 0, 0, 0.5); z-index: 20; }
.drawer { position: fixed; inset: 0 auto 0 0; width: min(440px, 100vw); z-index: 21; background: var(--surface); color: var(--text); padding: 20px 28px; overflow-y: auto; }
.close { background: none; border: 0; color: inherit; font-size: 1.25rem; cursor: pointer; padding: 8px; }
.feature { display: block; position: relative; margin: 16px 0 8px; border-radius: var(--radius-m); overflow: hidden; color: #fff; text-decoration: none; aspect-ratio: 16 / 10; }
.feature img { width: 100%; height: 100%; object-fit: cover; }
.feature::after { content: ''; position: absolute; inset: 0; background: linear-gradient(transparent 40%, rgba(0,0,0,.7)); }
.feature span { position: absolute; z-index: 1; left: 16px; bottom: 14px; font-size: 1.375rem; }
.feature small { display: block; font-size: 0.875rem; opacity: 0.85; }
ul { list-style: none; padding: 0; margin: 16px 0 0; display: grid; }
ul a { display: block; padding: 14px 0; font-size: 1.5rem; text-decoration: none; border-bottom: 1px solid var(--border); }
ul a:hover { color: var(--text-muted); }
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.slide-enter-active, .slide-leave-active { transition: transform 0.35s cubic-bezier(0.25, 0.1, 0.25, 1); }
.slide-enter-from, .slide-leave-to { transform: translateX(-100%); }
</style>
