// Simple side and top views of a 1960s-style roadster, drawn as SVG so that body,
// stripe, wheel and interior colours can change live in the configurator.
// Stylised illustration of the Segar Cobra's layout, not a technical drawing.

export interface Look {
  paint: string;
  stripe: string; // '' = no stripes
  wheel: string;
  interior: string;
  rollbar: boolean;
  sidepipes: boolean;
}

const BODY =
  'M70 256 C56 238 60 210 92 200 C140 186 176 160 230 158 C286 156 316 176 362 180 L560 184 ' +
  'C602 184 622 152 670 150 C727 148 792 168 824 196 C840 211 838 240 828 258 ' +
  'L768 262 A68 68 0 0 0 632 262 L278 262 A68 68 0 0 0 142 262 Z';
const TOPLINE =
  'M92 200 C140 186 176 160 230 158 C286 156 316 176 362 180 L560 184 C602 184 622 152 670 150 C727 148 792 168 824 196';

function wheel(cx: number, cy: number, rim: string): string {
  const spokes = Array.from({ length: 24 }, (_, i) => {
    const a = (i / 24) * Math.PI * 2;
    return `<line x1="${cx + Math.cos(a) * 9}" y1="${cy + Math.sin(a) * 9}" x2="${cx + Math.cos(a + 0.5) * 36}" y2="${cy + Math.sin(a + 0.5) * 36}" />`;
  }).join('');
  return `<g>
    <circle cx="${cx}" cy="${cy}" r="58" fill="#0b0b0c"/>
    <circle cx="${cx}" cy="${cy}" r="40" fill="${rim}"/>
    <g stroke="#0b0b0c" stroke-opacity=".55" stroke-width="1.4">${spokes}</g>
    <circle cx="${cx}" cy="${cy}" r="38" fill="none" stroke="#0b0b0c" stroke-opacity=".35" stroke-width="3"/>
    <circle cx="${cx}" cy="${cy}" r="10" fill="${rim}" stroke="#0b0b0c" stroke-opacity=".5"/>
  </g>`;
}

export function sideView(l: Look, title = 'Segar Cobra side view'): string {
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 340" role="img"><title>${title}</title>
  <defs>
    <linearGradient id="sv-shine" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#fff" stop-opacity=".32"/><stop offset=".4" stop-color="#fff" stop-opacity="0"/>
      <stop offset="1" stop-color="#000" stop-opacity=".35"/>
    </linearGradient>
    <linearGradient id="sv-chrome" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#f4f5f7"/><stop offset=".5" stop-color="#9ea3aa"/><stop offset="1" stop-color="#e3e5e8"/>
    </linearGradient>
    <clipPath id="sv-body"><path d="${BODY}"/></clipPath>
  </defs>
  <ellipse cx="450" cy="318" rx="400" ry="14" fill="#000" fill-opacity=".22"/>
  ${l.rollbar ? `<path d="M468 186 C468 112 538 112 538 186" fill="none" stroke="url(#sv-chrome)" stroke-width="9" stroke-linecap="round"/>` : ''}
  <circle cx="210" cy="262" r="66" fill="#1a1a1c"/><circle cx="700" cy="262" r="66" fill="#1a1a1c"/>
  <path d="M398 184 C402 160 430 150 462 156 C478 160 488 172 492 184 Z" fill="${l.interior}"/>
  <path d="M494 184 C496 166 512 158 532 162 C544 166 548 176 548 184 Z" fill="${l.interior}"/>
  <path d="${BODY}" fill="${l.paint}"/>
  ${l.stripe ? `<g clip-path="url(#sv-body)"><path d="${TOPLINE}" fill="none" stroke="${l.stripe}" stroke-width="14"/></g>` : ''}
  <path d="${BODY}" fill="url(#sv-shine)"/>
  <path d="M376 182 L414 120 L426 122 L396 183 Z" fill="#9fb3c4" fill-opacity=".55" stroke="url(#sv-chrome)" stroke-width="3"/>
  <path d="M370 192 L372 248 M548 190 L548 248" stroke="#000" stroke-opacity=".28" stroke-width="2"/>
  <g fill="#000" fill-opacity=".55">
    <rect x="300" y="200" width="7" height="26" rx="3"/><rect x="314" y="200" width="7" height="26" rx="3"/><rect x="328" y="200" width="7" height="26" rx="3"/>
  </g>
  <circle cx="104" cy="206" r="13" fill="url(#sv-chrome)"/>
  <rect x="812" y="214" width="16" height="9" rx="3" fill="#b3261e"/>
  ${l.sidepipes ? `<rect x="290" y="246" width="320" height="16" rx="8" fill="url(#sv-chrome)"/>` : ''}
  ${wheel(210, 262, l.wheel)}${wheel(700, 262, l.wheel)}
</svg>`;
}

export function topView(l: Look, title = 'Segar Cobra top view'): string {
  const outline = 'M60 120 C60 70 110 52 190 48 L700 44 C800 44 840 70 840 120 C840 170 800 196 700 196 L190 192 C110 188 60 170 60 120 Z';
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 240" role="img"><title>${title}</title>
  <defs>
    <clipPath id="tv-body"><path d="${outline}"/></clipPath>
    <linearGradient id="tv-shine" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#fff" stop-opacity=".18"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".25"/>
    </linearGradient>
  </defs>
  <path d="${outline}" fill="${l.paint}"/>
  ${l.stripe ? `<g clip-path="url(#tv-body)" fill="${l.stripe}"><rect x="40" y="96" width="820" height="18"/><rect x="40" y="126" width="820" height="18"/></g>` : ''}
  <rect x="430" y="62" width="150" height="116" rx="40" fill="${l.interior}"/>
  <path d="M440 120 h130" stroke="#000" stroke-opacity=".25" stroke-width="2"/>
  <rect x="410" y="58" width="12" height="124" rx="6" fill="#9fb3c4" fill-opacity=".8"/>
  ${l.rollbar ? `<rect x="560" y="70" width="10" height="44" rx="5" fill="#d7dade"/>` : ''}
  <path d="${outline}" fill="url(#tv-shine)"/>
  ${l.sidepipes ? `<rect x="300" y="194" width="300" height="10" rx="5" fill="#cfd3d8"/><rect x="300" y="36" width="300" height="10" rx="5" fill="#cfd3d8"/>` : ''}
</svg>`;
}
