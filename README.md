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
Hosted on GitHub Pages (repo `gajarthan02/segar-site`, branch `gh-pages`, domain `segar.bohar.online`
via `public/CNAME`). After changes: `npm run deploy` (builds and pushes `dist/` to `gh-pages`).
