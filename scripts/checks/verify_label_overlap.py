"""检查已发布 Pareto SVG 的标签碰撞 / Label-collision check for published Pareto SVGs.

Fail rules: label↔label overlap > 4 px²; label↔marker overlap ≥ 25% of the
marker box; label text × any non-label SVG text (ticks/captions/legend, zero
tolerance); frontier polyline × label text (name unpadded, zero tolerance);
leader×other-label and leader×leader crossings (zero tolerance); label text
outside the plot panel; a label union box fails only when another frontier
marker sits within 40 px of it and strictly closer than its own; leader longer
than 300 px (>200 px = info); every label text
box must stay left of the y-axis line (x ≥ 120) and above the x-axis line
(y ≤ 705), and must not touch the $0 axis-break zigzag near the axis.
Font metrics come from Pillow real glyphs (Ink box + advance), not estimates.
"""

import math
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import ImageFont

ROOT = Path(__file__).resolve().parent.parent.parent
NS = "{http://www.w3.org/2000/svg}"
# 白底面板 rect（plot_svg.py 写死）：x 40..1400, y 184..796
PANEL = (40.0, 184.0, 1400.0, 796.0)
# plot_svg.py L32：LEFT, RIGHT, TOP, BOTTOM = 120, 1338, 233, 705
AXIS_LEFT, AXIS_BOTTOM = 120.0, 705.0
LEADER_SAMPLES = 60
LONG_LEADER_PX = 200.0
MAX_LEADER_PX = 300.0
LABEL_OVERLAP_PX2 = 4.0
MARKER_COVERAGE = 0.25


def font_path():
    """标签字体解析顺序：CHART_LABEL_ENV → msyh.ttc → matplotlib 里的 Noto Sans CJK SC。"""
    env = os.environ.get("CHART_LABEL_FONT")
    if env and os.path.isfile(env):
        return env
    yahei = "C:/Windows/Fonts/msyh.ttc"
    if os.path.isfile(yahei):
        return yahei
    try:
        from matplotlib import font_manager
        from matplotlib.font_manager import FontProperties
        return font_manager.findfont(
            FontProperties(family="Noto Sans CJK SC"), fallback_to_default=False)
    except Exception:
        return None


def load_fonts():
    if os.environ.get("CHART_FONT_FALLBACK") == "1":
        print("SKIP: chart fonts unavailable (CHART_FONT_FALLBACK=1)")
        sys.exit(0)
    path = font_path()
    if path is None:
        sys.exit("找不到中文字体（Microsoft YaHei 或 Noto Sans CJK SC），无法按真实字形量标签框；"
                 "请安装其一或用 CHART_LABEL_FONT 指定。"
                 " No CJK font found: label boxes need real glyph metrics."
                 " Install Microsoft YaHei or Noto Sans CJK SC, or set CHART_LABEL_FONT."
                 " CI-only runs may set CHART_FONT_FALLBACK=1 to skip.")
    cache = {}

    def get(size):
        key = round(float(size), 2)
        if key not in cache:
            cache[key] = ImageFont.truetype(path, key)
        return cache[key]
    get.path = path
    return get


def text_box(font_of, x, y, content, size, anchor, pad):
    """(x,y) 是 SVG 基线原点；getbbox(anchor='ls') 给出相对基线的 ink box。"""
    font = font_of(size)
    left, top, right, bottom = font.getbbox(content, anchor="ls")
    if anchor == "end":
        x -= font.getlength(content)
    elif anchor == "middle":
        x -= font.getlength(content) / 2
    return (x + left - pad, y + top - pad, x + right + pad, y + bottom + pad)


def overlap(a, b):
    ox = min(a[2], b[2]) - max(a[0], b[0])
    oy = min(a[3], b[3]) - max(a[1], b[1])
    if ox <= 0 or oy <= 0:
        return None
    return (max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3]), ox * oy)


def seg_intersect(p1, p2, p3, p4):
    d1 = (p4[0] - p3[0]) * (p1[1] - p3[1]) - (p4[1] - p3[1]) * (p1[0] - p3[0])
    d2 = (p4[0] - p3[0]) * (p2[1] - p3[1]) - (p4[1] - p3[1]) * (p2[0] - p3[0])
    d3 = (p2[0] - p1[0]) * (p3[1] - p1[1]) - (p2[1] - p1[1]) * (p3[0] - p1[0])
    d4 = (p2[0] - p1[0]) * (p4[1] - p1[1]) - (p2[1] - p1[1]) * (p4[0] - p1[0])
    return ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0))


def seg_hits_rect(p1, p2, rect):
    x0, y0, x1, y1 = rect
    if x0 <= p1[0] <= x1 and y0 <= p1[1] <= y1:
        return True
    if x0 <= p2[0] <= x1 and y0 <= p2[1] <= y1:
        return True
    corners = ((x0, y0), (x1, y0), (x1, y1), (x0, y1))
    return any(seg_intersect(p1, p2, corners[i], corners[(i + 1) % 4]) for i in range(4))


def bezier(d):
    nums = [float(v) for v in re.findall(r"-?\d*\.?\d+(?:[eE][-+]?\d+)?", d)]
    if len(nums) != 6:
        return []
    sx, sy, cx, cy, ex, ey = nums
    pts = []
    for i in range(LEADER_SAMPLES + 1):
        t = i / LEADER_SAMPLES
        u = 1 - t
        pts.append((u * u * sx + 2 * u * t * cx + t * t * ex,
                    u * u * sy + 2 * u * t * cy + t * t * ey))
    return pts


def polyline_length(pts):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))


def marker_half(g):
    """点标半宽：前沿方块 11（描边1.35）/ 前沿按量菱形 12 / 非前沿按量菱形 5.5 /
    非前沿订阅方块 3.5（+0.9 深色边）/ Devin 非前沿 logo r2.4 按 5.5 计。"""
    frontier = g.get("data-frontier") == "true"
    metered = g.get("data-billing") == "metered"
    if frontier:
        return 12 + 1.35 / 2 if metered else 11 + 1.35 / 2
    if metered:
        return 5.5 + 1.5 / 2
    for child in g:
        if child.tag == NS + "rect":
            return 3.5 + (0.9 / 2 if child.get("stroke") else 0)
    return 5.5  # Devin logo（官方 mark），按非前沿菱形半宽计


def rotate_box(box, spec):
    """transform="rotate(a cx cy)"：旋转文本框四角后取外接矩形。"""
    m = re.match(r"rotate\(\s*(-?[\d.]+)(?:[,\s]+(-?[\d.]+)[,\s]+(-?[\d.]+))?\s*\)",
                 spec or "")
    if not m:
        return box
    a = math.radians(float(m.group(1)))
    cx = float(m.group(2) or 0.0)
    cy = float(m.group(3) or 0.0)
    cos, sin = math.cos(a), math.sin(a)
    pts = [(cx + (x - cx) * cos - (y - cy) * sin,
            cy + (x - cx) * sin + (y - cy) * cos)
           for x, y in ((box[0], box[1]), (box[2], box[1]),
                        (box[2], box[3]), (box[0], box[3]))]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return (min(xs), min(ys), max(xs), max(ys))


def path_points(d):
    """frontier path 只含 M/L 绝对坐标，成对取出。"""
    nums = [float(v) for v in re.findall(r"-?\d*\.?\d+(?:[eE][-+]?\d+)?", d or "")]
    return list(zip(nums[::2], nums[1::2]))


def box_pt_dist(box, pt):
    dx = max(box[0] - pt[0], 0.0, pt[0] - box[2])
    dy = max(box[1] - pt[1], 0.0, pt[1] - box[3])
    return math.hypot(dx, dy)


def parse_chart(path, font_of):
    root = ET.parse(path).getroot()
    labels, markers, statics, frontier_pts, breaks = [], [], [], [], []
    fl_ids = set()
    for g in root.iter(NS + "g"):
        if g.get("class") == "front-label":
            for t in g.iter(NS + "text"):
                fl_ids.add(id(t))
    for p in root.iter(NS + "path"):
        d = p.get("d", "")
        if p.get("id") == "frontier":
            frontier_pts = path_points(d)
        elif "l5 -7 5 7" in d:
            # $0 轴断裂 zigzag：M{bx} 699l5 -7 5 7M{bx+6} 711l5 -7 5 7
            m = re.match(r"M\s*(-?[\d.]+)", d)
            if m:
                bx = float(m.group(1))
                breaks.append((bx, AXIS_BOTTOM - 13, bx + 16, AXIS_BOTTOM + 6))
    for t in root.iter(NS + "text"):
        if id(t) in fl_ids or not (t.text or "").strip():
            continue
        box = text_box(font_of, float(t.get("x")), float(t.get("y")), t.text,
                       float(t.get("font-size", 12)),
                       t.get("text-anchor", "start"), 0.0)
        statics.append({"text": t.text, "box": rotate_box(box, t.get("transform"))})
    for g in root.iter(NS + "g"):
        if g.get("class") == "point":
            x, y = float(g.get("data-x")), float(g.get("data-y"))
            h = marker_half(g)
            title = g.find(NS + "title")
            tip = (title.text or "")[:60] if title is not None else ""
            markers.append({"box": (x - h, y - h, x + h, y + h), "tip": tip,
                            "area": (2 * h) ** 2, "c": (x, y),
                            "frontier": g.get("data-frontier") == "true"})
        elif g.get("class") == "front-label":
            label = {"model": g.get("data-model"), "texts": [], "leader": []}
            for child in g:
                if child.tag == NS + "path":
                    label["leader"] = bezier(child.get("d", ""))
                elif child.tag == NS + "text":
                    cls = child.get("class", "")
                    role = "name" if cls == "label-name" else "price" if cls == "number" else "plan"
                    pad = 2.5 if role == "name" else 1.0
                    content = child.text or ""
                    box = text_box(font_of, float(child.get("x")), float(child.get("y")),
                                   content, float(child.get("font-size")),
                                   child.get("text-anchor", "start"), pad)
                    box0 = (text_box(font_of, float(child.get("x")), float(child.get("y")),
                                     content, float(child.get("font-size")),
                                     child.get("text-anchor", "start"), 0.0)
                            if role == "name" else box)
                    label["texts"].append({"role": role, "text": content,
                                           "box": box, "box0": box0})
            labels.append(label)
    return labels, markers, statics, frontier_pts, breaks


def short(s, n=44):
    return s if len(s) <= n else s[: n - 1] + "…"


def fmt_rect(r):
    return f"({r[0]:.1f},{r[1]:.1f})–({r[2]:.1f},{r[3]:.1f}) area {r[4]:.1f}px²"


def check_chart(path, font_of):
    labels, markers, statics, frontier_pts, breaks = parse_chart(path, font_of)
    fmarkers = [m for m in markers if m["frontier"]]
    findings = {"label×label": [], "label×marker": [], "label×static": [],
                "label×frontier": [], "leader×label": [], "leader×leader": [],
                "outside-panel": [], "association": [], "label×axis": [],
                "label×axis-break": [], "long-leader": []}
    info = []
    for i, a in enumerate(labels):
        union = None
        for t in a["texts"]:
            union = t["box"] if union is None else (
                min(union[0], t["box"][0]), min(union[1], t["box"][1]),
                max(union[2], t["box"][2]), max(union[3], t["box"][3]))
        for t in a["texts"]:
            for s in statics:
                hit = overlap(t["box"], s["box"])
                if hit:
                    findings["label×static"].append(
                        f"'{short(t['text'])}' ({t['role']}, {a['model']}) × static "
                        f"'{short(s['text'], 30)}' {fmt_rect(hit)}")
            fbox = t["box0"] if t["role"] == "name" else t["box"]
            for k in range(len(frontier_pts) - 1):
                if seg_hits_rect(frontier_pts[k], frontier_pts[k + 1], fbox):
                    findings["label×frontier"].append(
                        f"frontier line through '{short(t['text'])}' "
                        f"({t['role']}, {a['model']})")
                    break
            if t["box"][3] > AXIS_BOTTOM or t["box"][0] < AXIS_LEFT:
                findings["label×axis"].append(
                    f"'{short(t['text'])}' ({t['role']}, {a['model']}) box "
                    f"({t['box'][0]:.1f},{t['box'][1]:.1f})–({t['box'][2]:.1f},{t['box'][3]:.1f}) "
                    f"crosses axis x<{AXIS_LEFT:.0f} or y>{AXIS_BOTTOM:.0f}")
            for ab in breaks:
                if overlap(t["box"], ab):
                    findings["label×axis-break"].append(
                        f"'{short(t['text'])}' ({t['role']}, {a['model']}) × "
                        f"$0 axis break {ab}")
        if union and a["leader"] and fmarkers:
            own = min(fmarkers,
                      key=lambda m: math.hypot(m["c"][0] - a["leader"][0][0],
                                               m["c"][1] - a["leader"][0][1]))
            own_d = box_pt_dist(union, own["c"])
            for m in fmarkers:
                if m is own:
                    continue
                d = box_pt_dist(union, m["c"])
                if d < 40.0 and d < own_d:
                    findings["association"].append(
                        f"label of {a['model']} nearer frontier point "
                        f"'{short(m['tip'], 36)}' ({d:.0f}px) than own ({own_d:.0f}px)")
                    break
        for t in a["texts"]:
            hit = overlap(t["box"], PANEL)
            if hit is None or t["box"][0] < PANEL[0] or t["box"][1] < PANEL[1] \
                    or t["box"][2] > PANEL[2] or t["box"][3] > PANEL[3]:
                findings["outside-panel"].append(
                    f"'{short(t['text'])}' ({t['role']}, {a['model']}) box "
                    f"({t['box'][0]:.1f},{t['box'][1]:.1f})–({t['box'][2]:.1f},{t['box'][3]:.1f}) "
                    f"outside panel {PANEL}")
            for m in markers:
                hit = overlap(t["box"], m["box"])
                if hit and hit[4] / m["area"] >= MARKER_COVERAGE:
                    findings["label×marker"].append(
                        f"'{short(t['text'])}' ({t['role']}, {a['model']}) × point '{short(m['tip'])}' "
                        f"{fmt_rect(hit)} = {hit[4] / m['area']:.0%} of marker")
            for j, b in enumerate(labels):
                if j <= i:
                    continue
                for u in b["texts"]:
                    hit = overlap(t["box"], u["box"])
                    if hit and hit[4] > LABEL_OVERLAP_PX2:
                        findings["label×label"].append(
                            f"'{short(t['text'])}' ({t['role']}, {a['model']}) × "
                            f"'{short(u['text'])}' ({u['role']}, {b['model']}) {fmt_rect(hit)}")
        for j, b in enumerate(labels):
            if j == i:
                continue
            hit_roles = set()
            for seg_i in range(len(a["leader"]) - 1):
                p1, p2 = a["leader"][seg_i], a["leader"][seg_i + 1]
                for u in b["texts"]:
                    if u["role"] not in hit_roles and seg_hits_rect(p1, p2, u["box"]):
                        hit_roles.add(u["role"])
                        findings["leader×label"].append(
                            f"leader of {a['model']} through '{short(u['text'])}' "
                            f"({u['role']}, {b['model']})")
            if j <= i:
                continue
            done = False
            for seg in zip(a["leader"], a["leader"][1:]):
                if done:
                    break
                for oseg in zip(b["leader"], b["leader"][1:]):
                    if seg_intersect(seg[0], seg[1], oseg[0], oseg[1]):
                        findings["leader×leader"].append(
                            f"leader of {a['model']} crosses leader of {b['model']} "
                            f"near ({seg[0][0]:.1f},{seg[0][1]:.1f})")
                        done = True
                        break
        length = polyline_length(a["leader"])
        if length > MAX_LEADER_PX:
            findings["long-leader"].append(f"leader of {a['model']} is {length:.0f}px")
        if length > LONG_LEADER_PX:
            info.append(f"leader of {a['model']} is {length:.0f}px")
    return findings, info


def main():
    font_of = load_fonts()
    charts = ([Path(p) for p in sys.argv[1:]] if len(sys.argv) > 1
              else sorted(ROOT.glob("charts/*/pareto/*.svg")))
    total = 0
    per_rule_totals = {}
    for path in charts:
        try:
            rel = path.relative_to(ROOT).as_posix()
        except ValueError:
            rel = path.name
        findings, info = check_chart(path, font_of)
        n = sum(len(v) for v in findings.values())
        total += n
        print(f"\n{rel} — {n} violation(s)")
        for rule, items in findings.items():
            if items:
                per_rule_totals[rule] = per_rule_totals.get(rule, 0) + len(items)
                print(f"  [{rule}] {len(items)}")
                for item in items:
                    print(f"    {item}")
        for line in info:
            print(f"  info: {line}")
    print("\n=== summary ===")
    print(f"charts checked: {len(charts)}; violations: {total}")
    for rule in ("label×label", "label×marker", "label×static",
                 "label×frontier", "leader×label", "leader×leader",
                 "outside-panel", "association", "label×axis",
                 "label×axis-break", "long-leader"):
        print(f"  {rule}: {per_rule_totals.get(rule, 0)}")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
