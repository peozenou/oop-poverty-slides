"""Static figures for the slide deck (matplotlib). Run from repo root:
   python slides/make_figures.py

Figure 1  fig_global_trend.png          global FH, its components and SPL poverty, 2000-2022
Figure 2  fig_decomp_illustration.png   exact macro decomposition with the 2025 GMR global figures (waterfall)
Figure 3  fig_parade_*.png              Pen's parade schematics: components of the identity; stories A and B;
                                         mechanical poverty effect; increased access effect
Figure 4  fig_hypothetical_*.png        hypothetical country (simulated): repeated cross-sections and panel
                                         (numbers from code/python/hypothetical_country.py)
"""
import os, sys
import pandas as pd, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.transforms import blended_transform_factory

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "code", "python"))
from oop_decomp import decompose_macro

OUT = os.path.join(ROOT, "slides", "figures"); os.makedirs(OUT, exist_ok=True)

# Palette shared by every figure of the deck (slide 3 sets the convention)
PURPLE = "#6a3d9a"    # financial hardship (SDG 3.8.2 total)
DORANGE = "#c2410c"   # impoverishing OOP (further pushed + pushed)
ORANGE = "#f0901e"    # large, non-impoverishing OOP
BLACK = "#111111"     # poverty (SPL headcount; poverty component)
NAVY = "#1f3a6e"      # financial protection among the poor (delta); parade curve; parameter labels
LBLUE = "#6f9bd8"     # financial protection among the non-poor (psi)
GREEN = "#2e8b57"     # OOP with no financial hardship (parade schematics only)
GHOST = "#c9c9c4"
INK, MUTED = "#44443f", "#6b6b66"

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.edgecolor": "#c3c2b7", "axes.labelcolor": INK,
                     "xtick.color": INK, "ytick.color": INK, "axes.grid": True,
                     "grid.color": "#e6e5e0", "grid.linewidth": 0.6, "axes.axisbelow": True})

BOLD = dict(fontweight="bold", color=NAVY)
PLAIN = dict(color=INK)


def rich_line(ax, x, y, parts, fs=10.5, transform=None, ha="left", va="bottom", gap=0.0):
    """Draw [(text, props), ...] side by side (mixed bold/plain) starting at x (ha='left') or centred on x."""
    transform = transform or ax.transAxes
    fig = ax.figure; rend = fig.canvas.get_renderer()
    inv = transform.inverted()
    arts, cur = [], x
    for txt, props in parts:
        t = ax.text(cur, y, txt, transform=transform, fontsize=fs, ha="left", va=va, **props)
        bb = t.get_window_extent(renderer=rend)
        cur = inv.transform((bb.x1, bb.y0))[0] + gap
        arts.append(t)
    if ha == "center":
        shift = (cur - gap - x) / 2
        for t in arts:
            px, py = t.get_position(); t.set_position((px - shift, py))
    return arts


def param_parts(items):
    """[('P', '7/16→4/16'), ...] -> bold navy 'P:' followed by the plain value, separated by wide gaps."""
    parts = []
    for k, (lab, val) in enumerate(items):
        parts += [(("    " if k else "") + f"{lab}:", BOLD), (f" {val}", PLAIN)]
    return parts


# SPL poverty series: PIP global aggregate (see data/README.md). Default: the release cited by the 2025 GMR
# (2021 PPP, 30 Sep 2025), which gives its "43% -> 25%" and "25.1% in 2022". Other columns of the file:
# "2017ppp_20250930" (PPP vintage of the GMR financial-hardship series), "2021ppp_20260922", "2017ppp_20260922".
SPL_VINTAGE = "2021ppp_20250930"
VINTAGE_LABEL = {"2021ppp_20250930": "2021 PPP, September 2025 release cited in the 2025 GMR",
                 "2017ppp_20250930": "2017 PPP, September 2025 release",
                 "2021ppp_20260922": "2021 PPP, September 2026 release",
                 "2017ppp_20260922": "2017 PPP, September 2026 release"}

# ---------------------------------------------------------------- Figure 1
df = pd.read_csv(os.path.join(ROOT, "data", "gho_financial_hardship_global_2025def.csv"))
w = df.pivot(index="year", columns="component", values="share_pct")
spl = pd.read_csv(os.path.join(ROOT, "data", "pip_spl_poverty_global.csv")).set_index("year")
w["SPL"] = spl[f"spl_headcount_pct_{SPL_VINTAGE}"]

fig, ax = plt.subplots(figsize=(9, 4.6), dpi=200)
series = [("SPL", BLACK, "--", "Poverty headcount at the societal poverty line (PIP)"),
          ("TOTAL", PURPLE, "-", "Financial hardship (SDG 3.8.2, 2025 def.)"),
          ("IMPOV", DORANGE, "-", "Impoverishing OOP (further pushed + pushed)"),
          ("LARGE", ORANGE, "-", "Large, non-impoverishing OOP")]
nudge_end = {"SPL": -7, "TOTAL": 6}           # 2022 labels of SPL (25.1) and FH (26.0) would collide
for col, c, ls, lab in series:
    ax.plot(w.index, w[col], color=c, lw=3, ls=ls, label=lab, solid_capstyle="round")
    ax.scatter([w.index[0], w.index[-1]], [w[col].iloc[0], w[col].iloc[-1]], color=c, s=36, zorder=3,
               edgecolor="white", linewidth=1.2)
    ax.annotate(f"{w[col].iloc[-1]:.1f}%", (w.index[-1], w[col].iloc[-1]), xytext=(7, nudge_end.get(col, 0)),
                textcoords="offset points", va="center", color=INK, fontsize=10)
    ax.annotate(f"{w[col].iloc[0]:.1f}%", (w.index[0], w[col].iloc[0]), xytext=(-7, 0),
                textcoords="offset points", va="center", ha="right", color=INK, fontsize=10)
ax.set_xlim(1997.6, 2024.2); ax.set_ylim(0, 50)
ax.set_ylabel("Percent of world population"); ax.set_xlabel("")
ax.legend(frameon=False, loc="upper right", fontsize=9.5)
ax.set_title("Global financial hardship and SPL poverty, 2000–2022", loc="left", fontsize=12, color="#1a1a19")
fig.text(0.01, 0.01, "Sources: WHO & World Bank, Tracking UHC: 2025 Global Monitoring Report.\n"
         f"Poverty: World Bank Poverty and Inequality Platform, global headcount at the societal poverty line ({VINTAGE_LABEL[SPL_VINTAGE]}).",
         fontsize=7, color=MUTED)
fig.tight_layout(rect=(0, 0.05, 1, 1)); fig.savefig(os.path.join(OUT, "fig_global_trend.png")); plt.close(fig)

# ---------------------------------------------------------------- Figure 2
# Exact macro decomposition with the published 2025 GMR global figures: further impoverished F and pushed U
# (GMR Fig. 3.1 = WDI SH_UHC_FH40_FURTHER / _PUSHED) and SPL poverty P (PIP release cited by the GMR).
comp = pd.read_csv(os.path.join(ROOT, "data", "wdi_impoverishment_components_global.csv")).set_index("year")
Y0, Y1 = 2000, 2022


def gmr_decomp(vintage):
    p = spl[f"spl_headcount_pct_{vintage}"] / 100
    f, u = comp["further_impoverished_pct"] / 100, comp["pushed_pct"] / 100
    return decompose_macro(p[Y0], f[Y0], u[Y0], p[Y1], f[Y1], u[Y1])


def mns(v, fmt="+.1f"):
    return format(v, fmt).replace("-", "−")


d = gmr_decomp(SPL_VINTAGE)
I0, I1 = d.P0 * d.phi0 + (1 - d.P0) * d.psi0, d.P1 * d.phi1 + (1 - d.P1) * d.psi1
vals = [I0 * 100, d.poverty * 100, d.finprot_poor * 100, d.finprot_nonpoor * 100, I1 * 100]
names = ["Impoverishing\nOOP, 2000", "Poverty\nreduction", "Financial protection\namong the poor",
         "Financial protection\namong the non-poor", "Impoverishing\nOOP, 2022"]
params = [("I", f"{I0:.1%}"), ("P", f"{d.P0:.1%} → {d.P1:.1%}"), ("δ", f"{d.phi0:.1%} → {d.phi1:.1%}"),
          ("β", f"{d.psi0:.1%} → {d.psi1:.1%}"), ("I", f"{I1:.1%}")]
cols = [DORANGE, BLACK, NAVY, LBLUE, DORANGE]

fig, ax = plt.subplots(figsize=(9, 5.0), dpi=200)
cum = vals[0]
ax.bar(0, vals[0], color=DORANGE, width=0.56)
ax.text(0, vals[0] + 0.6, f"{vals[0]:.1f}", ha="center", color=INK, fontsize=12)
tops = {}
for k in (1, 2, 3):
    v = vals[k]; bottom = cum if v >= 0 else cum + v
    ax.bar(k, abs(v), bottom=bottom, color=cols[k], width=0.56)
    ax.text(k, max(cum, cum + v) + 0.6, mns(v), ha="center", color=INK, fontsize=12)
    ax.plot([k - 0.28, k + 0.28], [cum + v, cum + v], color=MUTED, lw=0.8)
    # direction arrow to the left of each bar
    ax.annotate("", xy=(k - 0.36, cum + v), xytext=(k - 0.36, cum),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.4, mutation_scale=12, shrinkA=0, shrinkB=0))
    tops[k] = (bottom, bottom + abs(v))
    cum += v
ax.bar(4, vals[4], color=DORANGE, width=0.56)
ax.text(4, vals[4] + 0.6, f"{vals[4]:.1f}", ha="center", color=INK, fontsize=12)
# shares of the change: poverty term alone, and the two protection terms together
share_pov = d.poverty / d.dI
share_fp = (d.finprot_poor + d.finprot_nonpoor) / d.dI
yb = tops[1][0] - 1.6
ax.text(1, yb, f"{share_pov:+.0%}".replace("-", "−") + "\nof the change", ha="center", va="top", fontsize=11.5,
        color=BLACK, fontweight="bold")
ybr = min(tops[2][0], tops[3][0]) - 1.2
ax.annotate("", xy=(1.72, ybr), xytext=(3.28, ybr),
            arrowprops=dict(arrowstyle="-", color=INK, lw=1.2, connectionstyle="bar,fraction=-0.08"))
ax.text(2.5, ybr - 2.9, f"{share_fp:+.0%}".replace("-", "−") + " of the change", ha="center", va="top",
        fontsize=11.5, color=NAVY, fontweight="bold")
ax.set_xticks(range(5)); ax.set_xticklabels(names, fontsize=9.5)
ax.tick_params(axis="x", pad=4)
trans = blended_transform_factory(ax.transData, ax.transAxes)
for k, (lab, val) in enumerate(params):
    rich_line(ax, k, -0.155, [(f"{lab}:", BOLD), (f" {val}", PLAIN)], fs=9.5, transform=trans, ha="center", va="top")
ax.set_ylabel("Percent of world population"); ax.set_ylim(0, 34)
ax.set_title("Exact decomposition of the 2000–2022 change in impoverishing OOP, 2025 GMR figures",
             loc="left", fontsize=12, color="#1a1a19")
fig.text(0.01, 0.01, f"Inputs, 2000 → 2022: further impoverished {comp.further_impoverished_pct[Y0]:.2f}% → {comp.further_impoverished_pct[Y1]:.2f}%, pushed "
         f"{comp.pushed_pct[Y0]:.2f}% → {comp.pushed_pct[Y1]:.2f}% (2025 GMR, Fig. 3.1); SPL poverty {d.P0:.2%} → {d.P1:.2%} (PIP, as cited in the GMR).\n"
         f"δ = further impoverished / P;  β = pushed / (1 − P). Black = poverty component; dark and light blue = financial-protection components. "
         "Components sum exactly to " + mns(d.dI * 100, ".2f") + " pp.",
         fontsize=7, color=MUTED)
fig.tight_layout(rect=(0, 0.06, 1, 1)); fig.savefig(os.path.join(OUT, "fig_decomp_illustration.png")); plt.close(fig)
for v in VINTAGE_LABEL:                                      # numbers quoted in the deck, and their sensitivity
    e = gmr_decomp(v)
    print(f"{v}: P {e.P0:.4f}->{e.P1:.4f} delta {e.phi0:.4f}->{e.phi1:.4f} psi {e.psi0:.4f}->{e.psi1:.4f} | "
          f"poverty {e.poverty * 100:+.2f} poor {e.finprot_poor * 100:+.2f} non-poor {e.finprot_nonpoor * 100:+.2f} "
          f"= {e.dI * 100:+.2f} pp (resid {e.residual:.1e}; poverty = {e.poverty / e.dI:.0%} of the change)")

# ---------------------------------------------------------------- Figure 3: Pen's parade schematics
# Sixteen individuals ranked by consumption gross of OOP; the S-shaped curve is the parade.
# OOP is a downward arrow from gross to net consumption, coloured by SDG 3.8.2 (2025) status:
# further pushed (poor, OOP > 0) / pushed (x - m < z) in dark orange, large non-impoverishing
# (m > 0.4 (x - z)) in orange, no financial hardship in green. Schematic: arrows are exaggerated.
NK = 16
R = (np.arange(NK) + 0.5) / NK
CY0, CY1, KS, R0 = 0.55, 3.6, 8.0, 0.66
curve = lambda r, g=1.0: g * (CY0 + CY1 / (1 + np.exp(-KS * (r - R0))))
P_BASE, P_GROW = 0.43, 0.25
Z = curve(P_BASE)                       # line crosses the 2000 parade at P = 43%
G_GROW = Z / curve(P_GROW)              # distribution-neutral growth that brings P to 25%
# OOP budget shares by rank (protection held fixed by rank across panels unless stated)
S_BASE = np.array([0.45, 0.42, 0.00, 0.40, 0.38, 0.00, 0.28,     # poor in 2000 (k = 0..6)
                   0.34, 0.00, 0.22, 0.06, 0.00, 0.16, 0.04, 0.00, 0.03])
CAT_COL = {"further": DORANGE, "pushed": DORANGE, "large": ORANGE, "none": GREEN}


def classify(x, m, z=Z):
    if m <= 0:
        return "nopay"
    if x < z:
        return "further"
    if x - m < z:
        return "pushed"
    return "large" if m > 0.4 * (x - z) else "none"


def stats(g, s, z=Z):
    x = curve(R, g); cats = [classify(xi, si * xi, z) for xi, si in zip(x, s)]
    poor = x < z
    F = sum(c == "further" for c in cats); U = sum(c == "pushed" for c in cats)
    return dict(n_poor=int(poor.sum()), F=F, U=U, P=poor.mean(), delta=F / max(poor.sum(), 1),
                psi=U / max((~poor).sum(), 1), I=(F + U) / NK, cats=cats, x=x)


def parade_axes(ax, ymax=3.0):
    ax.grid(False); ax.set_xlim(0, 1.04); ax.set_ylim(0, ymax)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color(INK); ax.spines[sp].set_linewidth(1.2)
    ax.plot(1, 0, ">", color=INK, transform=ax.get_yaxis_transform(), clip_on=False, ms=6)
    ax.plot(0, 1, "^", color=INK, transform=ax.get_xaxis_transform(), clip_on=False, ms=6)


def draw_parade(ax, g, s, z=Z, ghost_g=None, ghost_s=None, highlight=(), fs=11, ymax=3.0,
                bracket=True, line_label=True):
    parade_axes(ax, ymax)
    rr = np.linspace(0, 1, 400)
    if ghost_g is not None:                                   # previous parade, for reference
        ax.plot(rr, curve(rr, ghost_g), color=GHOST, lw=2.2, zorder=1)
    ax.plot(rr, curve(rr, g), color=NAVY, lw=2.6, zorder=2)
    ax.axhline(z, color=BLACK, lw=1.3, ls="--", zorder=1)
    if line_label:
        ax.text(1.03, z + 0.06, "Poverty line $z$", ha="right", va="bottom", fontsize=fs - 1, color=INK)
    st = stats(g, s, z)
    shift = np.zeros(NK); ghost_mid = {}
    if ghost_s is not None:                                   # removed / shortened arrows, drawn alongside
        for k, (r, x, s_old, s_new) in enumerate(zip(R, st["x"], ghost_s, s)):
            if s_old > s_new:
                off = 0.016 if s_new > 0 else 0.0
                shift[k] = off
                ax.annotate("", xy=(r - off, x - s_old * x), xytext=(r - off, x),
                            arrowprops=dict(arrowstyle="-|>", color=GHOST, lw=2.0, shrinkA=0, shrinkB=0,
                                            mutation_scale=11), zorder=2)
                ghost_mid[k] = (r - off, x - 0.6 * s_old * x)
    for k, (r, x, c) in enumerate(zip(R, st["x"], st["cats"])):
        if c != "nopay":
            ax.annotate("", xy=(r + shift[k], x - s[k] * x), xytext=(r + shift[k], x),
                        arrowprops=dict(arrowstyle="-|>", color=CAT_COL[c], lw=2.4, shrinkA=0, shrinkB=0,
                                        mutation_scale=12), zorder=4)
        ax.plot(r, x, "o", ms=5.5, color=NAVY if x >= z else "white", mec=NAVY, mew=1.4, zorder=5)
        if k in highlight:
            ax.plot(r, x - 0.5 * s[k] * x, "o", ms=22, mfc="none", mec=DORANGE, mew=1.6, zorder=6)
    P = st["P"]
    ax.plot([P, P], [0, z], color=INK, lw=1, ls=":", zorder=1)
    if bracket:
        yb = 0.16
        ax.annotate("", xy=(0, yb), xytext=(P, yb), arrowprops=dict(arrowstyle="<->", color=INK, lw=1))
        ax.annotate("", xy=(P, yb), xytext=(1.0, yb), arrowprops=dict(arrowstyle="<->", color=INK, lw=1))
        ax.text(P / 2, yb + 0.05, "Poor: $P_t$", ha="center", va="bottom", fontsize=fs - 1, color=INK)
        ax.text((P + 1) / 2, yb + 0.05, "Non-poor: $1-P_t$", ha="center", va="bottom", fontsize=fs - 1, color=INK)
    st["ghost_mid"] = ghost_mid
    return st


def box(ax, xy, xytext, text, color, fs=10, ha="left"):
    ax.annotate(text, xy=xy, xytext=xytext, fontsize=fs, color=INK, ha=ha, va="center",
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=color, lw=1.3),
                arrowprops=dict(arrowstyle="-", color=color, lw=1.1, shrinkA=0, shrinkB=2), zorder=7)


def save(fig, name):
    fig.savefig(os.path.join(OUT, name)); plt.close(fig)


def change_items(a, b):
    f = lambda st: dict(P=f"{st['n_poor']}/{NK}", d=f"{st['F']}/{st['n_poor']}",
                        s=f"{st['U']}/{NK - st['n_poor']}", I=f"{st['F'] + st['U']}/{NK}")
    a, b = f(a), f(b)
    return [("P", f"{a['P']}→{b['P']}"), ("δ", f"{a['d']}→{b['d']}"), ("β", f"{a['s']}→{b['s']}"),
            ("I", f"{a['I']}→{b['I']}")]


def panel(ax, title, a=None, b=None):
    """Title, and (if a, b given) a one-line before -> after summary with bold navy parameter labels."""
    ax.set_title(title, loc="left", fontsize=12.5, color="#1a1a19", pad=24 if a is not None else 8)
    if a is not None:
        rich_line(ax, 0, 1.035, param_parts(change_items(a, b)), fs=10.5)


def axis_label(ax, x, text, color=INK, fs=12):
    """Label under the horizontal axis at rank x (P_t, P_{t-1})."""
    ax.text(x, -0.05, text, transform=blended_transform_factory(ax.transData, ax.transAxes),
            ha="center", va="top", fontsize=fs, color=color, clip_on=False)


# --- 3a. Components of I_t = P_t delta_t + (1 - P_t) psi_t (slide "Poverty and health impoverishment")
fig, ax = plt.subplots(figsize=(5.9, 4.7), dpi=200)
st0 = draw_parade(ax, 1.0, S_BASE, fs=11, ymax=3.3)
x0 = st0["x"]
mid = lambda k: (R[k], x0[k] - 0.5 * S_BASE[k] * x0[k])
box(ax, mid(3), (0.05, 1.55), "Further pushed:\npoor with OOP > 0", DORANGE)
ax.annotate("", xy=mid(1), xytext=(0.12, 1.36), arrowprops=dict(arrowstyle="-", color=DORANGE, lw=1.1))
box(ax, (R[5], x0[5] + 0.03), (0.37, 2.42), "Poor, no OOP", INK)      # right of the further-pushed box
box(ax, mid(7), (0.53, 0.66), "Pushed: $x-m<z$", DORANGE)             # clear of the non-poor bracket
box(ax, mid(9), (0.72, 1.62), "Large, not\nimpoverishing", ORANGE)
box(ax, mid(12), (0.84, 2.15), "No financial\nhardship", GREEN)
ax.text(0.02, 3.22, f"$\\delta_t$ = share of the poor with OOP = {st0['F']}/{st0['n_poor']}\n"
        f"$\\beta_t$ = share of the non-poor pushed = {st0['U']}/{NK - st0['n_poor']}\n"
        f"$I_t$ = {st0['n_poor']}/{NK}·{st0['F']}/{st0['n_poor']} + {NK - st0['n_poor']}/{NK}·{st0['U']}/{NK - st0['n_poor']}"
        f" = {st0['F'] + st0['U']}/{NK}", va="top", fontsize=10.5, color=INK, linespacing=1.5)
ax.set_xlabel("Cumulative % of population, ranked by consumption gross of OOP", fontsize=10)
ax.set_ylabel("Consumption (gross of OOP)", fontsize=10)
fig.tight_layout(); save(fig, "fig_parade_components.png")

# --- 3b. Story A (poverty falls, protection unchanged by rank) and Story B (poverty unchanged,
#         protection improves): both bring I from 6/16 to the same lower level.
S_B = S_BASE.copy()
S_B[3] = 0.0                             # one poor payer no longer pays (exemption, prepayment)
S_B[[0, 1, 4]] = 0.30; S_B[6] = 0.20     # the others pay less (still counted: any OOP > 0)
S_B[7] = 0.10                            # OOP of the near-poor falls: no longer pushed
stA, stB = stats(G_GROW, S_BASE), stats(1.0, S_B)
print("parade baseline:", {k: v for k, v in st0.items() if k not in ("cats", "x")})
print("parade story A :", {k: v for k, v in stA.items() if k not in ("cats", "x")})
print("parade story B :", {k: v for k, v in stB.items() if k not in ("cats", "x")})


def r_at(y, g):
    rr = np.linspace(0, 1, 2001); return rr[np.argmin(np.abs(curve(rr, g) - y))]


# Story A (slide "Interpretation"): parade c_{t-1} -> c_t, P_{t-1} -> P_t
fig, ax = plt.subplots(figsize=(5.6, 3.6), dpi=200)
st = draw_parade(ax, G_GROW, S_BASE, ghost_g=1.0, fs=11, ymax=3.6)
panel(ax, "Parade shifts up; same OOP shares by rank")
ax.plot([P_BASE, P_BASE], [0, Z], color=GHOST, lw=1.4, ls=":", zorder=1)
ya = 3.3
ra_new, ra_old = r_at(ya, G_GROW), r_at(ya, 1.0)
ax.text(ra_new - 0.03, ya + 0.02, "$c_t$", ha="right", va="center", fontsize=13, color=NAVY)
ax.text(ra_old + 0.03, ya + 0.02, "$c_{t-1}$", ha="left", va="center", fontsize=13, color=MUTED)
ax.annotate("", xy=(ra_new + 0.025, ya - 0.1), xytext=(ra_old - 0.01, ya - 0.1),
            arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.6, mutation_scale=13))
ax.text(0.80, 1.85, "grey = parade before", fontsize=10, color=MUTED, ha="center")
axis_label(ax, st["P"], "$P_t$")
axis_label(ax, P_BASE, "$P_{t-1}$", color=MUTED)
fig.tight_layout(); save(fig, "fig_parade_storyA.png")

# Story B (slide "Interpretation"): same parade, OOP_{t-1} in grey
fig, ax = plt.subplots(figsize=(5.6, 3.6), dpi=200)
st = draw_parade(ax, 1.0, S_B, ghost_s=S_BASE, fs=11, ymax=3.6)
panel(ax, "Same parade; fewer and smaller OOP payments")
lab = (0.30, 2.05)
ax.text(*lab, "OOP$_{t-1}$", ha="center", va="bottom", fontsize=12, color=MUTED)
for (gx, gy) in st["ghost_mid"].values():
    ax.annotate("", xy=(gx, gy), xytext=(lab[0], lab[1] - 0.02),
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8, shrinkA=0, shrinkB=1))
ax.text(0.60, 0.62, "grey = OOP before", fontsize=10.5, color=MUTED)
axis_label(ax, st["P"], "$P_t$")
fig.tight_layout(); save(fig, "fig_parade_storyB.png")

# --- 3c. Combined effects (slide "Combined effects"): mechanical poverty effect, then increased access
S_ACC = S_BASE.copy()
S_ACC[2] = 0.25                          # a poor non-user starts using care and pays a little
stAcc = stats(G_GROW, S_ACC)
print("parade access  :", {k: v for k, v in stAcc.items() if k not in ("cats", "x")})
fig, ax = plt.subplots(figsize=(5.6, 3.4), dpi=200)
draw_parade(ax, G_GROW, S_BASE, ghost_g=1.0, fs=11, ymax=3.6)
panel(ax, "Parade shifts up; same OOP shares by rank", st0, stA)
ax.plot([P_BASE, P_BASE], [0, Z], color=GHOST, lw=1.4, ls=":", zorder=1)
ax.text(0.80, 1.85, "grey = parade before", fontsize=10, color=MUTED, ha="center")
fig.tight_layout(); save(fig, "fig_parade_mechanical.png")

fig, ax = plt.subplots(figsize=(5.6, 3.4), dpi=200)
draw_parade(ax, G_GROW, S_ACC, highlight=(2,), fs=11, ymax=3.6)
panel(ax, "Same parade; a poor non-user now pays", stA, stAcc)
fig.tight_layout(); save(fig, "fig_parade_access_effect.png")

print("figures written to", OUT)
