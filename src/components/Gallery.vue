<script setup lang="ts">
// Photo grid with a full-screen viewer: arrows / swipe / Esc, focus returns to the thumbnail.
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue';

interface Photo { src: string; thumb: string; w: number; h: number; alt: string }
const props = defineProps<{ photos: Photo[]; label: string }>();
const open = ref<number | null>(null);
const closeBtn = ref<HTMLButtonElement | null>(null);
const thumbs = ref<HTMLButtonElement[]>([]);
const current = computed(() => (open.value === null ? null : props.photos[open.value]));
let lastIndex = 0;
let touchX = 0;

const step = (d: number) => {
  if (open.value === null) return;
  open.value = (open.value + d + props.photos.length) % props.photos.length;
};
function onKey(e: KeyboardEvent) {
  if (e.key === 'Escape') open.value = null;
  else if (e.key === 'ArrowRight') step(1);
  else if (e.key === 'ArrowLeft') step(-1);
}
watch(open, async (v, old) => {
  if (v !== null && old === null) {
    lastIndex = v;
    document.body.style.overflow = 'hidden';
    window.addEventListener('keydown', onKey);
    await nextTick();
    closeBtn.value?.focus();
  } else if (v === null) {
    document.body.style.overflow = '';
    window.removeEventListener('keydown', onKey);
    thumbs.value[lastIndex]?.focus();
  } else {
    lastIndex = v;
  }
});
onBeforeUnmount(() => window.removeEventListener('keydown', onKey));
</script>

<template>
  <div>
    <ul class="grid">
      <li v-for="(p, i) in props.photos" :key="p.src" :class="{ tall: p.h > p.w }">
        <button ref="thumbs" type="button" :aria-label="`Open photo: ${p.alt}`" @click="open = i">
          <img :src="p.thumb" :alt="p.alt" loading="lazy" decoding="async" :width="p.w" :height="p.h" />
        </button>
      </li>
    </ul>

    <Teleport to="body">
      <div v-if="current" class="viewer" role="dialog" aria-modal="true" :aria-label="props.label"
        @click.self="open = null"
        @touchstart.passive="(e: TouchEvent) => (touchX = e.touches[0].clientX)"
        @touchend="(e: TouchEvent) => { const dx = e.changedTouches[0].clientX - touchX; if (Math.abs(dx) > 50) step(dx < 0 ? 1 : -1); }">
        <img :src="current.src" :alt="current.alt" />
        <p class="caption">{{ current.alt }} · {{ (open ?? 0) + 1 }} / {{ props.photos.length }}</p>
        <button ref="closeBtn" type="button" class="close" aria-label="Close" @click="open = null">✕</button>
        <button type="button" class="nav prev" aria-label="Previous photo" @click="step(-1)">‹</button>
        <button type="button" class="nav next" aria-label="Next photo" @click="step(1)">›</button>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.grid { list-style: none; margin: 0; padding: 0; display: grid; gap: 10px; grid-template-columns: repeat(auto-fill, minmax(min(100%, 260px), 1fr)); grid-auto-flow: dense; }
.grid li { aspect-ratio: 1; }
.grid li.tall { grid-row: span 2; aspect-ratio: auto; }
.grid button { display: block; width: 100%; height: 100%; padding: 0; border: 0; border-radius: var(--radius); overflow: hidden; cursor: zoom-in; background: var(--surface); }
.grid img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.6s var(--ease), opacity 0.3s; }
.grid button:hover img { transform: scale(1.04); }
.viewer { position: fixed; inset: 0; z-index: 100; display: grid; place-items: center; background: rgba(0, 0, 0, 0.94); padding: 56px 16px; }
.viewer img { max-width: 100%; max-height: calc(100svh - 120px); width: auto; height: auto; border-radius: 8px; }
.caption { position: absolute; bottom: 16px; left: 16px; right: 16px; text-align: center; margin: 0; color: #cfcfcf; font-size: 0.875rem; }
.close, .nav { position: absolute; border: 0; cursor: pointer; color: #fff; background: rgba(255, 255, 255, 0.12); border-radius: 50%; width: 48px; height: 48px; font-size: 1.5rem; }
.close { top: 12px; right: 12px; font-size: 1.1rem; }
.nav { top: 50%; transform: translateY(-50%); }
.prev { left: 12px; }
.next { right: 12px; }
.close:hover, .nav:hover { background: rgba(255, 255, 255, 0.24); }
</style>
