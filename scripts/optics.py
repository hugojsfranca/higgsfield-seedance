#!/usr/bin/env python3
"""Frame size for a lens at a distance, to sanity-check size claims in a prompt.

Usage:  python3 optics.py 70mm 120m          (also 35cm, 2.5m, 800mm distances; lenses as 50mm or 47deg)
        python3 optics.py 100mm 35cm --aspect 16:9

Prints the diagonal and horizontal field of view and the frame width and height at that distance.
Full-frame (36 x 24 mm) equivalent focal lengths. Standard library only.
"""
import argparse
import math
import re
import sys

FF_DIAGONAL_MM = math.hypot(36, 24)  # 43.27 mm


def parse_distance(text):
    m = re.fullmatch(r"\s*([\d.]+)\s*(mm|cm|m)?\s*", text)
    if not m:
        sys.exit(f"can't read distance '{text}' (use e.g. 120m, 35cm)")
    value, unit = float(m.group(1)), (m.group(2) or "m")
    return value / {"mm": 1000, "cm": 100, "m": 1}[unit]


def diagonal_fov(lens):
    m = re.fullmatch(r"\s*([\d.]+)\s*(mm|deg|°)?\s*", lens)
    if not m:
        sys.exit(f"can't read lens '{lens}' (use e.g. 50mm or 47deg)")
    value, unit = float(m.group(1)), (m.group(2) or "mm")
    if unit == "mm":
        return math.degrees(2 * math.atan(FF_DIAGONAL_MM / (2 * value)))
    return value


def main():
    ap = argparse.ArgumentParser(description="Frame width/height for a lens at a distance.")
    ap.add_argument("lens", help="focal length (50mm) or diagonal field of view (47deg)")
    ap.add_argument("distance", help="camera-to-subject distance (120m, 35cm)")
    ap.add_argument("--aspect", default="16:9")
    a = ap.parse_args()
    w, h = (float(x) for x in a.aspect.split(":"))
    dfov = diagonal_fov(a.lens)
    d = parse_distance(a.distance)
    half_diag = math.tan(math.radians(dfov / 2))
    diag = math.hypot(w, h)
    half_w, half_h = half_diag * w / diag, half_diag * h / diag
    width, height = 2 * d * half_w, 2 * d * half_h
    hfov = math.degrees(2 * math.atan(half_w))

    def fmt(x):
        return f"{x:.2f} m" if x >= 1 else f"{x * 100:.1f} cm"

    print(f"{a.lens} → diagonal FOV {dfov:.0f}°, horizontal {hfov:.0f}° ({a.aspect})")
    print(f"at {fmt(d)}: frame {fmt(width)} wide × {fmt(height)} high")
    print(f"a subject fills the middle third only if it is about {fmt(width / 3)} wide or less")


if __name__ == "__main__":
    main()
