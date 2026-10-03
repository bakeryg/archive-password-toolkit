# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# ArchivePasswordCracker —— 图标生成脚本
# Copyright (c) 2026 bakeryg
# SPDX-License-Identifier: MIT
# 项目地址: https://github.com/bakeryg/ArchivePasswordCracker
# ---------------------------------------------------------------------------
"""生成破解器图标：蓝色圆角方块 + 白色挂锁 + 金色锁孔。
输出 icon.ico（多尺寸）与 icon_preview.png（供肉眼检查）。"""
import os
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
S = 1024
TOP = (52, 120, 224)
BOT = (18, 56, 128)
WHITE = (255, 255, 255, 255)
GOLD = (245, 182, 66, 255)


def build_master():
    # 背景渐变
    grad = Image.new("RGBA", (S, S))
    gd = ImageDraw.Draw(grad)
    for y in range(S):
        t = y / float(S - 1)
        c = tuple(int(TOP[i] + (BOT[i] - TOP[i]) * t) for i in range(3)) + (255,)
        gd.line([(0, y), (S, y)], fill=c)

    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, S - 1, S - 1],
                                           radius=int(S * 0.22), fill=255)
    img.paste(grad, (0, 0), mask)

    d = ImageDraw.Draw(img)

    # 锁梁（圆环上半部分），居中，两条腿都落进锁体
    cx, cy = int(S * 0.5), int(S * 0.42)
    ro, ri = int(S * 0.235), int(S * 0.152)
    ring = Image.new("L", (S, S), 0)
    rd = ImageDraw.Draw(ring)
    rd.ellipse([cx - ro, cy - ro, cx + ro, cy + ro], fill=255)
    rd.ellipse([cx - ri, cy - ri, cx + ri, cy + ri], fill=0)
    clip = Image.new("L", (S, S), 0)
    ImageDraw.Draw(clip).rectangle([0, 0, S, int(S * 0.53)], fill=255)
    ring = Image.composite(ring, Image.new("L", (S, S), 0), clip)
    img.paste(Image.new("RGBA", (S, S), WHITE), (0, 0), ring)

    d = ImageDraw.Draw(img)

    # 锁体
    d.rounded_rectangle([int(S * 0.245), int(S * 0.47), int(S * 0.755), int(S * 0.865)],
                        radius=int(S * 0.085), fill=WHITE)

    # 锁孔（金）
    kcx, kcy, kr = int(S * 0.50), int(S * 0.615), int(S * 0.058)
    d.ellipse([kcx - kr, kcy - kr, kcx + kr, kcy + kr], fill=GOLD)
    d.rounded_rectangle([kcx - int(S * 0.026), kcy,
                         kcx + int(S * 0.026), int(S * 0.795)],
                        radius=int(S * 0.022), fill=GOLD)
    return img


master = build_master()
master.save(os.path.join(HERE, "icon_preview.png"))
master.resize((256, 256), Image.LANCZOS).save(os.path.join(HERE, "icon_256.png"))

sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (24, 24), (16, 16)]
master.save(os.path.join(HERE, "icon.ico"), format="ICO", sizes=sizes)
print("icon.ico 字节 =", os.path.getsize(os.path.join(HERE, "icon.ico")))
print("已生成 icon_preview.png / icon_256.png")

# ---------------- 客观校验：采样关键像素 ----------------
icon = Image.open(os.path.join(HERE, "icon.ico"))
print("ICO 内含尺寸:", sorted(icon.info.get("sizes", [])))

im = Image.open(os.path.join(HERE, "icon_256.png")).convert("RGBA")
W, H = im.size
px = im.load()


def sample(nx, ny):
    return px[int(nx * (W - 1)), int(ny * (H - 1))]


checks = [
    ("左上圆角外(应透明)", (0.005, 0.005), "a=0"),
    ("顶部中间(应蓝)", (0.5, 0.06), "b"),
    ("锁梁弧上(应白)", (0.5, 0.20), "w"),
    ("锁梁中间空心(应蓝)", (0.5, 0.42), "b"),
    ("锁体上部(应白)", (0.5, 0.52), "w"),
    ("锁孔(应金)", (0.5, 0.615), "g"),
    ("锁体下部(应白)", (0.5, 0.75), "w"),
    ("左侧背景(应蓝)", (0.06, 0.5), "b"),
    ("底部中间(应蓝)", (0.5, 0.95), "b"),
    ("右下圆角外(应透明)", (0.995, 0.995), "a=0"),
]


def kind(rgba):
    r, g, b, a = rgba
    if a < 30:
        return "a=0"
    if r > 225 and g > 225 and b > 225:
        return "w"
    if r > 200 and 140 < g < 215 and b < 120:
        return "g"
    if b > r and b > 90:
        return "b"
    return "?(%d,%d,%d,%d)" % (r, g, b, a)


ok = 0
for name, (nx, ny), want in checks:
    got = kind(sample(nx, ny))
    good = (got == want)
    ok += 1 if good else 0
    print("  %-22s 期望=%-3s 实际=%-10s %s" % (name, want, got, "OK" if good else "<<< 不符"))
print("采样通过 %d/%d" % (ok, len(checks)))

