# Segar Motorsports: Segar Cobra website

Car-maker-style website for the Segar Cobra, built with Astro 7.4.8 + Vue 3.5.45.

| Page | URL |
|---|---|
| Home (full-screen stage, tiles, model card, Discover) | `/` |
| Model page (key facts, in-page nav, design, cockpit, technical data) | `/segar-cobra/` |
| Configurator (paint, stripes, wheels, interior, options; side/top view; price on request; send via Instagram) | `/segar-cobra/configure/` |
| About & milestones | `/about/` |
| Gallery with full-screen viewer | `/gallery/` |
| Contact | `/contact/` |

Configurator choices are in `content/site.json` → `configurator`. The car drawing is `src/lib/roadsterArt.ts`.

```bash
cd ~/segar-site && nvm use 24
npm run dev      # http://localhost:4321
npm run build    # static site in dist/ (upload anywhere: Netlify, Cloudflare Pages, any web host)
```

## Edit content
All text is in `content/site.json`. Empty fields are hidden on the site:

| Field | Shown as |
|---|---|
| `phone`, `whatsapp`, `email`, `address` | Contact buttons (WhatsApp opens a chat) |
| `price` | A "Price" section |
| `stats`, `story`, `madeHere`, `features`, `gauges`, `switches`, `milestones` | Page sections |
| `gallery`, `guides` | Photo grids (files in `public/img/`, 1800 px + 800 px versions) |

Facts come from public posts (Instagram @segarmotorsports, Newswire, LinkedIn, Nov 2026).
Engine, power, gearbox, top speed and price were not published, so they are not on the site.

## Photos
`public/img/` holds web-sized copies of photos from @segarmotorsports
(originals: `~/Downloads/segar-motorsports/`). Replace them with the original
high-resolution files when available, and the logo (`logo.jpg`, 150 px) with a vector version.

## Configurator colour photos
`public/img/paint-<id>.jpg` are AI-edited versions of the Galle Fort photo (made with ChatGPT,
26 Nov 2026; originals in `~/Downloads/segar-motorsports/ai-renders/`). They show body colour only and
are labelled on the page as previews. To add a colour: add it to `configurator.paints` in
`content/site.json` with `"photo": "/img/paint-<id>.jpg"` and put the image in `public/img/`.
Replace them with real photos of painted cars when Segar has them.

## Publish
Run `npm run build` and upload the contents of `dist/` to any web host (static files, no PHP or database needed).

## Configurator photos (all combinations)
`public/img/cfg/`: `ext-<paint>-<stripe>.jpg` (6 colours × 5 stripe options; same-colour stripes reuse
the plain photo), `wheel-<silver|black|gold>.jpg` (silver is the real photo), `interior-<black|tan|red>.jpg`.
All except `wheel-silver` are AI-edited (ChatGPT, 26 Nov 2026) from Segar's own photos; originals in
`~/Downloads/segar-motorsports/ai-renders/`. The Photo view follows the active tab (Exterior/Options/Summary
show the car, Wheels shows the wheel, Interior shows the cockpit).

## 3D view
`public/3d/segar-cobra.glb` (1.8 MB, ~23k triangles) was generated from one photo with Microsoft TRELLIS
(Hugging Face demo, 26 Nov 2026; source image `3d-source/segar-3q-black.jpg`). Shown with Google
`<model-viewer>` 4.3.1 (CDN) on `/segar-cobra/#view-3d` and as the "3D" view in the configurator, with
drag/zoom, auto-rotate and phone AR. The unseen side and rear are AI guesses; replace with a proper
model (artist or scan) when available. It shows the original Jet Black only.

### 3D colours
`public/3d/tex/<paint>-<stripe>.jpg` (30 textures) are made by `python3 tools/recolor3d.py` from the
model's own texture: each texel is mapped to its 3D position, wheels/cockpit/grille are excluded, and only
body paint and stripes are recoloured using the paint/stripe hex values in `content/site.json`.
Re-run it after changing colours or replacing the model (`--debug` writes a colour-coded check model).
The configurator's 3D view and the colour dots on the car page swap these textures live.
