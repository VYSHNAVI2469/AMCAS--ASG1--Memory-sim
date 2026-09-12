import subprocess
import os
import re
import sys

# ============================================================
# AMCAS TASK 3
#
# Baseline:
#   Ron  = 3 kOhm
#   Roff = 6 kOhm
#
# Modified:
#   Ron  = 4 kOhm
#   Roff = 12 kOhm
#
# TMR:
#   Baseline  = 2:1
#   Modified  = 3:1
# ============================================================

SIM_DIR = "/mnt/c/Users/lenovo/Downloads/AMCS/Memsim-stack/tools/NVSim"

NV_EXE = os.path.join(SIM_DIR, "nvsim")

BASE_CELL = os.path.join(SIM_DIR, "sample_STTRAM.cell")
BASE_CFG = os.path.join(SIM_DIR, "STT_cache.cfg")

TASK3_CELL = os.path.join(SIM_DIR, "task3_tmr.cell")
TASK3_CFG = os.path.join(SIM_DIR, "STT_cache_tmr.cfg")

BASE_OUT = os.path.join(SIM_DIR, "task3_baseline.out")
TMR_OUT = os.path.join(SIM_DIR, "task3_tmr.out")


# ============================================================
# Check files
# ============================================================

for filename in [NV_EXE, BASE_CELL, BASE_CFG]:

    if not os.path.isfile(filename):

        print("ERROR: File not found:")
        print(filename)

        sys.exit(1)


# ============================================================
# Create modified STT-MRAM cell
# ============================================================

print("=" * 70)
print("TASK 3 - TMR SWEEP")
print("=" * 70)

print("\nCreating modified STT-MRAM cell...")
print("R_on  = 4 kOhm")
print("R_off = 12 kOhm")

with open(BASE_CELL, "r") as f:
    lines = f.readlines()


new_lines = []

for line in lines:

    stripped = line.strip()

    if stripped.startswith("-ResistanceOn"):
        new_lines.append(
            "-ResistanceOn (ohm): 4000\n"
        )

    elif stripped.startswith("-ResistanceOff"):
        new_lines.append(
            "-ResistanceOff (ohm): 12000\n"
        )

    else:
        new_lines.append(line)


with open(TASK3_CELL, "w") as f:
    f.writelines(new_lines)


print("\nCreated:")
print(TASK3_CELL)


# ============================================================
# Create modified configuration
# ============================================================

with open(BASE_CFG, "r") as f:
    cfg_lines = f.readlines()


new_cfg = []

for line in cfg_lines:

    if line.strip().startswith("-MemoryCellInputFile:"):

        new_cfg.append(
            "-MemoryCellInputFile: task3_tmr.cell\n"
        )

    else:

        new_cfg.append(line)


with open(TASK3_CFG, "w") as f:
    f.writelines(new_cfg)


print("Created:")
print(TASK3_CFG)


# ============================================================
# NVSim runner
# ============================================================

def run_nvsim(config, output_file):

    print("\nRunning:")
    print(config)

    p = subprocess.run(
        [NV_EXE, config],
        cwd=SIM_DIR,
        capture_output=True,
        text=True
    )

    with open(output_file, "w") as f:

        f.write(p.stdout)

        if p.stderr:

            f.write("\n\nSTDERR:\n")
            f.write(p.stderr)


    if p.returncode != 0:

        print("\nNVSim ERROR:")
        print(p.stderr)

        sys.exit(1)


    return p.stdout


# ============================================================
# Extract metrics
# ============================================================

def extract_metrics(output):

    def get(pattern, name):

        m = re.search(
            pattern,
            output,
            re.MULTILINE
        )

        if not m:

            print(
                f"WARNING: Could not find {name}"
            )

            return None

        return float(m.group(1))


    return {

        "read_latency":
            get(
                r"Cache Hit Latency\s+=\s+([0-9.]+)ns",
                "read latency"
            ),

        "write_latency":
            get(
                r"Cache Write Latency\s+=\s+([0-9.]+)ns",
                "write latency"
            ),

        "read_energy":
            get(
                r"Cache Hit Dynamic Energy\s+=\s+([0-9.]+)nJ",
                "read energy"
            ),

        "write_energy":
            get(
                r"Cache Write Dynamic Energy\s+=\s+([0-9.]+)nJ",
                "write energy"
            ),

        "leakage":
            get(
                r"Cache Total Leakage Power\s+=\s+([0-9.]+)mW",
                "leakage"
            ),

        "area":
            get(
                r" - Total Area\s+=\s+([0-9.]+)mm\^2",
                "area"
            )
    }


# ============================================================
# Run BASELINE
# ============================================================

print("\n")
print("=" * 70)
print("CASE 1: BASELINE")
print("=" * 70)

print("""
R_on  = 3 kOhm
R_off = 6 kOhm

TMR ratio = R_off / R_on = 6 / 3 = 2
""")

baseline_output = run_nvsim(
    BASE_CFG,
    BASE_OUT
)

baseline = extract_metrics(
    baseline_output
)


# ============================================================
# Run MODIFIED TMR
# ============================================================

print("\n")
print("=" * 70)
print("CASE 2: HIGH-TMR DEVICE")
print("=" * 70)

print("""
R_on  = 4 kOhm
R_off = 12 kOhm

TMR ratio = R_off / R_on = 12 / 4 = 3
""")

tmr_output = run_nvsim(
    TASK3_CFG,
    TMR_OUT
)

tmr = extract_metrics(
    tmr_output
)


# ============================================================
# Print comparison
# ============================================================

metric_names = {

    "read_latency":
        "Read Latency",

    "write_latency":
        "Write Latency",

    "read_energy":
        "Read Energy",

    "write_energy":
        "Write Energy",

    "leakage":
        "Leakage",

    "area":
        "Area"
}


units = {

    "read_latency": "ns",

    "write_latency": "ns",

    "read_energy": "nJ",

    "write_energy": "nJ",

    "leakage": "mW",

    "area": "mm2"
}


print("\n")
print("=" * 70)
print("TASK 3 RESULTS")
print("=" * 70)

print(
    f"{'Metric':<22}"
    f"{'Baseline':>15}"
    f"{'High TMR':>15}"
    f"{'Change':>15}"
)

print("-" * 70)


changes = {}


for key in metric_names:

    b = baseline[key]
    h = tmr[key]

    if b is None or h is None:
        continue

    absolute_change = h - b

    percent_change = (
        absolute_change / b
    ) * 100.0

    changes[key] = percent_change

    print(
        f"{metric_names[key]:<22}"
        f"{b:>12.3f} "
        f"{h:>12.3f} "
        f"{percent_change:>+10.2f}%"
    )


# ============================================================
# Find metric that moved most
# ============================================================

largest_metric = max(
    changes,
    key=lambda x: abs(changes[x])
)

largest_change = changes[largest_metric]


print("\n")
print("=" * 70)
print("METRIC THAT MOVED MOST")
print("=" * 70)

print(
    f"{metric_names[largest_metric]}"
)
print(
    f"Change = {largest_change:+.2f}%"
)


# ============================================================
# Device-level explanation
# ============================================================

print("\n")
print("=" * 70)
print("DEVICE-LEVEL EXPLANATION")
print("=" * 70)

print("""
BASELINE DEVICE

R_on  = 3 kOhm
R_off = 6 kOhm

TMR ratio:

    TMR = R_off / R_on
        = 6 / 3
        = 2

The two MTJ resistance states are therefore separated
by a factor of 2.


HIGH-TMR DEVICE

R_on  = 4 kOhm
R_off = 12 kOhm

TMR ratio:

    TMR = 12 / 4
        = 3

The resistance-state separation is now 3:1.


WHY TMR MATTERS

The sense amplifier does not directly observe an abstract
"TMR percentage." It observes electrical quantities such
as MTJ resistance, read current and bitline voltage/current.

Increasing the separation between the resistance states
increases the sensing margin between logic-0 and logic-1.

That can make the two states easier to distinguish in the
presence of circuit noise, process variation and sense-
amplifier offset.


IMPORTANT ARRAY-LEVEL POINT

A high TMR value reported in a device paper does NOT mean
that the complete memory array automatically becomes that
many times faster, smaller or lower-energy.

The device-level TMR primarily improves the electrical
contrast available to the sensing circuit.

At array level, the result is filtered through:

    MTJ resistance
        |
        v
    Read current
        |
        v
    Bitline voltage/current
        |
        v
    Sense-amplifier margin
        |
        v
    Read latency / read energy / yield


WHY THE OTHER METRICS MAY MOVE LITTLE

Changing R_on and R_off does not change:

    - MTJ physical cell area
    - CMOS access-transistor dimensions
    - write pulse duration
    - SET/RESET current
    - number of cells
    - cache capacity
    - array organization

Therefore area normally remains approximately unchanged.

Similarly, write behavior is primarily controlled by
the switching current and write pulse parameters, so a
change in read resistance can have much less effect on
write latency and write energy.

The strongest effect should therefore appear in a
read-related metric, especially the metric dominated by
MTJ sensing.
""")


# ============================================================
# Final assignment statement
# ============================================================

print("\n")
print("=" * 70)
print("TASK 3 ASSIGNMENT CONCLUSION")
print("=" * 70)

print(f"""
The MTJ TMR ratio was increased from 2:1 to 3:1 by changing
R_on from 3 kOhm to 4 kOhm and R_off from 6 kOhm to 12 kOhm.

The metric that moved the most in the NVSim array simulation
was:

    {metric_names[largest_metric]}
    
with a change of:

    {largest_change:+.2f}%

The device-level benefit of higher TMR is increased
resistance-state contrast, which improves the electrical
sensing margin available to the sense amplifier.

However, the device-paper TMR headline does not translate
directly into the same percentage improvement in complete
memory-array performance. Array-level performance is also
limited by bitline capacitance, sense-amplifier offset,
decoder delay, peripheral circuits, wiring, variation and
the MTJ read current.
""")


print("\n")
print("Complete outputs:")
print(BASE_OUT)
print(TMR_OUT)