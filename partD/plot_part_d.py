import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Styling
plt.rcParams.update({
    'font.size': 11,
    'font.family': 'sans-serif',
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'xtick.labelsize': 10,
    'ytick.labelsize': 11,
    'legend.fontsize': 10,
    'figure.titlesize': 15
})

fig, axes = plt.subplots(2, 2, figsize=(14, 10), constrained_layout=True)

# 1. Subplot (a): Memory Execution Cycles across Tasks 1, 2, 3, 4
tasks = ['Task 1\n(FRFCFS, 1Ch)', 'Task 2\n(FCFS, 1Ch)', 'Task 3\n(Row < Bank)', 'Task 4\n(2 Channels)']
cycles = [63846, 70161, 118446, 36966]
colors = ['#4C72B0', '#DD8452', '#C44E52', '#55A868']

bars1 = axes[0, 0].bar(tasks, cycles, color=colors, edgecolor='black', width=0.55)
for bar, c in zip(bars1, cycles):
    axes[0, 0].text(bar.get_x() + bar.get_width()/2, c + 2000, f"{c:,}", ha='center', va='bottom', fontweight='bold', fontsize=10)

axes[0, 0].set_ylabel('Total Memory Controller Cycles')
axes[0, 0].set_title('(a) Memory Execution Cycles Across Configurations', pad=10)
axes[0, 0].set_ylim(0, 135000)
axes[0, 0].grid(axis='y', linestyle=':', alpha=0.6)

# 2. Subplot (b): Average Read Latency across Tasks 1, 2, 3, 4
latencies = [78.19, 88.32, 165.56, 35.13]
bars2 = axes[0, 1].bar(tasks, latencies, color=colors, edgecolor='black', width=0.55)
for bar, l in zip(bars2, latencies):
    axes[0, 1].text(bar.get_x() + bar.get_width()/2, l + 3, f"{l:.1f} cyc", ha='center', va='bottom', fontweight='bold', fontsize=10)

axes[0, 1].axhline(22.0, color='gray', linestyle='--', linewidth=1, label='Physical tCL floor (22 cyc)')
axes[0, 1].set_ylabel('Average Read Latency (DRAM Cycles)')
axes[0, 1].set_title('(b) Average Read Latency Across Configurations', pad=10)
axes[0, 1].set_ylim(0, 190)
axes[0, 1].grid(axis='y', linestyle=':', alpha=0.6)
axes[0, 1].legend(loc='upper right')

# 3. Subplot (c): Task 2 - Row Buffer Hit Rate Collapse & Latency Explosion
scheds = ['FRFCFS\n(Out-of-Order)', 'FCFS\n(Strict In-Order)']
hit_rates = [93.75, 0.00]
avg_lats = [145.27, 1096.27]

x = np.arange(len(scheds))
width = 0.35

ax_hr = axes[1, 0]
ax_lat = ax_hr.twinx()

rects_hr = ax_hr.bar(x - width/2, hit_rates, width, label='Row Hit Rate (%)', color='#4C72B0', edgecolor='black')
rects_lat = ax_lat.bar(x + width/2, avg_lats, width, label='Avg Read Latency (cyc)', color='#C44E52', edgecolor='black')

ax_hr.set_ylabel('Row-Buffer Hit Rate (%)', color='#4C72B0')
ax_lat.set_ylabel('Average Read Latency (Cycles)', color='#C44E52')
ax_hr.set_title('(c) Task 2: Scheduler Row-Buffer Thrashing Collapse', pad=10)
ax_hr.set_xticks(x)
ax_hr.set_xticklabels(scheds)
ax_hr.set_ylim(0, 110)
ax_lat.set_ylim(0, 1300)
ax_hr.grid(axis='y', linestyle=':', alpha=0.6)

for b, h in zip(rects_hr, hit_rates):
    ax_hr.text(b.get_x() + b.get_width()/2, h + 2, f"{h:.1f}%", ha='center', va='bottom', fontweight='bold', color='#4C72B0')
for b, l in zip(rects_lat, avg_lats):
    ax_lat.text(b.get_x() + b.get_width()/2, l + 25, f"{l:.1f} cyc", ha='center', va='bottom', fontweight='bold', color='#C44E52')

# 4. Subplot (d): Task 3 - Loss of Bank-Level Parallelism (BLP)
mappings = ['RoBaRaCoCh\n(Row Above Bank)', 'ChRaBaRoCo\n(Row Below Bank)']
conflicts = [69, 614]
cyc_map = [63846, 118446]

x_m = np.arange(len(mappings))
ax_conf = axes[1, 1]
ax_cyc = ax_conf.twinx()

rects_conf = ax_conf.bar(x_m - width/2, conflicts, width, label='Row Conflicts', color='#DD8452', edgecolor='black')
rects_cyc = ax_cyc.bar(x_m + width/2, cyc_map, width, label='Memory Cycles', color='#8172B3', edgecolor='black')

ax_conf.set_ylabel('Total Row Conflicts', color='#DD8452')
ax_cyc.set_ylabel('Total Memory Cycles', color='#8172B3')
ax_conf.set_title('(d) Task 3: Address Mapping & Loss of Bank-Level Parallelism', pad=10)
ax_conf.set_xticks(x_m)
ax_conf.set_xticklabels(mappings)
ax_conf.set_ylim(0, 750)
ax_cyc.set_ylim(0, 140000)
ax_conf.grid(axis='y', linestyle=':', alpha=0.6)

for b, c in zip(rects_conf, conflicts):
    ax_conf.text(b.get_x() + b.get_width()/2, c + 15, f"{c}", ha='center', va='bottom', fontweight='bold', color='#DD8452')
for b, c in zip(rects_cyc, cyc_map):
    ax_cyc.text(b.get_x() + b.get_width()/2, c + 2500, f"{c:,}", ha='center', va='bottom', fontweight='bold', color='#8172B3')

out_dir = os.path.dirname(os.path.abspath(__file__))
out_svg = os.path.join(out_dir, "part_d_metrics.svg")
out_png = os.path.join(out_dir, "part_d_metrics.png")
plt.savefig(out_svg, format='svg')
plt.savefig(out_png, format='png', dpi=300)
print(f"Saved plots to {out_svg} and {out_png}")
