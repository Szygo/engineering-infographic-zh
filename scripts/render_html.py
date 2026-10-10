#!/usr/bin/env python3
"""把固定尺寸的 HTML 版面渲染成 PNG（或矢量 PDF）。

用法:
    python render_html.py board.html board.png --scale 3
    python render_html.py board.html board.pdf --pdf

画布尺寸默认从 HTML 里 .root 的 width/height 自动读取，也可以用
--width/--height 覆盖。渲染走 Edge/Chrome 的无头模式。
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid

WIN_BROWSERS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]
NIX_BROWSERS = ["microsoft-edge", "msedge", "google-chrome", "chromium", "chromium-browser", "chrome"]


def find_browser():
    for path in WIN_BROWSERS:
        if os.path.exists(path):
            return path
    for name in NIX_BROWSERS:
        found = shutil.which(name)
        if found:
            return found
    return None


def detect_size(html_path):
    with open(html_path, "r", encoding="utf-8") as fh:
        css = fh.read()
    root = re.search(r"\.root\s*\{[^}]*\}", css, re.S)
    scope = root.group(0) if root else css
    w = re.search(r"width\s*:\s*(\d+)px", scope)
    h = re.search(r"height\s*:\s*(\d+)px", scope)
    if not (w and h):
        raise SystemExit("无法从 HTML 读到画布尺寸，请用 --width/--height 指定")
    return int(w.group(1)), int(h.group(1))


def wait_for_file(path, timeout=25.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            time.sleep(0.3)
            return True
        time.sleep(0.25)
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("out")
    ap.add_argument("--scale", type=float, default=3.0, help="PNG 输出倍率，默认 3")
    ap.add_argument("--width", type=int)
    ap.add_argument("--height", type=int)
    ap.add_argument("--pdf", action="store_true", help="输出矢量 PDF 而不是 PNG")
    ap.add_argument("--browser")
    args = ap.parse_args()

    html = os.path.abspath(args.html)
    out = os.path.abspath(args.out)
    if not os.path.exists(html):
        raise SystemExit("找不到 HTML: %s" % html)

    browser = args.browser or find_browser()
    if not browser:
        raise SystemExit("没找到 Edge/Chrome，可用 --browser 指定可执行文件路径")

    w, h = detect_size(html)
    if args.width:
        w = args.width
    if args.height:
        h = args.height

    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    # Chromium 在目标文件已存在时可能直接跳过截图，先清掉
    if os.path.exists(out):
        os.remove(out)
    url = "file:///" + html.replace("\\", "/")
    if os.name != "nt":
        from pathlib import Path
        url = Path(html).as_uri()

    profile = os.path.join(tempfile.gettempdir(), "board-render-" + uuid.uuid4().hex[:8])
    base = [
        browser, "--headless=new", "--disable-gpu", "--no-sandbox",
        "--hide-scrollbars", "--disable-extensions",
        "--user-data-dir=" + profile,
    ]

    if args.pdf:
        cmd = base + [
            "--no-pdf-header-footer",
            "--print-to-pdf=" + out,
            url,
        ]
    else:
        cmd = base + [
            "--force-device-scale-factor=%s" % args.scale,
            "--window-size=%d,%d" % (w, h),
            "--screenshot=" + out,
            url,
        ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if not wait_for_file(out) and not args.pdf:
        sys.stderr.write(result.stdout or "")
        sys.stderr.write(result.stderr or "")
        raise SystemExit("渲染失败，没有生成 %s" % out)

    print("browser : %s" % browser)
    print("canvas  : %dx%d @%sx" % (w, h, args.scale) if not args.pdf else "canvas  : %dx%d (pdf)" % (w, h))
    print("output  : %s (%d bytes)" % (out, os.path.getsize(out) if os.path.exists(out) else 0))


if __name__ == "__main__":
    main()
