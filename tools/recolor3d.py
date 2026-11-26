#!/usr/bin/env python3
"""Make recoloured textures for the AI-generated Segar Cobra 3D model.

The GLB has one baked colour texture (a UV atlas). To recolour only the body
paint and stripes, every texel is mapped back to its 3D position on the car
(rasterising triangles in UV space), then:
  - wheels/tyres  : excluded (cylinders around the 4 wheel centres)
  - cockpit       : excluded (box between windscreen and roll bar, above sill)
  - paint         : dark, low-saturation texels on the remaining body
  - stripes       : bright, low-saturation texels on top surfaces near the centre line
Outputs public/3d/tex/<paint>-<stripe>.jpg for every configurator combination.

Usage: python3 tools/recolor3d.py [--debug]
"""
import json, os, struct, sys
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GLB = os.path.join(ROOT, 'public/3d/segar-cobra.glb')
OUT = os.path.join(ROOT, 'public/3d/tex')
SITE = os.path.join(ROOT, 'content/site.json')
DEBUG = '--debug' in sys.argv


def load_glb(path):
    d = open(path, 'rb').read()
    clen = struct.unpack('<I', d[12:16])[0]
    j = json.loads(d[20:20 + clen])
    binoff = 20 + clen + 8

    def acc(i):
        a = j['accessors'][i]
        bv = j['bufferViews'][a['bufferView']]
        off = binoff + bv.get('byteOffset', 0) + a.get('byteOffset', 0)
        n = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3}[a['type']]
        dt = {5126: np.float32, 5125: np.uint32, 5123: np.uint16}[a['componentType']]
        return np.frombuffer(d, dtype=dt, count=a['count'] * n, offset=off).reshape(-1, n) if n > 1 else \
            np.frombuffer(d, dtype=dt, count=a['count'], offset=off)

    prim = j['meshes'][0]['primitives'][0]
    pos = acc(prim['attributes']['POSITION']).astype(np.float64)
    uv = acc(prim['attributes']['TEXCOORD_0']).astype(np.float64)
    idx = acc(prim['indices']).astype(np.int64).reshape(-1, 3)
    img = j['images'][0]
    bv = j['bufferViews'][img['bufferView']]
    png = d[binoff + bv.get('byteOffset', 0): binoff + bv.get('byteOffset', 0) + bv['byteLength']]
    return pos, uv, idx, png


def rasterise(pos, uv, idx, size):
    """Per-texel 3D position and face normal, by drawing each triangle in UV space."""
    P = np.full((size, size, 3), np.nan)
    N = np.zeros((size, size, 3))
    px = uv * [size, size]  # glTF UV: v=0 is the top row of the image
    for t in idx:
        a, b, c = px[t]
        xmin, xmax = int(np.floor(min(a[0], b[0], c[0]))), int(np.ceil(max(a[0], b[0], c[0])))
        ymin, ymax = int(np.floor(min(a[1], b[1], c[1]))), int(np.ceil(max(a[1], b[1], c[1])))
        xmin, ymin = max(xmin, 0), max(ymin, 0)
        xmax, ymax = min(xmax, size - 1), min(ymax, size - 1)
        if xmax < xmin or ymax < ymin:
            continue
        xs, ys = np.meshgrid(np.arange(xmin, xmax + 1) + 0.5, np.arange(ymin, ymax + 1) + 0.5)
        v0, v1 = b - a, c - a
        den = v0[0] * v1[1] - v1[0] * v0[1]
        if abs(den) < 1e-12:
            continue
        w1 = ((xs - a[0]) * v1[1] - v1[0] * (ys - a[1])) / den
        w2 = (v0[0] * (ys - a[1]) - (xs - a[0]) * v0[1]) / den
        w0 = 1 - w1 - w2
        inside = (w0 >= -0.02) & (w1 >= -0.02) & (w2 >= -0.02)
        if not inside.any():
            continue
        p3 = pos[t]
        pts = w0[..., None] * p3[0] + w1[..., None] * p3[1] + w2[..., None] * p3[2]
        nrm = np.cross(p3[1] - p3[0], p3[2] - p3[0])
        nrm /= (np.linalg.norm(nrm) + 1e-12)
        yy, xx = np.nonzero(inside)
        P[ymin + yy, xmin + xx] = pts[inside]
        N[ymin + yy, xmin + xx] = nrm
    return P, N


def main():
    pos, uv, idx, png = load_glb(GLB)
    from io import BytesIO
    base = np.asarray(Image.open(BytesIO(png)).convert('RGB')).astype(np.float64) / 255
    size = base.shape[0]
    P, N = rasterise(pos, uv, idx, size)
    covered = ~np.isnan(P[..., 0])
    lo, hi = pos.min(0), pos.max(0)
    print('bbox', lo.round(3), hi.round(3), 'covered texels %.1f%%' % (100 * covered.mean()))
    np.save(os.path.join(ROOT, '3d-source/tex/posmap.npy'), P.astype(np.float32))
    np.save(os.path.join(ROOT, '3d-source/tex/nrmmap.npy'), N.astype(np.float32))

    masks = build_masks(base, P, N, covered)
    if DEBUG:
        dbg = base.copy() * 0.35
        for name, col in (('paint', (1, 0, 0)), ('stripe', (0, 1, 0)), ('wheel', (0, 0.3, 1)), ('cockpit', (1, 0.9, 0))):
            dbg[masks[name] > 0.5] = col
        write_glb_with_texture(GLB, os.path.join(ROOT, 'dist/3d/debug.glb'), to_jpeg(dbg))
        print({k: round(float((v > 0.5).mean() * 100), 1) for k, v in masks.items()}, '% of texels')
        return

    site = json.load(open(SITE))
    c = site['configurator']
    paints = {p['id']: hex2rgb(p['hex']) for p in c['paints']}
    stripes = {s['id']: (hex2rgb(s['hex']) if s['hex'] else None) for s in c['stripes']}
    os.makedirs(OUT, exist_ok=True)
    for pid, prgb in paints.items():
        for sid, srgb in stripes.items():
            tex = recolour(base, masks, prgb, srgb if srgb is not None else prgb, pid)
            open(os.path.join(OUT, f'{pid}-{sid}.jpg'), 'wb').write(to_jpeg(tex))
    print('wrote', len(paints) * len(stripes), 'textures to', OUT)


# --- regions ---------------------------------------------------------------
WHEELS = [(-0.305, -0.042), (0.303, -0.041)]  # (x, y) centres, both sides (|z| > 0.15)
COCKPIT_X = (-0.03, 0.18)                       # between windscreen base and roll bar


def smooth(m, r=1):
    """Tiny box blur so mask edges blend instead of showing hard pixel steps."""
    out = m.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx or dy:
                out += np.roll(np.roll(m, dy, 0), dx, 1)
    return out / (2 * r + 1) ** 2


def build_masks(base, P, N, covered):
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    az = np.abs(z)
    mx = base.max(-1); mn = base.min(-1)
    lum = 0.2126 * base[..., 0] + 0.7152 * base[..., 1] + 0.0722 * base[..., 2]
    sat = np.where(mx > 1e-6, (mx - mn) / np.maximum(mx, 1e-6), 0)
    with np.errstate(invalid='ignore'):
        wheel = np.zeros_like(lum, bool)
        for wx, wy in WHEELS:
            wheel |= (np.hypot(x - wx, y - wy) < 0.095) & (az > 0.15)
        cockpit = (x > COCKPIT_X[0]) & (x < COCKPIT_X[1]) & (az < 0.19) & (y < 0.075)
        underside = (N[..., 1] < -0.6) & (az < 0.2)
        body = covered & ~wheel & ~cockpit & ~underside & (y > -0.127)
        # Paint: dark, near-neutral texels (black paint incl. its reflections), blue-ish tint allowed.
        grille = (x < -0.44) & (az < 0.12) & (y < 0.02) & (N[..., 0] < -0.4)
        paint = body & ~grille & (lum < 0.55) & ((sat < 0.9) | (mx < 0.2))
        # Stripes: light neutral texels on upward-facing surfaces near the centre line, off the cockpit/windscreen.
        stripe = body & (lum > 0.38) & (sat < 0.25) & (N[..., 1] > 0.35) & (az < 0.11) & ~((x > -0.09) & (x < 0.2))
    paint &= ~stripe
    return {
        'paint': smooth(paint.astype(float)),
        'stripe': smooth(stripe.astype(float)),
        'wheel': wheel.astype(float),
        'cockpit': cockpit.astype(float),
        'lum': lum,
    }


def hex2rgb(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float) / 255


def recolour(base, masks, paint, stripe, pid):
    lum = masks['lum'][..., None]
    out = base.copy()
    # Paint keeps the original light/shadow: colour * (shading relative to typical black paint),
    # plus the original highlights on top so reflections stay.
    ref = 0.10
    shade = np.clip(lum / ref, 0.25, 2.2)
    if pid == 'black':
        new_paint = base  # original colour
    else:
        light = float(paint.mean())
        if light > 0.6:
            # Pale paints: compress the shading so dark original areas don't stay dark grey,
            # and keep reflections soft so it doesn't turn into chrome.
            soft = np.clip(lum / 0.14, 0, 1.3)
            new_paint = np.clip(paint * (0.6 + 0.32 * soft) + np.clip(lum - 0.35, 0, 1) * 0.35, 0, 1)
        else:
            new_paint = np.clip(paint * (0.35 + 0.8 * shade) + np.clip(lum - 0.25, 0, 1) * 0.9, 0, 1)
    new_stripe = np.clip(stripe * np.clip(lum / 0.62, 0.45, 1.25), 0, 1)
    mp, ms = masks['paint'][..., None], masks['stripe'][..., None]
    out = out * (1 - mp) + new_paint * mp
    out = out * (1 - ms) + new_stripe * ms
    return out


# --- GLB / image helpers ----------------------------------------------------------
def to_jpeg(arr, q=88):
    from io import BytesIO
    b = BytesIO()
    Image.fromarray((np.clip(arr, 0, 1) * 255).round().astype(np.uint8)).save(b, 'JPEG', quality=q, optimize=True)
    return b.getvalue()


def write_glb_with_texture(src, dst, jpeg):
    """Copy the GLB, replacing its single image with a JPEG (used for the debug view)."""
    d = open(src, 'rb').read()
    clen = struct.unpack('<I', d[12:16])[0]
    j = json.loads(d[20:20 + clen])
    binoff = 20 + clen + 8
    blen = struct.unpack('<I', d[20 + clen:24 + clen])[0]
    bin_ = d[binoff:binoff + blen]
    img_bv = j['images'][0]['bufferView']
    parts, new_bvs, cursor = [], [], 0
    for i, bv in enumerate(j['bufferViews']):
        data = jpeg if i == img_bv else bin_[bv.get('byteOffset', 0):bv.get('byteOffset', 0) + bv['byteLength']]
        pad = (-len(data)) % 4
        parts.append(data + b'\0' * pad)
        nbv = dict(bv); nbv['byteOffset'] = cursor; nbv['byteLength'] = len(data)
        new_bvs.append(nbv); cursor += len(data) + pad
    j['bufferViews'] = new_bvs
    j['images'][0]['mimeType'] = 'image/jpeg'
    j['buffers'][0]['byteLength'] = cursor
    js = json.dumps(j, separators=(',', ':')).encode()
    js += b' ' * ((-len(js)) % 4)
    body = b''.join(parts)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, 'wb') as f:
        f.write(struct.pack('<4sII', b'glTF', 2, 12 + 8 + len(js) + 8 + len(body)))
        f.write(struct.pack('<I4s', len(js), b'JSON') + js)
        f.write(struct.pack('<I4s', len(body), b'BIN\0') + body)


if __name__ == '__main__':
    main()
