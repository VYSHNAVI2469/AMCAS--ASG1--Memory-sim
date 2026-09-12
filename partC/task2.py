import subprocess
import os
import re
import sys

# ============================================================
# AMCAS TASK 2
# STT-MRAM vs CACTI SRAM
# ============================================================

NV_DIR = "/mnt/c/Users/lenovo/Downloads/AMCS/Memsim-stack/tools/NVSim"
CACTI_DIR = "/mnt/c/Users/lenovo/Downloads/AMCS/Memsim-stack/tools/cacti"

NV_EXE = os.path.join(NV_DIR, "nvsim")
NV_CFG = os.path.join(NV_DIR, "STT_cache.cfg")

CACTI_EXE = os.path.join(CACTI_DIR, "cacti")
CACTI_CFG = os.path.join(CACTI_DIR, "cache.cfg")

NV_OUT = os.path.join(NV_DIR, "task2_nvsim.out")
CACTI_OUT = os.path.join(NV_DIR, "task2_cacti.out")


# ============================================================
# Check files
# ============================================================

for filename in [NV_EXE, NV_CFG, CACTI_EXE, CACTI_CFG]:
    if not os.path.isfile(filename):
        print("ERROR: File not found:")
        print(filename)
        sys.exit(1)


# ============================================================
# Run NVSim
# ============================================================

print("=" * 70)
print("TASK 2: STT-MRAM vs SRAM")
print("=" * 70)

print("\n[1/2] Running NVSim...")

nv = subprocess.run(
    [NV_EXE, NV_CFG],
    cwd=NV_DIR,
    capture_output=True,
    text=True
)

with open(NV_OUT, "w") as f:
    f.write(nv.stdout)
    if nv.stderr:
        f.write("\nSTDERR:\n")
        f.write(nv.stderr)

if nv.returncode != 0:
    print("NVSim failed:")
    print(nv.stderr)
    sys.exit(1)

print("NVSim completed successfully.")


# ============================================================
# Run CACTI
# ============================================================

print("\n[2/2] Running CACTI...")

ca = subprocess.run(
    [CACTI_EXE, "-infile", CACTI_CFG],
    cwd=CACTI_DIR,
    capture_output=True,
    text=True
)

with open(CACTI_OUT, "w") as f:
    f.write(ca.stdout)
    if ca.stderr:
        f.write("\nSTDERR:\n")
        f.write(ca.stderr)

if ca.returncode != 0:
    print("CACTI failed:")
    print(ca.stderr)
    sys.exit(1)

print("CACTI completed successfully.")


# ============================================================
# NVSim extraction
# ============================================================

def nv_value(pattern, name):
    m = re.search(pattern, nv.stdout, re.MULTILINE)

    if not m:
        print(f"\nERROR: Could not find NVSim {name}")
        sys.exit(1)

    return float(m.group(1))


STT = {
    "read_latency": nv_value(
        r"Cache Hit Latency\s+=\s+([0-9.]+)ns",
        "read latency"
    ),

    "write_latency": nv_value(
        r"Cache Write Latency\s+=\s+([0-9.]+)ns",
        "write latency"
    ),

    "read_energy": nv_value(
        r"Cache Hit Dynamic Energy\s+=\s+([0-9.]+)nJ",
        "read energy"
    ),

    "write_energy": nv_value(
        r"Cache Write Dynamic Energy\s+=\s+([0-9.]+)nJ",
        "write energy"
    ),

    "leakage": nv_value(
        r"Cache Total Leakage Power\s+=\s+([0-9.]+)mW",
        "leakage"
    ),

    "area": nv_value(
        r" - Total Area\s+=\s+([0-9.]+)mm\^2",
        "area"
    )
}


# ============================================================
# CACTI extraction
#
# CACTI output normally contains:
#
#   Access time
#   Total dynamic read energy per access
#   Total dynamic write energy per access
#   Total leakage power of a bank
#   Total area
#
# ============================================================

def find_first(patterns, text, name):
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)

        if m:
            return float(m.group(1))

    print("\nWARNING: Could not automatically extract:", name)
    return None


# Access time
cacti_read_latency = find_first(
    [
        r"Access time\s*=\s*([0-9.eE+-]+)",
        r"Access time\s*:\s*([0-9.eE+-]+)",
        r"Data array, \(read\) - Access time\s*:\s*([0-9.eE+-]+)"
    ],
    ca.stdout,
    "CACTI read latency"
)

# Read energy
cacti_read_energy = find_first(
    [
        r"Total dynamic read energy per access\s*=\s*([0-9.eE+-]+)",
        r"Total dynamic read energy per access\s*:\s*([0-9.eE+-]+)"
    ],
    ca.stdout,
    "CACTI read energy"
)

# Write energy
cacti_write_energy = find_first(
    [
        r"Total dynamic write energy per access\s*=\s*([0-9.eE+-]+)",
        r"Total dynamic write energy per access\s*:\s*([0-9.eE+-]+)"
    ],
    ca.stdout,
    "CACTI write energy"
)

# Leakage
cacti_leakage = find_first(
    [
        r"Total leakage power of a bank\s*=\s*([0-9.eE+-]+)",
        r"Total leakage power.*=\s*([0-9.eE+-]+)"
    ],
    ca.stdout,
    "CACTI leakage"
)

# Area
cacti_area = find_first(
    [
        r"Total area\s*=\s*([0-9.eE+-]+)",
        r"Total area\s*:\s*([0-9.eE+-]+)"
    ],
    ca.stdout,
    "CACTI area"
)


# ============================================================
# Unit conversion
#
# CACTI commonly reports:
#   latency  -> ns
#   energy   -> nJ
#   leakage  -> W
#   area     -> mm^2
#
# The conversion below assumes the standard CACTI output.
# ============================================================

SRAM = {}

SRAM["read_latency"] = cacti_read_latency

# CACTI does not always provide a separate write latency.
# For a simple SRAM baseline, use access time if no write
# latency is separately reported.
SRAM["write_latency"] = cacti_read_latency

SRAM["read_energy"] = cacti_read_energy
SRAM["write_energy"] = cacti_write_energy

if cacti_leakage is not None:
    SRAM["leakage"] = cacti_leakage * 1000.0
else:
    SRAM["leakage"] = None

SRAM["area"] = cacti_area


# ============================================================
# Display extracted values
# ============================================================

print("\n")
print("=" * 70)
print("EXTRACTED RESULTS")
print("=" * 70)

print("\nSTT-MRAM:")
for k, v in STT.items():
    print(f"{k:<20}: {v}")

print("\nSRAM:")
for k, v in SRAM.items():
    print(f"{k:<20}: {v}")


# ============================================================
# Stop if CACTI extraction failed
# ============================================================

if any(v is None for v in SRAM.values()):
    print("\n")
    print("=" * 70)
    print("CACTI PARSING NEEDS ADJUSTMENT")
    print("=" * 70)

    print("""
CACTI ran successfully, but its output format did not match
the parser.

The complete CACTI output has been saved here:

    task2_cacti.out

Run:

    cat task2_cacti.out

and use that output to adjust the exact CACTI field names.
""")

    sys.exit(1)


# ============================================================
# Comparison
# ============================================================

names = {
    "read_latency": "Read Latency",
    "write_latency": "Write Latency",
    "read_energy": "Read Energy",
    "write_energy": "Write Energy",
    "leakage": "Leakage Power",
    "area": "Area"
}

units = {
    "read_latency": "ns",
    "write_latency": "ns",
    "read_energy": "nJ/access",
    "write_energy": "nJ/access",
    "leakage": "mW",
    "area": "mm^2"
}


print("\n")
print("=" * 70)
print("TASK 2 COMPARISON")
print("=" * 70)

print(
    f"{'Metric':<22}"
    f"{'STT-MRAM':>15}"
    f"{'SRAM':>15}"
    f"{'STT/SRAM':>15}"
)

print("-" * 70)

ratios = {}

for key in names:

    stt = STT[key]
    sram = SRAM[key]

    ratio = stt / sram
    ratios[key] = ratio

    print(
        f"{names[key]:<22}"
        f"{stt:>12.3f} {units[key]:<5}"
        f"{sram:>12.3f} {units[key]:<5}"
        f"{ratio:>12.2f}x"
    )


# ============================================================
# Find best/worst
# ============================================================

# Lower is better for every metric here.
worst = sorted(
    ratios.items(),
    key=lambda x: x[1],
    reverse=True
)

best = sorted(
    ratios.items(),
    key=lambda x: x[1]
)


print("\n")
print("=" * 70)
print("TWO DRAMATICALLY WORSE")
print("=" * 70)

for key, ratio in worst[:2]:

    print(
        f"{names[key]}: "
        f"{ratio:.2f}x higher than SRAM"
    )


print("\n")
print("=" * 70)
print("TWO DRAMATICALLY BETTER")
print("=" * 70)

for key, ratio in best[:2]:

    print(
        f"{names[key]}: "
        f"{1.0 / ratio:.2f}x lower than SRAM"
    )


# ============================================================
# Device-level explanation
# ============================================================

print("\n")
print("=" * 70)
print("DEVICE-LEVEL EXPLANATION")
print("=" * 70)

print("""
STT-MRAM stores the bit in the magnetic state of an MTJ,
whereas SRAM stores the bit in a CMOS latch.

WORSE METRICS:
The main STT-MRAM disadvantage is associated with magnetic
state switching and sensing.

WRITE:
An STT-MRAM write requires spin-polarized current through
the MTJ to change the magnetization state. The cell therefore
needs a relatively large SET/RESET current and a finite write
pulse. In this model:

    Iwrite = 200 uA
    tpulse = 10 ns

The write energy is therefore strongly dependent on the
switching current and pulse duration.

READ:
The read operation must distinguish the MTJ resistance states.
The finite resistance difference and TMR determine the
available sensing margin. The bitline, MTJ current and sense
amplifier therefore contribute significantly to read delay
and read energy.


BETTER METRICS:
STT-MRAM has two fundamental advantages.

1. NONVOLATILE STORAGE

The magnetic state remains stored without continuously
refreshing the cell. SRAM needs a continuously powered
cross-coupled CMOS latch.

Therefore STT-MRAM can have substantially lower standby
leakage at the storage-cell level.

2. CELL DENSITY

A conventional 6T SRAM cell requires six transistors to
maintain the stored state.

An STT-MRAM bit uses an MTJ plus an access transistor.
The magnetic device stores the information itself.

Therefore the storage cell can occupy less area and provide
higher bit density.

At complete-array level, peripheral circuits such as
decoders, sense amplifiers, write drivers and routing still
contribute to area and leakage.
""")


print("\n")
print("=" * 70)
print("TASK 2 COMPLETE")
print("=" * 70)

print("\nOutput files:")
print("NVSim :", NV_OUT)
print("CACTI :", CACTI_OUT)