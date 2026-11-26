<script setup lang="ts">
// Segar Cobra configurator: paint, stripes, wheels, interior, options.
// No prices are published, so the summary shows "Price on request".
// The configuration is kept in the URL so it can be shared.
import { computed, onMounted, reactive, ref, watch } from 'vue';
import { sideView, topView } from '../lib/roadsterArt';

interface Choice { id: string; name: string; hex: string; original?: boolean; photo?: string }
interface Option { id: string; name: string; default?: boolean }
const props = defineProps<{
  car: string; instagramDm: string; note: string; photoNote?: string; photoBase?: string;
  paints: Choice[]; stripes: Choice[]; wheels: Choice[]; interiors: Choice[]; options: Option[];
}>();

const first = (list: Choice[]) => (list.find((c) => c.original) ?? list[0]).id;
const cfg = reactive({
  paint: first(props.paints), stripe: first(props.stripes), wheel: first(props.wheels), interior: first(props.interiors),
  opts: props.options.filter((o) => o.default).map((o) => o.id),
});
const step = ref<'exterior' | 'wheels' | 'interior' | 'options' | 'summary'>('exterior');
const view = ref<'photo' | '3d' | 'side' | 'top'>('photo');
const copied = ref('');

onMounted(() => {
  const q = new URLSearchParams(location.search);
  const pick = (list: Choice[], key: string, cur: string) => (list.some((c) => c.id === q.get(key)) ? q.get(key)! : cur);
  cfg.paint = pick(props.paints, 'paint', cfg.paint);
  cfg.stripe = pick(props.stripes, 'stripe', cfg.stripe);
  cfg.wheel = pick(props.wheels, 'wheel', cfg.wheel);
  cfg.interior = pick(props.interiors, 'interior', cfg.interior);
  if (q.has('opts')) cfg.opts = (q.get('opts') ?? '').split(',').filter((id) => props.options.some((o) => o.id === id));
});
watch(cfg, () => {
  const q = new URLSearchParams({ paint: cfg.paint, stripe: cfg.stripe, wheel: cfg.wheel, interior: cfg.interior, opts: cfg.opts.join(',') });
  history.replaceState(null, '', `?${q}`);
  copied.value = '';
}, { deep: true });

const find = (list: Choice[], id: string) => list.find((c) => c.id === id)!;
const paint = computed(() => find(props.paints, cfg.paint));
const stripe = computed(() => find(props.stripes, cfg.stripe));
const wheel = computed(() => find(props.wheels, cfg.wheel));
const interior = computed(() => find(props.interiors, cfg.interior));
const look = computed(() => ({
  paint: paint.value.hex, stripe: stripe.value.hex, wheel: wheel.value.hex, interior: interior.value.hex,
  rollbar: cfg.opts.includes('rollbar'), sidepipes: cfg.opts.includes('sidepipes'),
}));
const art = computed(() => (view.value === 'side' ? sideView(look.value) : topView(look.value)));
// Photo view: one photo per body colour × stripe (/img/cfg/ext-<paint>-<stripe>.jpg),
// plus a wheel close-up on the Wheels tab and the cockpit on the Interior tab.
const photos = computed(() => (props.photoBase ? [1] : props.paints.filter((p) => p.photo)));
const photoKind = computed(() => (step.value === 'wheels' ? 'wheel' : step.value === 'interior' ? 'interior' : 'ext'));
const currentPhoto = computed(() => {
  if (!props.photoBase) return paint.value.photo ?? '';
  if (photoKind.value === 'wheel') return `${props.photoBase}/wheel-${cfg.wheel}.jpg`;
  if (photoKind.value === 'interior') return `${props.photoBase}/interior-${cfg.interior}.jpg`;
  return `${props.photoBase}/ext-${cfg.paint}-${cfg.stripe}.jpg`;
});
const photoAlt = computed(() =>
  photoKind.value === 'wheel' ? `${wheel.value.name} close-up`
  : photoKind.value === 'interior' ? `${interior.value.name} cockpit`
  : `${props.car} in ${paint.value.name} with ${stripe.value.name.toLowerCase()}`);
// Images stay in the DOM once shown, so switching back crossfades instantly.
const shown = ref<string[]>([]);
watch(currentPhoto, (src) => { if (src && !shown.value.includes(src)) shown.value.push(src); }, { immediate: true });
onMounted(() => {
  if (!props.photoBase) return;
  // Warm the cache for the other stripe options of the current colour.
  for (const s of props.stripes) new Image().src = `${props.photoBase}/ext-${cfg.paint}-${s.id}.jpg`;
});

const summaryText = computed(() => [
  `${props.car} configuration`,
  `Body: ${paint.value.name}`,
  `Stripes: ${stripe.value.name}`,
  `Wheels: ${wheel.value.name}`,
  `Interior: ${interior.value.name}`,
  `Options: ${props.options.filter((o) => cfg.opts.includes(o.id)).map((o) => o.name).join(', ') || 'none'}`,
  typeof location !== 'undefined' ? location.href : '',
].join('\n'));

async function copy(what: 'text' | 'link') {
  try {
    await navigator.clipboard.writeText(what === 'text' ? summaryText.value : location.href);
    copied.value = what;
  } catch { copied.value = ''; }
}
function toggle(id: string) {
  const i = cfg.opts.indexOf(id);
  i >= 0 ? cfg.opts.splice(i, 1) : cfg.opts.push(id);
}
const steps = ['exterior', 'wheels', 'interior', 'options', 'summary'] as const;
</script>

<template>
  <div class="cfg">
    <div class="stage">
      <div class="views" role="group" aria-label="View">
        <button v-if="photos.length" type="button" :aria-pressed="view === 'photo'" @click="view = 'photo'">Photo</button>
        <button type="button" :aria-pressed="view === '3d'" @click="view = '3d'">3D</button>
        <button type="button" :aria-pressed="view === 'side'" @click="view = 'side'">Side</button>
        <button type="button" :aria-pressed="view === 'top'" @click="view = 'top'">Top</button>
      </div>
      <div v-if="view === 'photo' && currentPhoto" class="photo" :class="photoKind">
        <img v-for="src in shown" :key="src" :src="src" :alt="src === currentPhoto ? photoAlt : ''"
          :class="{ on: src === currentPhoto }" :aria-hidden="src !== currentPhoto" decoding="async" />
      </div>
      <div v-else-if="view === '3d'" class="model">
        <model-viewer src="/3d/segar-cobra.glb" alt="3D model of the Segar Cobra" camera-controls auto-rotate
          rotation-per-second="20deg" shadow-intensity="1" exposure="1.1" environment-image="neutral"
          camera-orbit="240deg 75deg 85%" ar ar-modes="webxr scene-viewer quick-look" />
        <p class="caption small-note">3D preview shows the original Jet Black car (AI-generated from a photo). Your colour choices appear in the Photo view.</p>
      </div>
      <div v-else class="art" v-html="art" />
      <p class="caption">{{ paint.name }} · {{ stripe.name }} · {{ wheel.name }}</p>
      <p v-if="view === 'photo' && props.photoNote" class="caption small-note">{{ props.photoNote }}</p>
    </div>

    <div class="panel">
      <div class="steps" role="tablist" aria-label="Configuration steps">
        <button v-for="s in steps" :key="s" type="button" role="tab" :aria-selected="step === s" @click="step = s">{{ s }}</button>
      </div>

      <div v-if="step === 'exterior'" role="tabpanel">
        <h2>Body colour</h2>
        <div class="swatches">
          <button v-for="c in props.paints" :key="c.id" type="button" class="swatch" :style="{ background: c.hex }"
            :aria-pressed="cfg.paint === c.id" :aria-label="c.name" :title="c.name" @click="cfg.paint = c.id" />
        </div>
        <p class="pick">{{ paint.name }}<span v-if="paint.original" class="muted"> · as on the first car</span></p>
        <h2>Stripes</h2>
        <div class="swatches">
          <button v-for="c in props.stripes" :key="c.id" type="button" class="swatch" :class="{ none: !c.hex }"
            :style="c.hex ? { background: `linear-gradient(90deg, ${paint.hex} 0 30%, ${c.hex} 30% 45%, ${paint.hex} 45% 55%, ${c.hex} 55% 70%, ${paint.hex} 70%)` } : {}"
            :aria-pressed="cfg.stripe === c.id" :aria-label="c.name" :title="c.name" @click="cfg.stripe = c.id" />
        </div>
        <p class="pick">{{ stripe.name }}<span v-if="stripe.original" class="muted"> · as on the first car</span></p>
      </div>

      <div v-else-if="step === 'wheels'" role="tabpanel">
        <h2>Wheels</h2>
        <ul class="opts">
          <li v-for="c in props.wheels" :key="c.id">
            <label><input type="radio" name="wheel" :checked="cfg.wheel === c.id" @change="cfg.wheel = c.id" />
              <span class="dot" :style="{ background: c.hex }" /><span>{{ c.name }}</span>
              <span class="muted">{{ c.original ? 'As on the first car' : '' }}</span></label>
          </li>
        </ul>
      </div>

      <div v-else-if="step === 'interior'" role="tabpanel">
        <h2>Interior</h2>
        <ul class="opts">
          <li v-for="c in props.interiors" :key="c.id">
            <label><input type="radio" name="interior" :checked="cfg.interior === c.id" @change="cfg.interior = c.id" />
              <span class="dot" :style="{ background: c.hex }" /><span>{{ c.name }}</span>
              <span class="muted">{{ c.original ? 'As on the first car' : '' }}</span></label>
          </li>
        </ul>
      </div>

      <div v-else-if="step === 'options'" role="tabpanel">
        <h2>Options</h2>
        <ul class="opts">
          <li v-for="o in props.options" :key="o.id">
            <label><input type="checkbox" :checked="cfg.opts.includes(o.id)" @change="toggle(o.id)" />
              <span /><span>{{ o.name }}</span><span class="muted">{{ o.default ? 'As on the first car' : '' }}</span></label>
          </li>
        </ul>
      </div>

      <div v-else role="tabpanel">
        <h2>Your {{ props.car }}</h2>
        <dl class="summary">
          <div><dt>Body</dt><dd>{{ paint.name }}</dd></div>
          <div><dt>Stripes</dt><dd>{{ stripe.name }}</dd></div>
          <div><dt>Wheels</dt><dd>{{ wheel.name }}</dd></div>
          <div><dt>Interior</dt><dd>{{ interior.name }}</dd></div>
          <div v-for="o in props.options" :key="o.id"><dt>{{ o.name }}</dt><dd>{{ cfg.opts.includes(o.id) ? 'Yes' : 'No' }}</dd></div>
        </dl>
        <div class="actions">
          <a class="btn btn-primary" :href="props.instagramDm" target="_blank" rel="noopener" @click="copy('text')">Send on Instagram</a>
          <button type="button" class="btn ghost" @click="copy('text')">{{ copied === 'text' ? 'Copied ✓' : 'Copy configuration' }}</button>
          <button type="button" class="btn ghost" @click="copy('link')">{{ copied === 'link' ? 'Link copied ✓' : 'Copy link' }}</button>
        </div>
        <p class="muted small">“Send on Instagram” copies your configuration and opens a chat with us. Paste it into the message.</p>
      </div>

      <div class="total">
        <span>Price</span><strong>On request</strong>
      </div>
      <p class="muted small">{{ props.note }}</p>
    </div>
  </div>
</template>

<style scoped>
.cfg { display: grid; gap: 32px; }
@media (min-width: 1000px) { .cfg { grid-template-columns: 1.45fr 1fr; align-items: start; } .stage { position: sticky; top: 24px; } }
.stage { position: relative; padding: 56px 24px 20px; border-radius: var(--radius-l); background: radial-gradient(100% 90% at 50% 25%, var(--surface), var(--bg)); }
.views { position: absolute; top: 14px; right: 14px; display: flex; gap: 4px; padding: 4px; border-radius: 999px; background: var(--bg); }
.views button { font: inherit; font-size: 0.875rem; padding: 6px 14px; border: 0; border-radius: 999px; background: none; color: inherit; cursor: pointer; }
.views button[aria-pressed='true'] { background: var(--contrast); color: var(--on-contrast); }
.art :deep(svg) { width: 100%; height: auto; display: block; }
.photo { position: relative; aspect-ratio: 4 / 3; width: 100%; margin: 0 auto; border-radius: var(--radius-m); overflow: hidden; background: #ddd; }
.photo img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: 50% 88%; opacity: 0; transition: opacity 0.45s ease; }
.photo img.on { opacity: 1; }
.model model-viewer { width: 100%; height: min(60vh, 520px); --poster-color: transparent; }
.photo.wheel img { object-position: 50% 75%; }
.photo.interior img { object-position: 50% 50%; }
.small-note { font-size: 0.75rem; max-width: 60ch; margin: 6px auto 0; }
.art :deep(svg path), .art :deep(svg rect), .art :deep(svg circle) { transition: fill 0.35s ease; }
.caption { text-align: center; font-size: 0.875rem; color: var(--text-muted); margin: 8px 0 0; }
.panel { display: grid; gap: 16px; }
.steps { display: flex; gap: 4px; padding: 4px; border-radius: var(--radius-m); background: var(--surface); overflow-x: auto; }
.steps button { flex: 1; font: inherit; text-transform: capitalize; padding: 10px 12px; border: 0; border-radius: var(--radius-s); background: none; color: inherit; cursor: pointer; white-space: nowrap; }
.steps button[aria-selected='true'] { background: var(--contrast); color: var(--on-contrast); }
h2 { font-size: 1.125rem; font-weight: 600; margin: 16px 0 12px; }
.swatches { display: flex; flex-wrap: wrap; gap: 10px; }
.swatch { width: 46px; height: 46px; border-radius: 50%; border: 2px solid var(--border); cursor: pointer; padding: 0; }
.swatch.none { background: repeating-linear-gradient(45deg, var(--surface) 0 6px, var(--border) 6px 8px); }
.swatch[aria-pressed='true'] { outline: 2px solid var(--text); outline-offset: 3px; }
.pick { margin: 12px 0 0; }
.opts { list-style: none; padding: 0; margin: 0; display: grid; gap: 8px; }
.opts label { display: grid; grid-template-columns: auto auto 1fr auto; gap: 12px; align-items: center; cursor: pointer; padding: 14px 16px; border-radius: var(--radius-m); background: var(--surface); }
.opts input { width: 18px; height: 18px; accent-color: var(--contrast); }
.opts .muted { font-size: 0.8125rem; }
.dot { width: 22px; height: 22px; border-radius: 50%; border: 1px solid var(--border); }
.summary { margin: 0; }
.summary div { display: flex; justify-content: space-between; gap: 16px; padding: 12px 0; border-bottom: 1px solid var(--border); }
.summary dd { margin: 0; font-weight: 500; text-align: right; }
.actions { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 20px; }
.ghost { border-color: var(--border); background: none; color: inherit; }
.small { font-size: 0.8125rem; margin: 0; }
.total { display: flex; justify-content: space-between; align-items: baseline; padding: 18px 20px; border-radius: var(--radius-m); background: var(--contrast); color: var(--on-contrast); }
.total strong { font-size: 1.375rem; font-weight: 500; }
</style>
