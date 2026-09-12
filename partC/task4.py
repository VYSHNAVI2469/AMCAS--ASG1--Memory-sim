import subprocess
import os

# ============================================================
# TASK 4 - NVSim
# Halve ResetCurrent from 200 uA to 100 uA
# Show coupling:
# ResetCurrent -> Access transistor size -> CellArea -> Cache Area
# ============================================================

SIM_DIR = "/mnt/c/Users/lenovo/Downloads/AMCS/Memsim-stack/tools/NVSim"

NVSim = os.path.join(SIM_DIR, "nvsim")

BASE_CELL = os.path.join(SIM_DIR, "sample_STTRAM.cell")
BASE_CFG = os.path.join(SIM_DIR, "STT_cache.cfg")

CASE_A_CELL = os.path.join(SIM_DIR, "task4_case_a.cell")
CASE_A_CFG = os.path.join(SIM_DIR, "STT_task4_a.cfg")
CASE_A_OUT = os.path.join(SIM_DIR, "nvsim_task4_a_out.txt")

CASE_B_CELL = os.path.join(SIM_DIR, "task4_case_b.cell")
CASE_B_CFG = os.path.join(SIM_DIR, "STT_task4_b.cfg")
CASE_B_OUT = os.path.join(SIM_DIR, "nvsim_task4_b_out.txt")


# ------------------------------------------------------------
# Check required files
# ------------------------------------------------------------

if not os.path.isfile(NVSim):
    raise FileNotFoundError("nvsim executable not found")

if not os.path.isfile(BASE_CELL):
    raise FileNotFoundError(
        "sample_STTRAM.cell not found in NVSim directory"
    )

if not os.path.isfile(BASE_CFG):
    raise FileNotFoundError(
        "STT_cache.cfg not found in NVSim directory"
    )


# ------------------------------------------------------------
# Read original cell file
# ------------------------------------------------------------

with open(BASE_CELL, "r") as f:
    original_cell = f.readlines()


# ============================================================
# CASE A
# Only halve ResetCurrent to 100 uA
#
# Keep:
#   AccessCMOSWidth = original
#   CellArea        = original
#
# This shows that simply changing the electrical current
# does NOT automatically change the physical cell area.
# ============================================================

case_a_lines = []

for line in original_cell:

    if line.strip().startswith("-ResetCurrent"):
        case_a_lines.append(
            "-ResetCurrent (uA): 100\n"
        )

    else:
        case_a_lines.append(line)


with open(CASE_A_CELL, "w") as f:
    f.writelines(case_a_lines)


# ------------------------------------------------------------
# Create Case A configuration
# ------------------------------------------------------------

with open(BASE_CFG, "r") as f:
    cfg_lines = f.readlines()

case_a_cfg_lines = []

for line in cfg_lines:

    if line.strip().startswith("-MemoryCellInputFile:"):
        case_a_cfg_lines.append(
            "-MemoryCellInputFile: task4_case_a.cell\n"
        )

    else:
        case_a_cfg_lines.append(line)


with open(CASE_A_CFG, "w") as f:
    f.writelines(case_a_cfg_lines)


# ------------------------------------------------------------
# Run Case A
# ------------------------------------------------------------

print("\n============================================================")
print("CASE A")
print("ResetCurrent = 100 uA")
print("AccessCMOSWidth = ORIGINAL")
print("CellArea = ORIGINAL")
print("============================================================")

p_a = subprocess.run(
    [NVSim, "STT_task4_a.cfg"],
    cwd=SIM_DIR,
    capture_output=True,
    text=True
)

with open(CASE_A_OUT, "w") as f:
    f.write(p_a.stdout)
    f.write("\n\nSTDERR:\n")
    f.write(p_a.stderr)


print("Exit code:", p_a.returncode)

if p_a.returncode != 0:
    print("\nNVSim ERROR:")
    print(p_a.stderr)


# ------------------------------------------------------------
# Print important Case A results
# ------------------------------------------------------------

for line in p_a.stdout.splitlines():

    if any(key in line for key in [
        "Cache Hit Latency",
        "Cache Miss Latency",
        "Cache Write Latency",
        "Cache Hit Dynamic Energy",
        "Cache Miss Dynamic Energy",
        "Cache Write Dynamic Energy",
        "Total Area =",
        "Data Array Area",
        "Tag Array Area",
        "Cache Total Leakage",
        "Cache Total Leakage Power",
        "Cell Area",
        "Access Transistor"
    ]):
        print(line)


# ============================================================
# CASE B
#
# ResetCurrent = 100 uA
# AccessCMOSWidth = 3 F
# CellArea = 36 F^2
#
# This explicitly models the physical consequence:
#
# Lower write current
#       ↓
# smaller access transistor
#       ↓
# smaller bitcell
#       ↓
# smaller array area
#       ↓
# higher density
# ============================================================

case_b_lines = []

for line in original_cell:

    if line.strip().startswith("-ResetCurrent"):
        case_b_lines.append(
            "-ResetCurrent (uA): 100\n"
        )

    elif line.strip().startswith("-AccessCMOSWidth"):
        case_b_lines.append(
            "-AccessCMOSWidth (F): 3\n"
        )

    elif line.strip().startswith("-CellArea"):
        case_b_lines.append(
            "-CellArea (F^2): 36\n"
        )

    else:
        case_b_lines.append(line)


with open(CASE_B_CELL, "w") as f:
    f.writelines(case_b_lines)


# ------------------------------------------------------------
# Create Case B configuration
# ------------------------------------------------------------

case_b_cfg_lines = []

for line in cfg_lines:

    if line.strip().startswith("-MemoryCellInputFile:"):
        case_b_cfg_lines.append(
            "-MemoryCellInputFile: task4_case_b.cell\n"
        )

    else:
        case_b_cfg_lines.append(line)


with open(CASE_B_CFG, "w") as f:
    f.writelines(case_b_cfg_lines)


# ------------------------------------------------------------
# Run Case B
# ------------------------------------------------------------

print("\n============================================================")
print("CASE B")
print("ResetCurrent = 100 uA")
print("AccessCMOSWidth = 3 F")
print("CellArea = 36 F^2")
print("============================================================")

p_b = subprocess.run(
    [NVSim, "STT_task4_b.cfg"],
    cwd=SIM_DIR,
    capture_output=True,
    text=True
)

with open(CASE_B_OUT, "w") as f:
    f.write(p_b.stdout)
    f.write("\n\nSTDERR:\n")
    f.write(p_b.stderr)


print("Exit code:", p_b.returncode)

if p_b.returncode != 0:
    print("\nNVSim ERROR:")
    print(p_b.stderr)


# ------------------------------------------------------------
# Print important Case B results
# ------------------------------------------------------------

for line in p_b.stdout.splitlines():

    if any(key in line for key in [
        "Cache Hit Latency",
        "Cache Miss Latency",
        "Cache Write Latency",
        "Cache Hit Dynamic Energy",
        "Cache Miss Dynamic Energy",
        "Cache Write Dynamic Energy",
        "Total Area =",
        "Data Array Area",
        "Tag Array Area",
        "Cache Total Leakage",
        "Cache Total Leakage Power",
        "Cell Area",
        "Access Transistor"
    ]):
        print(line)


# ============================================================
# SUMMARY
# ============================================================

print("\n============================================================")
print("TASK 4 SUMMARY")
print("============================================================")

print("Case A:")
print("  ResetCurrent = 100 uA")
print("  Original access transistor")
print("  Original cell area")

print("\nCase B:")
print("  ResetCurrent = 100 uA")
print("  AccessCMOSWidth = 3 F")
print("  CellArea = 36 F^2")

print("\nRequired design chain:")
print("ResetCurrent ↓")
print("      ↓")
print("Required write-drive strength ↓")
print("      ↓")
print("Access transistor width ↓")
print("      ↓")
print("Bitcell area ↓")
print("      ↓")
print("Array area ↓")
print("      ↓")
print("Memory density ↑")

print("\nOutput files:")
print("  ", CASE_A_OUT)
print("  ", CASE_B_OUT)