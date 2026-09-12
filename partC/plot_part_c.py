import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

# ============================================================
# FONT / STYLE
# ============================================================

plt.rcParams.update({
    'font.size': 11,
    'font.family': 'sans-serif',
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 10,
    'figure.titlesize': 14
})

# ============================================================
# COLOR PALETTE
# ============================================================

SRAM_COLOR = '#1F4E79'       # Dark blue
STT_COLOR = '#E67E22'        # Orange
STT_IMPROVED = '#2E8B57'     # Green
TMR_COLOR = '#7B4FA3'        # Purple
TMR_HIGH = '#C0392B'         # Dark red

MACRO_COLOR = '#2874A6'      # Medium blue
DATA_COLOR = '#76B7C5'       # Light blue

GRID_COLOR = '#B0B0B0'

# ============================================================
# FIGURE
# ============================================================

fig, axes = plt.subplots(
    1, 3,
    figsize=(16, 5),
    constrained_layout=True
)

# ============================================================
# 1. SRAM vs STT-MRAM
# ============================================================

categories = [
    'Read Latency\n(ns)',
    'Write Latency\n(ns)',
    'Read Energy\n(nJ)',
    'Write Energy\n(nJ)',
    'Leakage\n(W)',
    'Total Area\n(mm²)'
]

sram_vals = [
    2.902,
    2.652,
    0.793,
    0.793,
    2.251,
    11.474
]

stt_t1_vals = [
    1.589,
    10.608,
    0.760,
    0.531,
    0.425,
    3.590
]

stt_t4b_vals = [
    1.517,
    10.717,
    0.646,
    0.323,
    0.313,
    2.209
]

x = np.arange(len(categories))
width = 0.25

# SRAM
axes[0].bar(
    x - width,
    [v/s for v, s in zip(sram_vals, sram_vals)],
    width,
    label='6T SRAM (Baseline)',
    color=SRAM_COLOR,
    edgecolor='black',
    linewidth=0.8
)

# STT-MRAM baseline
axes[0].bar(
    x,
    [v/s for v, s in zip(stt_t1_vals, sram_vals)],
    width,
    label='STT-MRAM (200µA, 54F²)',
    color=STT_COLOR,
    edgecolor='black',
    linewidth=0.8
)

# STT-MRAM improved
axes[0].bar(
    x + width,
    [v/s for v, s in zip(stt_t4b_vals, sram_vals)],
    width,
    label='STT-MRAM (100µA, 36F²)',
    color=STT_IMPROVED,
    edgecolor='black',
    linewidth=0.8
)

axes[0].axhline(
    1.0,
    color='#555555',
    linestyle='--',
    linewidth=1.2
)

axes[0].set_ylabel('Normalized to SRAM Baseline')
axes[0].set_title(
    '(a) SRAM vs STT-MRAM Metrics (Relative)',
    pad=10
)

axes[0].set_xticks(x)
axes[0].set_xticklabels(categories)

axes[0].set_yscale('log')
axes[0].set_ylim(0.05, 10.0)

axes[0].grid(
    axis='y',
    linestyle=':',
    color=GRID_COLOR,
    alpha=0.7
)

axes[0].legend(
    loc='upper right',
    framealpha=0.95
)

# ============================================================
# 2. TASK 4 - AREA IMPACT
# ============================================================

configs = [
    '6T SRAM\n(146 F²)',
    'STT Baseline\n(200µA, 6F, 54F²)',
    'STT Case A\n(100µA unscaled)',
    'STT Case B\n(100µA, 3F, 36F²)'
]

macro_area = [
    11.474,
    3.590,
    3.590,
    2.209
]

data_area = [
    10.271,
    3.142,
    3.142,
    1.946
]

x_cfg = np.arange(len(configs))
w_cfg = 0.35

# Total macro area
axes[1].bar(
    x_cfg - w_cfg/2,
    macro_area,
    w_cfg,
    label='Total Macro Area',
    color=MACRO_COLOR,
    edgecolor='black',
    linewidth=0.8
)

# Data array area
axes[1].bar(
    x_cfg + w_cfg/2,
    data_area,
    w_cfg,
    label='Data Array Area',
    color=DATA_COLOR,
    edgecolor='black',
    linewidth=0.8
)

# Value labels
for i, (m, d) in enumerate(zip(macro_area, data_area)):

    axes[1].text(
        i - w_cfg/2,
        m + 0.25,
        f"{m:.2f}",
        ha='center',
        va='bottom',
        fontsize=9,
        fontweight='bold'
    )

    axes[1].text(
        i + w_cfg/2,
        d + 0.25,
        f"{d:.2f}",
        ha='center',
        va='bottom',
        fontsize=9
    )

axes[1].set_ylabel('Area (mm²)')

axes[1].set_title(
    '(b) Task 4: Area Impact of Write Current Sizing',
    pad=10
)

axes[1].set_xticks(x_cfg)
axes[1].set_xticklabels(
    configs,
    rotation=15,
    ha='right'
)

axes[1].set_ylim(0, 13.5)

axes[1].grid(
    axis='y',
    linestyle=':',
    color=GRID_COLOR,
    alpha=0.7
)

axes[1].legend(
    loc='upper right',
    framealpha=0.95
)

# ============================================================
# 3. TASK 3 - TMR
# ============================================================

metrics_tmr = [
    'Read Latency\n(ns)',
    'Write Latency\n(ns)',
    'Read Energy\n(nJ)',
    'Write Energy\n(nJ)',
    'Macro Area\n(mm²)',
    'ΔV_sense\n(mV)'
]

t1_tmr = [
    1.589,
    10.608,
    0.760,
    0.531,
    3.590,
    60.0
]

t3_tmr = [
    1.594,
    10.657,
    0.758,
    0.529,
    3.580,
    160.0
]

x_tmr = np.arange(len(metrics_tmr))
w_tmr = 0.32

norm_t1 = [1.0] * 6

norm_t3 = [
    t3/t1
    for t3, t1 in zip(t3_tmr, t1_tmr)
]

# TMR baseline
axes[2].bar(
    x_tmr - w_tmr/2,
    norm_t1,
    w_tmr,
    label='TMR 100% (3kΩ / 6kΩ)',
    color=TMR_COLOR,
    edgecolor='black',
    linewidth=0.8
)

# TMR improved
axes[2].bar(
    x_tmr + w_tmr/2,
    norm_t3,
    w_tmr,
    label='TMR 200% (4kΩ / 12kΩ)',
    color=TMR_HIGH,
    edgecolor='black',
    linewidth=0.8
)

# Value labels
for i, n in enumerate(norm_t3):

    label_color = TMR_HIGH if n > 1.5 else '#222222'

    axes[2].text(
        i + w_tmr/2,
        n + 0.05,
        f"{n:.2f}×",
        ha='center',
        va='bottom',
        fontsize=9,
        fontweight='bold',
        color=label_color
    )

axes[2].axhline(
    1.0,
    color='#555555',
    linestyle='--',
    linewidth=1.2
)

axes[2].set_ylabel(
    'Ratio (TMR 200% / TMR 100%)'
)

axes[2].set_title(
    '(c) Task 3: What TMR 200% Actually Changes',
    pad=10
)

axes[2].set_xticks(x_tmr)

axes[2].set_xticklabels(
    metrics_tmr,
    rotation=20,
    ha='right'
)

axes[2].set_ylim(0, 3.0)

axes[2].grid(
    axis='y',
    linestyle=':',
    color=GRID_COLOR,
    alpha=0.7
)

axes[2].legend(
    loc='upper left',
    framealpha=0.95
)

# ============================================================
# SAVE
# ============================================================

out_dir = os.path.dirname(os.path.abspath(__file__))

out_svg = os.path.join(
    out_dir,
    "part_c_metrics.svg"
)

out_png = os.path.join(
    out_dir,
    "part_c_metrics.png"
)

plt.savefig(
    out_svg,
    format='svg',
    bbox_inches='tight'
)

plt.savefig(
    out_png,
    format='png',
    dpi=300,
    bbox_inches='tight'
)

plt.close()

print(f"Saved SVG: {out_svg}")
print(f"Saved PNG: {out_png}")