#!/usr/bin/env python3
"""Generate clean, editorial-quality SVG charts for the No Code by Hand article.

Charts are designed at 800px wide to fit within the blog's col-lg-8 article
column. They use transparent backgrounds (styled by CSS in the blog theme)
and system fonts for consistent rendering.
"""

from __future__ import annotations

import html
import json
import csv
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = Path("/Users/monty/Downloads/agentic-engineering-manuscript-2026-02-28/data")
OUTPUT_DIR = REPO_ROOT / "content" / "images" / "articles" / "no-code-by-hand"

WORKSTREAM_PR_MAP: dict[str, set[str]] = {
    "CI architecture": {"2636", "2641", "2664", "2692", "2697", "2700", "2713", "2717"},
    "Testing platform": {"191", "281", "282", "283", "285", "286", "290", "302", "318", "320", "2613"},
    "Typing modernization": {"2561", "2635", "2706"},
    "Local dev & worktrees": {"1863", "47", "48"},
    "Operations & safety": {"2563", "2649", "2651", "2656", "2660", "45", "46", "49"},
    "Security & dependency": {"2674", "2675", "2676", "317", "319", "310", "311", "218", "260", "275", "276", "298"},
    "Debt & migrations": {"2553", "2554", "2558", "2628", "2642", "2648"},
    "Agent workflow skills": {"301", "334", "335", "341"},
    "Prototype infra": {"263"},
}

# -- Design tokens ----------------------------------------------------------
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif"
NAVY = "#1e3a5f"
TEAL = "#0d9488"
AMBER = "#d97706"
ROSE = "#be123c"
EMERALD = "#059669"
INDIGO = "#4f46e5"
PURPLE = "#7c3aed"
S900 = "#0f172a"
S700 = "#334155"
S500 = "#64748b"
S400 = "#94a3b8"
S300 = "#cbd5e1"
S200 = "#e2e8f0"
S100 = "#f1f5f9"
S50 = "#f8fafc"
WHITE = "#ffffff"
RED_50 = "#fef2f2"
RED_300 = "#fca5a5"
GREEN_50 = "#ecfdf5"
GREEN_300 = "#86efac"


def esc(v: object) -> str:
    return html.escape(str(v), quote=True)


def svg_open(w: int, h: int, label: str = "chart") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" role="img" aria-label="{esc(label)}">\n'
        f"<defs><style>\n"
        f"text {{ font-family: {FONT}; }}\n"
        f".v {{ font-weight: 700; font-size: 14px; fill: {S900}; }}\n"
        f".vl {{ font-weight: 700; font-size: 14px; fill: {WHITE}; }}\n"
        f".cat {{ font-weight: 600; font-size: 13px; fill: {S700}; }}\n"
        f".sm {{ font-weight: 500; font-size: 11px; fill: {S500}; }}\n"
        f".sm-dark {{ font-weight: 500; font-size: 11px; fill: {S700}; }}\n"
        f".smb {{ font-weight: 600; font-size: 11px; fill: {S500}; }}\n"
        f".ax {{ stroke: {S300}; stroke-width: 1; }}\n"
        f".grid {{ stroke: {S200}; stroke-width: 1; stroke-dasharray: 4 3; }}\n"
        f".box-label {{ font-weight: 700; font-size: 12px; fill: {WHITE}; }}\n"
        f".box-sub {{ font-weight: 500; font-size: 11px; fill: rgba(255,255,255,0.85); }}\n"
        f".heading {{ font-weight: 700; font-size: 13px; fill: {S700}; }}\n"
        f".heading-sm {{ font-weight: 600; font-size: 12px; fill: {S500}; }}\n"
        f".good {{ font-weight: 600; font-size: 11px; fill: #059669; }}\n"
        f".bad {{ font-weight: 600; font-size: 11px; fill: #dc2626; }}\n"
        f"</style></defs>\n"
        f'<rect width="100%" height="100%" fill="{WHITE}"/>'
    )


def svg_close() -> str:
    return "</svg>"


def write_svg(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    print(f"  wrote {path.name}")


def read_major_pr_rows(data_dir: Path) -> list[dict[str, str]]:
    with (data_dir / "major_non_product_prs.csv").open("r", encoding="utf-8", newline="") as fp:
        return list(csv.DictReader(fp))


# ── Chart 1: Changeset Mix ─────────────────────────────────────────────────

def make_changeset_mix(summary: dict, out: Path) -> None:
    counts = summary["major_pr_counts"]
    direct = len(summary["true_non_pr_commits"])
    combined = summary["combined_totals_including_true_non_pr_commits"]

    cats = [
        ("Backend", counts["backend"], NAVY),
        ("Frontend", counts["frontend"], TEAL),
        ("Monolith", counts["monolith"], AMBER),
        ("Direct", direct, ROSE),
    ]

    W, H = 800, 360
    pad_l, pad_r, pad_t, pad_b = 60, 30, 20, 80
    chart_w = W - pad_l - pad_r
    chart_h = H - pad_t - pad_b - 40  # room for summary strip
    max_v = max(v for _, v, _ in cats)
    # Round up to nearest 5
    max_v_ceil = ((max_v + 4) // 5) * 5

    lines = [svg_open(W, H, "Non-product changesets by repo type")]

    # Y-axis grid + labels
    for tick in range(0, max_v_ceil + 1, 5):
        y = pad_t + chart_h - (tick / max_v_ceil) * chart_h
        lines.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{pad_l + chart_w}" y2="{y:.1f}" class="grid"/>')
        lines.append(f'<text x="{pad_l - 8}" y="{y + 4:.1f}" text-anchor="end" class="sm">{tick}</text>')

    # Axis
    lines.append(f'<line x1="{pad_l}" y1="{pad_t + chart_h}" x2="{pad_l + chart_w}" y2="{pad_t + chart_h}" class="ax"/>')

    # Bars
    n = len(cats)
    bar_w = min(90, (chart_w - 40) // n)
    gap = (chart_w - bar_w * n) / (n + 1)

    for i, (label, val, color) in enumerate(cats):
        x = pad_l + gap + i * (bar_w + gap)
        h = (val / max_v_ceil) * chart_h
        y = pad_t + chart_h - h
        lines.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w}" height="{h:.1f}" fill="{color}" rx="4"/>')
        # Value above bar
        lines.append(f'<text x="{x + bar_w / 2:.1f}" y="{y - 6:.1f}" text-anchor="middle" class="v">{val}</text>')
        # Category below axis
        lines.append(f'<text x="{x + bar_w / 2:.1f}" y="{pad_t + chart_h + 20}" text-anchor="middle" class="cat">{esc(label)}</text>')

    # Summary strip at bottom
    strip_y = H - 36
    summary_parts = [
        f"57 changesets",
        f"1,303 files",
        f"+{combined['additions']:,} / \u2212{combined['deletions']:,} lines",
    ]
    summary_text = "  \u00b7  ".join(summary_parts)
    lines.append(f'<text x="{W / 2}" y="{strip_y}" text-anchor="middle" class="sm">{esc(summary_text)}</text>')

    lines.append(svg_close())
    write_svg(out, "\n".join(lines))


# ── Chart 2: Workstream Coverage ───────────────────────────────────────────

def make_workstream_coverage(pr_rows: list[dict[str, str]], summary: dict, out: Path) -> None:
    agg: dict[str, dict[str, int]] = defaultdict(lambda: {"count": 0, "files": 0})
    for row in pr_rows:
        pr = row["pr_number"]
        for stream, prs in WORKSTREAM_PR_MAP.items():
            if pr in prs:
                agg[stream]["count"] += 1
                agg[stream]["files"] += int(row["changed_files"])
                break

    # Include direct monolith commit
    for commit in summary["true_non_pr_commits"]:
        if commit["sha"].startswith("100d698"):
            agg["Local dev & worktrees"]["count"] += 1
            agg["Local dev & worktrees"]["files"] += int(commit["changed_files"])
            break

    ordered = sorted(agg.items(), key=lambda x: x[1]["count"], reverse=True)
    max_count = max(d["count"] for _, d in ordered)

    W, H = 800, 430
    pad_l, pad_r, pad_t, pad_b = 180, 80, 16, 16
    bar_area_w = W - pad_l - pad_r
    row_h = (H - pad_t - pad_b) / len(ordered)
    bar_h = max(18, row_h * 0.5)

    lines = [svg_open(W, H, "Non-product changesets by workstream")]

    for i, (stream, stats) in enumerate(ordered):
        cy = pad_t + i * row_h + row_h / 2
        count = stats["count"]
        bar_w = (count / max_count) * bar_area_w

        # Stream label
        lines.append(f'<text x="{pad_l - 12}" y="{cy + 4:.1f}" text-anchor="end" class="cat">{esc(stream)}</text>')
        # Background bar
        lines.append(f'<rect x="{pad_l}" y="{cy - bar_h / 2:.1f}" width="{bar_area_w}" height="{bar_h:.1f}" fill="{S100}" rx="4"/>')
        # Data bar
        lines.append(f'<rect x="{pad_l}" y="{cy - bar_h / 2:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" fill="{NAVY}" rx="4"/>')
        # Count label — always outside bar to avoid overlap
        lines.append(f'<text x="{pad_l + bar_w + 8:.1f}" y="{cy + 4:.1f}" class="v">{count}</text>')
        # Files count — in right margin, well clear of bars
        lines.append(f'<text x="{W - 10}" y="{cy + 4:.1f}" text-anchor="end" class="sm">{stats["files"]:,} files</text>')

    lines.append(svg_close())
    write_svg(out, "\n".join(lines))


# ── Chart 3: Heavy CI Lane Pre/Post ────────────────────────────────────────

def make_heavy_lane(ci_timing: dict, out: Path) -> None:
    pre_data = ci_timing["circleci_test_and_checks"]["workflow_wall_runtime_s"]["pre_2697"]
    post_data = ci_timing["circleci_test_and_checks"]["workflow_wall_runtime_s"]["post_2697"]

    pre_val, post_val = pre_data["median_s"], post_data["median_s"]
    pre_n, post_n = pre_data["n"], post_data["n"]
    delta = abs((post_val - pre_val) / pre_val * 100)

    bars = [
        ("Before", pre_val, pre_n, NAVY),
        ("After", post_val, post_n, TEAL),
    ]

    W, H = 800, 320
    pad_l, pad_r, pad_t, pad_b = 70, 40, 20, 60
    chart_w = W - pad_l - pad_r
    chart_h = H - pad_t - pad_b
    max_v = pre_val * 1.12

    lines = [svg_open(W, H, "Heavy CI workflow median runtime before and after")]

    # Grid
    for tick in range(0, int(max_v) + 1, 200):
        y = pad_t + chart_h - (tick / max_v) * chart_h
        lines.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{pad_l + chart_w}" y2="{y:.1f}" class="grid"/>')
        lines.append(f'<text x="{pad_l - 8}" y="{y + 4:.1f}" text-anchor="end" class="sm">{tick}s</text>')

    lines.append(f'<line x1="{pad_l}" y1="{pad_t + chart_h}" x2="{pad_l + chart_w}" y2="{pad_t + chart_h}" class="ax"/>')

    bar_w = 140
    total_bars_w = bar_w * 2 + 120
    start_x = pad_l + (chart_w - total_bars_w) / 2

    for i, (label, val, n, color) in enumerate(bars):
        x = start_x + i * (bar_w + 120)
        h = (val / max_v) * chart_h
        y = pad_t + chart_h - h
        lines.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w}" height="{h:.1f}" fill="{color}" rx="4"/>')
        lines.append(f'<text x="{x + bar_w / 2:.1f}" y="{y - 8:.1f}" text-anchor="middle" class="v">{val:.1f}s</text>')
        lines.append(f'<text x="{x + bar_w / 2:.1f}" y="{pad_t + chart_h + 20}" text-anchor="middle" class="cat">{esc(label)}</text>')
        lines.append(f'<text x="{x + bar_w / 2:.1f}" y="{pad_t + chart_h + 38}" text-anchor="middle" class="sm">n={n}</text>')

    # Delta annotation between bars
    mid_x = start_x + bar_w + 60
    mid_y = pad_t + chart_h / 2
    lines.append(f'<text x="{mid_x:.1f}" y="{mid_y - 8:.1f}" text-anchor="middle"'
                 f' style="font-weight:800; font-size:18px; fill:{EMERALD};">\u2193{delta:.1f}%</text>')

    lines.append(svg_close())
    write_svg(out, "\n".join(lines))


# ── Chart 4: Three CI Phases ──────────────────────────────────────────────

def make_three_phases(three_phase: dict, out: Path) -> None:
    phases = [
        ("Baseline", three_phase["era_summaries"]["linear"]),
        ("Parallel", three_phase["era_summaries"]["multi"]),
        ("Current", three_phase["era_summaries"]["current_pr"]),
    ]
    rt_vals = [d["critical_path_mean_min"] for _, d in phases]
    cr_vals = [d["combined_credits_mean"] for _, d in phases]
    ns = [d["sample_size"] for _, d in phases]
    colors = [NAVY, AMBER, TEAL]

    W, H = 800, 340
    mid = W // 2
    pad_l, pad_r, pad_t, pad_b = 60, 20, 30, 56
    panel_w = mid - pad_l - 10
    chart_h = H - pad_t - pad_b

    lines = [svg_open(W, H, "Three CI phases: runtime and compute")]

    # Panel A: Runtime
    lines.append(f'<text x="{pad_l}" y="{pad_t - 8}" class="heading">Runtime (min)</text>')
    max_rt = max(rt_vals) * 1.15
    for tick in range(0, int(max_rt) + 1, 10):
        y = pad_t + chart_h - (tick / max_rt) * chart_h
        lines.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{pad_l + panel_w}" y2="{y:.1f}" class="grid"/>')
        lines.append(f'<text x="{pad_l - 6}" y="{y + 4:.1f}" text-anchor="end" class="sm">{tick}</text>')
    lines.append(f'<line x1="{pad_l}" y1="{pad_t + chart_h}" x2="{pad_l + panel_w}" y2="{pad_t + chart_h}" class="ax"/>')

    bar_w = 70
    gap_a = (panel_w - bar_w * 3) / 4
    for i, ((name, _), val, color) in enumerate(zip(phases, rt_vals, colors)):
        x = pad_l + gap_a + i * (bar_w + gap_a)
        h = (val / max_rt) * chart_h
        y = pad_t + chart_h - h
        lines.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w}" height="{h:.1f}" fill="{color}" rx="3"/>')
        lines.append(f'<text x="{x + bar_w / 2:.1f}" y="{y - 5:.1f}" text-anchor="middle" class="v">{val:.1f}</text>')
        lines.append(f'<text x="{x + bar_w / 2:.1f}" y="{pad_t + chart_h + 16}" text-anchor="middle" class="cat">{esc(name)}</text>')
        lines.append(f'<text x="{x + bar_w / 2:.1f}" y="{pad_t + chart_h + 32}" text-anchor="middle" class="sm">n={ns[i]}</text>')

    # Divider
    lines.append(f'<line x1="{mid}" y1="{pad_t}" x2="{mid}" y2="{pad_t + chart_h}" stroke="{S200}" stroke-width="1"/>')

    # Panel B: Credits
    rx = mid + 20
    rw = W - rx - pad_r
    lines.append(f'<text x="{rx}" y="{pad_t - 8}" class="heading">Credits per run</text>')
    max_cr = max(cr_vals) * 1.15
    for tick in range(0, int(max_cr) + 1, 100):
        y = pad_t + chart_h - (tick / max_cr) * chart_h
        lines.append(f'<line x1="{rx}" y1="{y:.1f}" x2="{rx + rw}" y2="{y:.1f}" class="grid"/>')
        lines.append(f'<text x="{rx - 6}" y="{y + 4:.1f}" text-anchor="end" class="sm">{tick}</text>')
    lines.append(f'<line x1="{rx}" y1="{pad_t + chart_h}" x2="{rx + rw}" y2="{pad_t + chart_h}" class="ax"/>')

    gap_b = (rw - bar_w * 3) / 4
    for i, ((name, _), val, color) in enumerate(zip(phases, cr_vals, colors)):
        x = rx + gap_b + i * (bar_w + gap_b)
        h = (val / max_cr) * chart_h
        y = pad_t + chart_h - h
        lines.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w}" height="{h:.1f}" fill="{color}" rx="3"/>')
        lines.append(f'<text x="{x + bar_w / 2:.1f}" y="{y - 5:.1f}" text-anchor="middle" class="v">{val:.0f}</text>')
        lines.append(f'<text x="{x + bar_w / 2:.1f}" y="{pad_t + chart_h + 16}" text-anchor="middle" class="cat">{esc(name)}</text>')
        lines.append(f'<text x="{x + bar_w / 2:.1f}" y="{pad_t + chart_h + 32}" text-anchor="middle" class="sm">n={ns[i]}</text>')

    # Delta annotation
    delta_rt = abs(three_phase["deltas"]["current_vs_linear"]["critical_path_mean_pct"])
    delta_cr = abs(three_phase["deltas"]["current_vs_linear"]["combined_credits_mean_pct"])
    lines.append(f'<text x="{pad_l + panel_w / 2}" y="{pad_t + chart_h + 50}" text-anchor="middle" class="smb">\u2193 {delta_rt:.0f}% faster</text>')
    lines.append(f'<text x="{rx + rw / 2}" y="{pad_t + chart_h + 50}" text-anchor="middle" class="smb">\u2193 {delta_cr:.0f}% fewer credits</text>')

    lines.append(svg_close())
    write_svg(out, "\n".join(lines))


# ── Chart 5: Waiting-Time Model ───────────────────────────────────────────

def make_waiting_time(out: Path) -> None:
    components = [
        ("Faster heavy CI", 11.07, NAVY),
        ("Early stop on failed checks", 6.38, AMBER),
        ("Skipped irrelevant deep runs", 3.94, EMERALD),
    ]
    total = sum(v for _, v, _ in components)

    W, H = 800, 180
    pad_x, pad_t = 30, 16
    bar_w = W - 2 * pad_x
    bar_h = 40
    bar_y = pad_t

    lines = [svg_open(W, H, "Modeled waiting-time reduction")]

    # Stacked bar
    x = pad_x
    for label, val, color in components:
        w = bar_w * (val / total)
        lines.append(f'<rect x="{x:.1f}" y="{bar_y}" width="{w:.1f}" height="{bar_h}" fill="{color}" rx="4"/>')
        lines.append(f'<text x="{x + w / 2:.1f}" y="{bar_y + bar_h / 2 + 5}" text-anchor="middle" class="vl">{val:.1f}h</text>')
        x += w

    # Fix corners: overlay rects to clean up
    # (the rx on each segment creates inner rounded corners; acceptable for blog quality)

    # Legend
    legend_y = bar_y + bar_h + 28
    lx = pad_x
    for label, val, color in components:
        lines.append(f'<rect x="{lx}" y="{legend_y - 10}" width="12" height="12" rx="2" fill="{color}"/>')
        lines.append(f'<text x="{lx + 18}" y="{legend_y}" class="sm">{esc(label)} ({val:.1f}h)</text>')
        lx += 260

    # Total
    lines.append(f'<text x="{W / 2}" y="{H - 14}" text-anchor="middle" class="heading">Total modeled reduction: {total:.1f} hours</text>')

    lines.append(svg_close())
    write_svg(out, "\n".join(lines))


# ── Chart 6: Testing Platform Phases ──────────────────────────────────────

def make_testing_phases(out: Path) -> None:
    phases = [
        ("Phase 1", "Infra foundation"),
        ("Phase 2\u20134", "Role-based E2E"),
        ("Phase 5", "Unit + integration"),
        ("Phase 6", "CI + sandbox"),
        ("Phase 7", "Deterministic"),
    ]
    colors = [NAVY, "#2d5f8f", "#3b7ab3", TEAL, EMERALD]

    W, H = 800, 110
    pad_x = 20
    n = len(phases)
    arrow_w = 16
    total_arrows = (n - 1) * arrow_w
    box_w = (W - 2 * pad_x - total_arrows) / n
    box_h = 58
    box_y = (H - box_h) / 2

    lines = [svg_open(W, H, "Testing platform phased rollout")]

    for i, ((label, desc), color) in enumerate(zip(phases, colors)):
        x = pad_x + i * (box_w + arrow_w)
        lines.append(f'<rect x="{x:.1f}" y="{box_y:.1f}" width="{box_w:.1f}" height="{box_h}" rx="6" fill="{color}"/>')
        lines.append(f'<text x="{x + box_w / 2:.1f}" y="{box_y + 24}" text-anchor="middle" class="box-label">{esc(label)}</text>')
        lines.append(f'<text x="{x + box_w / 2:.1f}" y="{box_y + 42}" text-anchor="middle" class="box-sub">{esc(desc)}</text>')

        if i < n - 1:
            ax = x + box_w + 2
            ay = box_y + box_h / 2
            lines.append(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{ax + arrow_w - 6:.1f}" y2="{ay:.1f}" stroke="{S400}" stroke-width="2"/>')
            lines.append(f'<polygon points="{ax + arrow_w - 2:.1f},{ay:.1f} {ax + arrow_w - 8:.1f},{ay - 4:.1f} {ax + arrow_w - 8:.1f},{ay + 4:.1f}" fill="{S400}"/>')

    lines.append(svg_close())
    write_svg(out, "\n".join(lines))


# ── Chart 7: Local Dev Isolation ──────────────────────────────────────────

def make_local_dev(out: Path) -> None:
    W, H = 800, 240
    mid = W // 2
    pad = 20
    panel_w = mid - pad - 8

    lines = [svg_open(W, H, "Local development before and after isolation")]

    # Before panel
    lines.append(f'<rect x="{pad}" y="10" width="{panel_w}" height="{H - 20}" rx="8" fill="{S50}" stroke="{RED_300}" stroke-width="1.5"/>')
    lines.append(f'<text x="{pad + 14}" y="34" class="bad">Before: shared defaults</text>')
    before_ports = [("Worktree A", "8000"), ("Worktree B", "8000"), ("Worktree C", "8000")]
    for i, (name, port) in enumerate(before_ports):
        y = 52 + i * 56
        lines.append(f'<rect x="{pad + 14}" y="{y}" width="{panel_w / 2 - 10:.0f}" height="42" rx="4" fill="{WHITE}" stroke="{S300}" stroke-width="1"/>')
        lines.append(f'<text x="{pad + 24}" y="{y + 26}" class="sm-dark">{esc(name)}</text>')
        px = pad + panel_w / 2 + 14
        lines.append(f'<rect x="{px:.0f}" y="{y + 6}" width="{panel_w / 2 - 30:.0f}" height="30" rx="4" fill="{RED_50}" stroke="{RED_300}" stroke-width="1"/>')
        lines.append(f'<text x="{px + (panel_w / 2 - 30) / 2:.0f}" y="{y + 26}" text-anchor="middle" class="bad">:{port}</text>')

    # After panel
    ax = mid + 8
    lines.append(f'<rect x="{ax}" y="10" width="{panel_w}" height="{H - 20}" rx="8" fill="{S50}" stroke="{GREEN_300}" stroke-width="1.5"/>')
    lines.append(f'<text x="{ax + 14}" y="34" class="good">After: deterministic isolation</text>')
    after_ports = [("Primary", "8000"), ("Worktree B", "18021"), ("Worktree C", "18037")]
    for i, (name, port) in enumerate(after_ports):
        y = 52 + i * 56
        lines.append(f'<rect x="{ax + 14}" y="{y}" width="{panel_w / 2 - 10:.0f}" height="42" rx="4" fill="{WHITE}" stroke="{S300}" stroke-width="1"/>')
        lines.append(f'<text x="{ax + 24}" y="{y + 26}" class="sm-dark">{esc(name)}</text>')
        px = ax + panel_w / 2 + 14
        lines.append(f'<rect x="{px:.0f}" y="{y + 6}" width="{panel_w / 2 - 30:.0f}" height="30" rx="4" fill="{GREEN_50}" stroke="{GREEN_300}" stroke-width="1"/>')
        lines.append(f'<text x="{px + (panel_w / 2 - 30) / 2:.0f}" y="{y + 26}" text-anchor="middle" class="good">:{port}</text>')

    lines.append(svg_close())
    write_svg(out, "\n".join(lines))


# ── Chart 8: Ops Safety Surfaces ──────────────────────────────────────────

def make_ops_safety(out: Path) -> None:
    cards = [
        ("Snapshot ops", "Manual runbook steps", "Scripted flow + alerts"),
        ("Support shell", "Unclear failure modes", "Diagnostics + auto-reconcile"),
        ("Admin commands", "Raw shell folklore", "Allowlisted queue + audit"),
        ("High-impact actions", "Single-step mutation", "Two-step confirmation"),
    ]

    W, H = 800, 230
    pad = 20
    cols, rows = 2, 2
    gap = 14
    card_w = (W - 2 * pad - gap) / cols
    card_h = (H - 2 * pad - gap) / rows

    lines = [svg_open(W, H, "Operational safety surfaces before and after")]

    for idx, (title, before, after) in enumerate(cards):
        col = idx % cols
        row = idx // cols
        x = pad + col * (card_w + gap)
        y = pad + row * (card_h + gap)

        lines.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{card_w:.1f}" height="{card_h:.1f}" rx="6" fill="{S50}" stroke="{S200}" stroke-width="1"/>')
        lines.append(f'<text x="{x + 12:.1f}" y="{y + 22}" class="heading">{esc(title)}</text>')
        lines.append(f'<text x="{x + 12:.1f}" y="{y + 44}" class="bad">\u2717 {esc(before)}</text>')
        lines.append(f'<text x="{x + 12:.1f}" y="{y + 62}" class="good">\u2713 {esc(after)}</text>')

    lines.append(svg_close())
    write_svg(out, "\n".join(lines))


# ── Chart 9: Security & Dependabot ────────────────────────────────────────

def make_security_waves(out: Path) -> None:
    W, H = 800, 220
    pad = 20

    lines = [svg_open(W, H, "Security remediation layered approach")]

    # Three horizontal lanes
    lane_h = 50
    lane_gap = 12
    label_w = 120

    lanes = [
        ("Layer 1", "Dep + CVE waves", [
            ("Wave 1: Critical", NAVY),
            ("Wave 2: Crypto chain", "#2d5f8f"),
            ("Wave 3: Transitive", TEAL),
        ]),
        ("Layer 2", "Workflow hardening", [
            ("CI input sanitized", S500),
            ("PII removed from telemetry", S500),
        ]),
        ("Layer 3", "Release closures", [
            ("Faster, safer dependency closure with no delivery churn", EMERALD),
        ]),
    ]

    for li, (label, sublabel, blocks) in enumerate(lanes):
        ly = pad + li * (lane_h + lane_gap)

        # Label
        lines.append(f'<text x="{pad}" y="{ly + 20}" class="heading">{esc(label)}</text>')
        lines.append(f'<text x="{pad}" y="{ly + 36}" class="sm">{esc(sublabel)}</text>')

        # Blocks
        block_area_x = pad + label_w + 10
        block_area_w = W - block_area_x - pad
        n = len(blocks)
        block_gap = 8
        block_w = (block_area_w - (n - 1) * block_gap) / n

        for bi, (text, color) in enumerate(blocks):
            bx = block_area_x + bi * (block_w + block_gap)
            lines.append(f'<rect x="{bx:.1f}" y="{ly}" width="{block_w:.1f}" height="{lane_h}" rx="6" fill="{color}"/>')
            # Truncate text to fit
            lines.append(f'<text x="{bx + block_w / 2:.1f}" y="{ly + lane_h / 2 + 4:.1f}" text-anchor="middle" class="vl" style="font-size:11px">{esc(text)}</text>')

    lines.append(svg_close())
    write_svg(out, "\n".join(lines))


# ── Chart 10: Skills Flywheel ─────────────────────────────────────────────

def make_skills_flywheel(out: Path) -> None:
    W, H = 800, 340
    cx, cy = W // 2, 155  # push center up to leave room for stats

    lines = [svg_open(W, H, "Open-source skills compounding flywheel")]

    import math

    # Center label
    lines.append(f'<circle cx="{cx}" cy="{cy}" r="46" fill="{S50}" stroke="{S200}" stroke-width="1.5"/>')
    lines.append(f'<text x="{cx}" y="{cy - 4}" text-anchor="middle" class="heading" style="font-size:11px">Compounding</text>')
    lines.append(f'<text x="{cx}" y="{cy + 12}" text-anchor="middle" class="sm" style="font-size:10px">loop</text>')

    # Four nodes around the center
    nodes = [
        (cx, cy - 100, "1. Discover pattern"),
        (cx + 190, cy, "2. Encode as skill"),
        (cx, cy + 100, "3. Team reuse"),
        (cx - 190, cy, "4. Faster onboarding"),
    ]
    node_w, node_h = 155, 36

    for nx, ny, text in nodes:
        lines.append(f'<rect x="{nx - node_w / 2:.1f}" y="{ny - node_h / 2:.1f}" width="{node_w}" height="{node_h}" rx="6" fill="{NAVY}"/>')
        lines.append(f'<text x="{nx:.1f}" y="{ny + 4:.1f}" text-anchor="middle" class="vl" style="font-size:12px">{esc(text)}</text>')

    # Arrows between nodes (clockwise)
    arrow_pairs = [
        (cx + 58, cy - 90, cx + 160, cy - 28),   # 1 -> 2
        (cx + 160, cy + 28, cx + 58, cy + 90),    # 2 -> 3
        (cx - 58, cy + 90, cx - 160, cy + 28),    # 3 -> 4
        (cx - 160, cy - 28, cx - 58, cy - 90),    # 4 -> 1
    ]
    for x1, y1, x2, y2 in arrow_pairs:
        lines.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{S400}" stroke-width="1.5"/>')
        dx, dy = x2 - x1, y2 - y1
        length = max(math.sqrt(dx * dx + dy * dy), 1)
        ux, uy = dx / length, dy / length
        px, py = -uy, ux
        hx, hy = x2 - ux * 8, y2 - uy * 8
        lines.append(f'<polygon points="{x2:.1f},{y2:.1f} {hx + px * 4:.1f},{hy + py * 4:.1f} {hx - px * 4:.1f},{hy - py * 4:.1f}" fill="{S400}"/>')

    # Stats well below the flywheel
    stats = "15 plugins  \u00b7  17 skills  \u00b7  37 commands"
    lines.append(f'<text x="{cx}" y="{H - 24}" text-anchor="middle" class="sm">{esc(stats)}</text>')

    lines.append(svg_close())
    write_svg(out, "\n".join(lines))


# ── Chart 11: Reinforcement System Map ────────────────────────────────────

def make_reinforcement_map(out: Path) -> None:
    W, H = 800, 390
    pad = 20
    top_offset = 30  # space for feedback label at top

    lines = [svg_open(W, H, "How workstreams reinforced each other")]

    import math

    # Source nodes (left column)
    sources = [
        ("Faster CI loop", NAVY),
        ("Local-dev isolation", "#2d5f8f"),
        ("Ops safety rails", TEAL),
        ("Security + debt", AMBER),
    ]
    bridges = [
        "Cleaner test signal",
        "Faster validation",
        "Stable change surface",
    ]
    results = [
        ("Codified skills", INDIGO),
        ("Team learning", EMERALD),
    ]

    content_h = H - top_offset - pad
    src_x, src_w, src_h = pad, 150, 40
    brg_x, brg_w, brg_h = 220, 160, 40
    res_x, res_w, res_h = 440, 150, 40

    # Source nodes
    src_ys = []
    src_gap = (content_h - len(sources) * src_h) / (len(sources) + 1)
    for i, (label, color) in enumerate(sources):
        y = top_offset + src_gap + i * (src_h + src_gap)
        src_ys.append(y + src_h / 2)
        lines.append(f'<rect x="{src_x}" y="{y:.1f}" width="{src_w}" height="{src_h}" rx="6" fill="{color}"/>')
        lines.append(f'<text x="{src_x + src_w / 2}" y="{y + src_h / 2 + 4:.1f}" text-anchor="middle" class="vl" style="font-size:11px">{esc(label)}</text>')

    # Bridge nodes
    brg_ys = []
    brg_gap = (content_h - len(bridges) * brg_h) / (len(bridges) + 1)
    for i, label in enumerate(bridges):
        y = top_offset + brg_gap + i * (brg_h + brg_gap)
        brg_ys.append(y + brg_h / 2)
        lines.append(f'<rect x="{brg_x}" y="{y:.1f}" width="{brg_w}" height="{brg_h}" rx="6" fill="{S100}" stroke="{S300}" stroke-width="1"/>')
        lines.append(f'<text x="{brg_x + brg_w / 2}" y="{y + brg_h / 2 + 4:.1f}" text-anchor="middle" class="sm-dark">{esc(label)}</text>')

    # Result nodes
    res_ys = []
    res_gap = (content_h - len(results) * res_h) / (len(results) + 1)
    for i, (label, color) in enumerate(results):
        y = top_offset + res_gap + i * (res_h + res_gap)
        res_ys.append(y + res_h / 2)
        lines.append(f'<rect x="{res_x}" y="{y:.1f}" width="{res_w}" height="{res_h}" rx="6" fill="{color}"/>')
        lines.append(f'<text x="{res_x + res_w / 2}" y="{y + res_h / 2 + 4:.1f}" text-anchor="middle" class="vl" style="font-size:11px">{esc(label)}</text>')

    # Attention reallocation box (right side)
    att_x = 640
    att_w = W - att_x - pad
    att_h = 70
    att_y = top_offset + content_h / 2 - att_h / 2
    lines.append(f'<rect x="{att_x}" y="{att_y:.1f}" width="{att_w}" height="{att_h}" rx="6" fill="{S50}" stroke="{S300}" stroke-width="1"/>')
    lines.append(f'<text x="{att_x + att_w / 2}" y="{att_y + att_h / 2 - 6:.1f}" text-anchor="middle" class="heading" style="font-size:11px">Attention</text>')
    lines.append(f'<text x="{att_x + att_w / 2}" y="{att_y + att_h / 2 + 10:.1f}" text-anchor="middle" class="sm" style="font-size:10px">reallocation</text>')

    def draw_arrow(x1: float, y1: float, x2: float, y2: float, color: str = S300) -> None:
        lines.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="1.5"/>')
        dx, dy = x2 - x1, y2 - y1
        length = max(math.sqrt(dx * dx + dy * dy), 1)
        ux, uy = dx / length, dy / length
        px, py = -uy, ux
        hx, hy = x2 - ux * 7, y2 - uy * 7
        lines.append(f'<polygon points="{x2:.1f},{y2:.1f} {hx + px * 3:.1f},{hy + py * 3:.1f} {hx - px * 3:.1f},{hy - py * 3:.1f}" fill="{color}"/>')

    # Source -> nearest bridge
    src_right = src_x + src_w
    brg_left = brg_x
    for i, sy in enumerate(src_ys):
        bi = min(i, len(brg_ys) - 1)
        if i == 0:
            bi = 0
        elif i == 1:
            bi = 1
        elif i >= 2:
            bi = min(i - 1, len(brg_ys) - 1)
        draw_arrow(src_right, sy, brg_left, brg_ys[bi])

    # Bridge -> results
    brg_right = brg_x + brg_w
    res_left = res_x
    for i, by in enumerate(brg_ys):
        ri = 0 if i < 2 else 1
        draw_arrow(brg_right, by, res_left, res_ys[ri])

    # Results -> attention
    for ry in res_ys:
        draw_arrow(res_x + res_w, ry, att_x, att_y + att_h / 2)

    # Feedback curve from attention back to sources — keep well inside viewBox
    curve_top = top_offset + 6
    lines.append(f'<path d="M {att_x + att_w / 2} {att_y} C {att_x + att_w / 2} {curve_top}, {src_x + src_w / 2} {curve_top}, {src_x + src_w / 2} {src_ys[0] - src_h / 2}" '
                 f'fill="none" stroke="{S400}" stroke-width="1.5" stroke-dasharray="4 3"/>')
    lines.append(f'<polygon points="{src_x + src_w / 2},{src_ys[0] - src_h / 2} {src_x + src_w / 2 - 4},{src_ys[0] - src_h / 2 - 8} {src_x + src_w / 2 + 4},{src_ys[0] - src_h / 2 - 8}" fill="{S400}"/>')
    lines.append(f'<text x="{W / 2}" y="{top_offset - 6}" text-anchor="middle" class="sm" style="font-size:10px; font-style:italic">feedback: codified learning improves upstream quality</text>')

    lines.append(svg_close())
    write_svg(out, "\n".join(lines))


# ── Chart 12: CI Dedup Effect ─────────────────────────────────────────────

def make_ci_dedup(out: Path) -> None:
    """Before/after dedup: push vs PR triggered runs."""
    W, H = 800, 240
    pad_l, pad_r, pad_t = 30, 30, 16
    mid = W // 2

    lines = [svg_open(W, H, "CI deduplication: push vs PR trigger ratio")]

    # Before panel
    bx = pad_l
    pw = mid - pad_l - 10
    lines.append(f'<text x="{bx + pw / 2}" y="{pad_t + 14}" text-anchor="middle" class="heading">Before dedup</text>')

    # Stacked bar showing 399 push vs 22 PR
    bar_y, bar_h = pad_t + 30, 100
    total_before = 399 + 22
    # Reserve space for "22 PR" label on the right
    bar_w = pw - 50  # leave 50px for label
    push_w = bar_w * (399 / total_before)
    pr_w = bar_w * (22 / total_before)

    lines.append(f'<rect x="{bx}" y="{bar_y}" width="{push_w:.1f}" height="{bar_h}" fill="{ROSE}" rx="4"/>')
    lines.append(f'<text x="{bx + push_w / 2:.1f}" y="{bar_y + bar_h / 2 + 5}" text-anchor="middle" class="vl">399 push</text>')
    lines.append(f'<rect x="{bx + push_w:.1f}" y="{bar_y}" width="{pr_w:.1f}" height="{bar_h}" fill="{TEAL}" rx="4"/>')
    # PR label outside bar, within panel
    lines.append(f'<text x="{bx + push_w + pr_w + 8:.1f}" y="{bar_y + bar_h / 2 + 5}" class="v">22 PR</text>')

    lines.append(f'<text x="{bx + pw / 2}" y="{bar_y + bar_h + 22}" text-anchor="middle" class="sm">18x more push runs than PR runs</text>')
    lines.append(f'<text x="{bx + pw / 2}" y="{bar_y + bar_h + 40}" text-anchor="middle" class="bad">Redundant work on every commit</text>')

    # After panel
    ax = mid + 10
    aw = W - ax - pad_r
    lines.append(f'<text x="{ax + aw / 2}" y="{pad_t + 14}" text-anchor="middle" class="heading">After dedup</text>')

    total_after = 9 + 36
    push_w2 = aw * (9 / total_after)
    pr_w2 = aw * (36 / total_after)

    lines.append(f'<rect x="{ax}" y="{bar_y}" width="{push_w2:.1f}" height="{bar_h}" fill="{ROSE}" rx="4"/>')
    lines.append(f'<text x="{ax + push_w2 / 2:.1f}" y="{bar_y + bar_h / 2 + 5}" text-anchor="middle" class="vl" style="font-size:12px">9</text>')
    lines.append(f'<rect x="{ax + push_w2:.1f}" y="{bar_y}" width="{pr_w2:.1f}" height="{bar_h}" fill="{TEAL}" rx="4"/>')
    lines.append(f'<text x="{ax + push_w2 + pr_w2 / 2:.1f}" y="{bar_y + bar_h / 2 + 5}" text-anchor="middle" class="vl">36 PR</text>')

    lines.append(f'<text x="{ax + aw / 2}" y="{bar_y + bar_h + 22}" text-anchor="middle" class="sm">0.25x ratio - only meaningful runs</text>')
    lines.append(f'<text x="{ax + aw / 2}" y="{bar_y + bar_h + 40}" text-anchor="middle" class="good">Redundant runs eliminated</text>')

    # Divider
    lines.append(f'<line x1="{mid}" y1="{pad_t + 24}" x2="{mid}" y2="{bar_y + bar_h + 10}" stroke="{S200}" stroke-width="1"/>')

    lines.append(svg_close())
    write_svg(out, "\n".join(lines))


# ── Chart 13: Deep Check Lane ─────────────────────────────────────────────

def make_deep_check_lane(ci_timing: dict, out: Path) -> None:
    """The deepest check lane improvement: 332s -> 95.5s."""
    jobs = ci_timing["circleci_test_and_checks"]["job_runtime_s"]
    checks_pre = jobs["Checks (Deep DB/RLS)"]["pre_2697"]
    checks_post = jobs["Checks (Deep DB/RLS)"]["post_2697"]

    items = [
        ("Overall workflow", 942.5, 675.0),
        ("Deep DB/RLS checks", checks_pre["median_s"], checks_post["median_s"]),
        ("Tests (Optimo)", 621.0, 557.5),
        ("Tests (Diversio)", 584.5, 514.5),
    ]

    W, H = 800, 260
    pad_l, pad_r, pad_t, pad_b = 160, 30, 16, 16
    bar_area_w = W - pad_l - pad_r
    row_h = (H - pad_t - pad_b) / len(items)
    bar_h = min(22, row_h * 0.45)
    max_v = max(b for _, b, _ in items) * 1.05

    lines = [svg_open(W, H, "CI job-level improvements after runtime image")]

    for i, (label, before, after) in enumerate(items):
        cy = pad_t + i * row_h + row_h / 2
        pct = abs((after - before) / before * 100)

        # Label
        lines.append(f'<text x="{pad_l - 12}" y="{cy - 4:.1f}" text-anchor="end" class="cat">{esc(label)}</text>')
        delta_color = EMERALD if pct > 25 else TEAL
        lines.append(f'<text x="{pad_l - 12}" y="{cy + 12:.1f}" text-anchor="end" class="good" style="font-size:10px">\u2193{pct:.0f}%</text>')

        # Before bar (faded)
        bw = (before / max_v) * bar_area_w
        lines.append(f'<rect x="{pad_l}" y="{cy - bar_h - 2:.1f}" width="{bw:.1f}" height="{bar_h:.1f}" fill="{S200}" rx="3"/>')
        lines.append(f'<text x="{pad_l + bw + 6:.1f}" y="{cy - bar_h / 2 + 2:.1f}" class="sm">{before:.0f}s</text>')

        # After bar
        aw = (after / max_v) * bar_area_w
        lines.append(f'<rect x="{pad_l}" y="{cy + 2:.1f}" width="{aw:.1f}" height="{bar_h:.1f}" fill="{TEAL}" rx="3"/>')
        lines.append(f'<text x="{pad_l + aw + 6:.1f}" y="{cy + bar_h / 2 + 6:.1f}" class="v" style="font-size:12px">{after:.0f}s</text>')

    # Legend
    ly = H - 10
    lines.append(f'<rect x="{pad_l}" y="{ly - 8}" width="10" height="10" rx="2" fill="{S200}"/>')
    lines.append(f'<text x="{pad_l + 16}" y="{ly}" class="sm">Before</text>')
    lines.append(f'<rect x="{pad_l + 80}" y="{ly - 8}" width="10" height="10" rx="2" fill="{TEAL}"/>')
    lines.append(f'<text x="{pad_l + 96}" y="{ly}" class="sm">After</text>')

    lines.append(svg_close())
    write_svg(out, "\n".join(lines))


# ── Chart 14: Snapshot Automation ─────────────────────────────────────────

def make_snapshot_flow(out: Path) -> None:
    """Before: 6 manual steps. After: one command."""
    steps = ["Dump SQL", "Package", "Upload", "Restore", "Snapshot", "Notify Slack"]

    W, H = 800, 160
    pad = 20

    lines = [svg_open(W, H, "Database snapshot automation")]

    # Before: chain of manual steps
    lines.append(f'<text x="{pad}" y="22" class="bad">Before: 6 manual steps, in order, by memory</text>')
    n = len(steps)
    step_w = (W - 2 * pad - (n - 1) * 8) / n
    for i, step in enumerate(steps):
        x = pad + i * (step_w + 8)
        lines.append(f'<rect x="{x:.1f}" y="32" width="{step_w:.1f}" height="32" rx="4" fill="{S100}" stroke="{RED_300}" stroke-width="1"/>')
        lines.append(f'<text x="{x + step_w / 2:.1f}" y="52" text-anchor="middle" class="sm-dark" style="font-size:10px">{esc(step)}</text>')
        if i < n - 1:
            ax = x + step_w + 1
            lines.append(f'<text x="{ax + 3:.1f}" y="52" class="sm" style="font-size:10px">\u2192</text>')

    # After: one command
    lines.append(f'<text x="{pad}" y="92" class="good">After: one command, with preflight checks and Slack notification</text>')
    lines.append(f'<rect x="{pad}" y="102" width="{W - 2 * pad}" height="36" rx="6" fill="{EMERALD}"/>')
    lines.append(f'<text x="{W / 2}" y="124" text-anchor="middle" class="vl" style="font-size:13px">./manage.sh snapshot create \u2014 runs full pipeline with error handling</text>')

    lines.append(svg_close())
    write_svg(out, "\n".join(lines))


# ── Chart 15: Admin Safety ────────────────────────────────────────────────

def make_admin_safety(out: Path) -> None:
    """Before: one click mutates. After: plan → confirm → execute."""
    W, H = 800, 130
    pad = 20

    lines = [svg_open(W, H, "Admin action safety model")]

    mid = W // 2

    # Before
    bw = mid - pad - 8
    lines.append(f'<rect x="{pad}" y="10" width="{bw}" height="{H - 20}" rx="8" fill="{S50}" stroke="{RED_300}" stroke-width="1.5"/>')
    lines.append(f'<text x="{pad + 14}" y="34" class="bad">Before: click and pray</text>')
    lines.append(f'<rect x="{pad + 14}" y="46" width="{bw - 28}" height="34" rx="4" fill="{RED_50}" stroke="{RED_300}" stroke-width="1"/>')
    lines.append(f'<text x="{pad + bw / 2}" y="68" text-anchor="middle" class="sm-dark">Select action \u2192 immediate mutation (no undo)</text>')
    lines.append(f'<text x="{pad + 14}" y="104" class="sm">One accidental click = irreversible data loss</text>')

    # After
    ax = mid + 8
    aw = W - ax - pad
    lines.append(f'<rect x="{ax}" y="10" width="{aw}" height="{H - 20}" rx="8" fill="{S50}" stroke="{GREEN_300}" stroke-width="1.5"/>')
    lines.append(f'<text x="{ax + 14}" y="34" class="good">After: plan \u2192 confirm \u2192 execute</text>')
    step_w = (aw - 28 - 16) / 3
    for i, (label, color) in enumerate([("Review impact", NAVY), ("Confirm scope", "#2d5f8f"), ("Execute", EMERALD)]):
        sx = ax + 14 + i * (step_w + 8)
        lines.append(f'<rect x="{sx:.1f}" y="46" width="{step_w:.1f}" height="34" rx="4" fill="{color}"/>')
        lines.append(f'<text x="{sx + step_w / 2:.1f}" y="68" text-anchor="middle" class="vl" style="font-size:10px">{esc(label)}</text>')
    lines.append(f'<text x="{ax + 14}" y="104" class="sm">Eligibility checks + risk context before any mutation</text>')

    lines.append(svg_close())
    write_svg(out, "\n".join(lines))


# ── Chart 16: Migration Squash ────────────────────────────────────────────

def make_migration_squash(out: Path) -> None:
    """Before: tangled chain. After: clean lineage."""
    W, H = 800, 120
    pad = 20

    lines = [svg_open(W, H, "Migration topology simplification")]

    mid = W // 2

    # Before: tangled nodes
    bw = mid - pad - 8
    lines.append(f'<rect x="{pad}" y="10" width="{bw}" height="{H - 20}" rx="8" fill="{S50}" stroke="{RED_300}" stroke-width="1.5"/>')
    lines.append(f'<text x="{pad + 14}" y="30" class="bad">Before: tangled migration graph</text>')
    # Draw messy nodes
    nodes_x = [pad + 30, pad + 80, pad + 130, pad + 170, pad + 220, pad + 270, pad + 310]
    for i, nx in enumerate(nodes_x):
        ny = 55 + (i % 3) * 18
        lines.append(f'<circle cx="{nx}" cy="{ny}" r="8" fill="{S300}"/>')
        if i > 0:
            px = nodes_x[i - 1]
            py = 55 + ((i - 1) % 3) * 18
            lines.append(f'<line x1="{px + 8}" y1="{py}" x2="{nx - 8}" y2="{ny}" stroke="{S300}" stroke-width="1"/>')
            if i > 1:
                ppx = nodes_x[i - 2]
                ppy = 55 + ((i - 2) % 3) * 18
                lines.append(f'<line x1="{ppx + 8}" y1="{ppy}" x2="{nx - 8}" y2="{ny}" stroke="{S200}" stroke-width="1" stroke-dasharray="2 2"/>')

    # After: clean chain
    ax = mid + 8
    aw = W - ax - pad
    lines.append(f'<rect x="{ax}" y="10" width="{aw}" height="{H - 20}" rx="8" fill="{S50}" stroke="{GREEN_300}" stroke-width="1.5"/>')
    lines.append(f'<text x="{ax + 14}" y="30" class="good">After: squashed, clean lineage</text>')
    clean_nodes = [ax + 60, ax + 140, ax + 220, ax + 300]
    for i, nx in enumerate(clean_nodes):
        lines.append(f'<circle cx="{nx}" cy="68" r="10" fill="{TEAL}"/>')
        if i > 0:
            lines.append(f'<line x1="{clean_nodes[i-1] + 10}" y1="68" x2="{nx - 10}" y2="68" stroke="{TEAL}" stroke-width="2"/>')

    lines.append(svg_close())
    write_svg(out, "\n".join(lines))


# ── Main ──────────────────────────────────────────────────────────────────

def main() -> None:
    data_dir = DEFAULT_DATA_DIR
    if not data_dir.exists():
        raise SystemExit(f"Data dir not found: {data_dir}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    summary = json.loads((data_dir / "major_non_product_summary.json").read_text(encoding="utf-8"))
    timing = json.loads((data_dir / "ci_timing_analysis.json").read_text(encoding="utf-8"))
    three_phase = json.loads((data_dir / "ci_three_era_comparison.json").read_text(encoding="utf-8"))
    pr_rows = read_major_pr_rows(data_dir)

    print("Generating charts...")
    make_changeset_mix(summary, OUTPUT_DIR / "changeset-mix.svg")
    make_workstream_coverage(pr_rows, summary, OUTPUT_DIR / "workstream-coverage.svg")
    make_heavy_lane(timing, OUTPUT_DIR / "ci-heavy-lane-pre-post.svg")
    make_three_phases(three_phase, OUTPUT_DIR / "ci-three-phases-runtime-credits.svg")
    make_waiting_time(OUTPUT_DIR / "ci-waiting-time-model.svg")
    make_ci_dedup(OUTPUT_DIR / "ci-dedup-effect.svg")
    make_deep_check_lane(timing, OUTPUT_DIR / "ci-deep-check-lane.svg")
    make_testing_phases(OUTPUT_DIR / "testing-platform-phases.svg")
    make_local_dev(OUTPUT_DIR / "local-dev-isolation.svg")
    make_ops_safety(OUTPUT_DIR / "ops-safety-surfaces.svg")
    make_snapshot_flow(OUTPUT_DIR / "snapshot-automation.svg")
    make_admin_safety(OUTPUT_DIR / "admin-safety-model.svg")
    make_migration_squash(OUTPUT_DIR / "migration-squash.svg")
    make_security_waves(OUTPUT_DIR / "security-dependabot-program.svg")
    make_skills_flywheel(OUTPUT_DIR / "skills-compounding-flywheel.svg")
    make_reinforcement_map(OUTPUT_DIR / "reinforcement-system-map.svg")
    print(f"Done. Charts written to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
