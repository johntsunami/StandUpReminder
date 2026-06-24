#!/usr/bin/env python3
"""
Generate standup.ico using ONLY the Python standard library (zlib + struct).

Draws a rounded green square with a white "stand up" arrow and writes it as a
256x256 PNG embedded inside an .ico container (supported by Windows Vista+).
No Pillow / pip dependencies -- so it works on any machine that has Python.

Run directly (`python make_icon.py`) or import and call build_icon(path).
"""

import os
import zlib
import struct

SIZE = 256


def _lerp(a, b, t):
    return int(a + (b - a) * t)


def _build_pixels():
    """Return a bytearray of RGBA pixels (top-to-bottom, left-to-right)."""
    w = h = SIZE
    px = bytearray(w * h * 4)

    radius = 46          # rounded-corner radius of the background tile
    # Arrow geometry (an upward arrow = "stand up").
    cx = w // 2
    stem_half = 26
    stem_top = 118
    stem_bot = 196
    head_apex_y = 58
    head_base_y = 132
    head_half = 70

    for y in range(h):
        for x in range(w):
            i = (y * w + x) * 4
            inside_tile = _in_rounded_rect(x, y, 8, 8, w - 8, h - 8, radius)
            if not inside_tile:
                px[i:i + 4] = bytes((0, 0, 0, 0))   # transparent outside tile
                continue

            # Vertical gradient background: bright green -> deep green.
            t = y / h
            r = _lerp(0x2E, 0x0B, t)
            g = _lerp(0xC4, 0x5E, t)
            b = _lerp(0x6B, 0x30, t)

            # White arrow on top.
            in_stem = (stem_top <= y <= stem_bot and abs(x - cx) <= stem_half)
            in_head = False
            if head_apex_y <= y <= head_base_y:
                # triangle width grows linearly from apex to base
                frac = (y - head_apex_y) / (head_base_y - head_apex_y)
                half = int(head_half * frac)
                in_head = abs(x - cx) <= half
            if in_stem or in_head:
                r, g, b = 0xFF, 0xFF, 0xFF

            px[i:i + 4] = bytes((r, g, b, 255))
    return w, h, px


def _in_rounded_rect(x, y, x0, y0, x1, y1, rad):
    if x < x0 or x > x1 or y < y0 or y > y1:
        return False
    # Check the four corner circles.
    for cxr, cyr in ((x0 + rad, y0 + rad), (x1 - rad, y0 + rad),
                     (x0 + rad, y1 - rad), (x1 - rad, y1 - rad)):
        if ((x < x0 + rad and y < y0 + rad and cxr == x0 + rad and cyr == y0 + rad) or
                (x > x1 - rad and y < y0 + rad and cxr == x1 - rad and cyr == y0 + rad) or
                (x < x0 + rad and y > y1 - rad and cxr == x0 + rad and cyr == y1 - rad) or
                (x > x1 - rad and y > y1 - rad and cxr == x1 - rad and cyr == y1 - rad)):
            if (x - cxr) ** 2 + (y - cyr) ** 2 > rad ** 2:
                return False
    return True


def _png_bytes(w, h, px):
    def chunk(typ, data):
        return (struct.pack(">I", len(data)) + typ + data +
                struct.pack(">I", zlib.crc32(typ + data) & 0xffffffff))

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)   # 8-bit RGBA
    raw = bytearray()
    row = w * 4
    for y in range(h):
        raw.append(0)                                     # filter type 0
        raw += px[y * row:(y + 1) * row]
    idat = zlib.compress(bytes(raw), 9)
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


def build_icon(path):
    w, h, px = _build_pixels()
    png = _png_bytes(w, h, px)
    # ICONDIR (6 bytes) + one ICONDIRENTRY (16 bytes) + PNG payload.
    icondir = struct.pack("<HHH", 0, 1, 1)
    bw = 0 if w >= 256 else w        # 0 means 256 in the .ico spec
    bh = 0 if h >= 256 else h
    entry = struct.pack("<BBBBHHII", bw, bh, 0, 0, 1, 32, len(png), 6 + 16)
    with open(path, "wb") as fh:
        fh.write(icondir + entry + png)
    return path


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "standup.ico")
    build_icon(out)
    print("Wrote", out, "(%d bytes)" % os.path.getsize(out))
