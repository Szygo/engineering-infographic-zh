#!/usr/bin/env python3
"""把生成图和参考图逐像素比对，并报出错位带位置。

用法:
    python compare_images.py 参考图.png 生成图.png --report
    python compare_images.py 参考图.png 生成图.png --heatmap diff.png

思路：先整体算平均色差；再把"差得比较狠"的行/列聚成带状区间，
那些区间就是没对齐的卡片或文字。用它定位，而不是靠眼睛扫全图。
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image


def group_bands(flags, gap=3, min_len=2):
    bands = []
    start = None
    last = None
    for i, on in enumerate(flags):
        if on:
            if start is None:
                start = i
            last = i
        elif start is not None and i - last > gap:
            if last - start + 1 >= min_len:
                bands.append((start, last))
            start = None
    if start is not None and last - start + 1 >= min_len:
        bands.append((start, last))
    return bands


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("reference")
    ap.add_argument("generated")
    ap.add_argument("--report", action="store_true", help="打印错位带明细")
    ap.add_argument("--heatmap", help="把差异热力图写到这个路径")
    ap.add_argument("--threshold", type=int, default=40,
                    help="判定为差异像素的阈值，默认 40")
    args = ap.parse_args()

    for p in (args.reference, args.generated):
        if not os.path.exists(p):
            raise SystemExit("找不到文件: %s" % p)

    ref = Image.open(args.reference).convert("RGB")
    gen = Image.open(args.generated).convert("RGB")
    if gen.size != ref.size:
        print("尺寸不同：参考 %s / 生成 %s，已把生成图缩放到参考尺寸"
              % (ref.size, gen.size))
        gen = gen.resize(ref.size, Image.LANCZOS)

    a = np.asarray(ref, dtype=np.int16)
    b = np.asarray(gen, dtype=np.int16)
    diff = np.abs(a - b)
    per_pixel = diff.max(axis=2)

    mean = float(diff.mean())
    print("平均色差 : %.2f / 255" % mean)
    print("最大色差 : %d" % int(per_pixel.max()))
    print("差异像素 : %.2f%% (阈值 %d)" % ((per_pixel > args.threshold).mean() * 100,
                                          args.threshold))

    if args.report:
        rows = (per_pixel > args.threshold).sum(axis=1) > 3
        cols = (per_pixel > args.threshold).sum(axis=0) > 3
        rb = group_bands(rows)
        cb = group_bands(cols)
        print("错的比较狠的行区间 : %s" % (rb if rb else "无"))
        print("错的比较狠的列区间 : %s" % (cb if cb else "无"))
        if mean < 15 and not rb and not cb:
            print("结论 : 与原图基本一致")
        else:
            print("结论 : 上面这些区间就是没对齐的卡片/文字，回去改坐标或字号")

    if args.heatmap:
        heat = np.zeros(a.shape, dtype=np.uint8)
        heat[..., 0] = np.clip(per_pixel * 3, 0, 255).astype(np.uint8)
        Image.fromarray(heat).save(args.heatmap)
        print("热力图 : %s" % args.heatmap)


if __name__ == "__main__":
    main()
