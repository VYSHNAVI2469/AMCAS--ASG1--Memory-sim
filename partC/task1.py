import subprocess
import os
import re
import sys

# ============================================================
# NVSim Task 1
# 2 MB STT-MRAM Cache
# ============================================================

# Actual NVSim directory
NVSim_DIR = "/mnt/c/Users/lenovo/Downloads/AMCS/Memsim-stack/tools/NVSim"

# NVSim executable
NVSim_EXE = os.path.join(NVSim_DIR, "nvsim")

# Task-1 configuration file
CONFIG_FILE = os.path.join(NVSim_DIR, "STT_cache.cfg")

# Output file
OUTPUT_FILE = os.path.join(NVSim_DIR, "nvsim_task1_out.txt")


# ============================================================
# Check files
# ============================================================

print("=" * 70)
print("NVSim Task 1 - 2 MB STT-MRAM Cache")
print("=" * 70)

if not os.path.isfile(NVSim_EXE):
    print("ERROR: NVSim executable not found:")
    print(NVSim_EXE)
    sys.exit(1)

if not os.path.isfile(CONFIG_FILE):
    print("ERROR: Configuration file not found:")
    print(CONFIG_FILE)
    print("\nCreate STT_cache.cfg in the NVSim directory first.")
    sys.exit(1)

print("\nNVSim executable:")
print(NVSim_EXE)

print("\nConfiguration:")
print(CONFIG_FILE)


# ============================================================
# Run NVSim
# ============================================================

print("\nRunning NVSim...\n")

p = subprocess.run(
    [NVSim_EXE, CONFIG_FILE],
    cwd=NVSim_DIR,
    capture_output=True,
    text=True
)

# Save complete output
with open(OUTPUT_FILE, "w") as f:
    f.write(p.stdout)

    if p.stderr:
        f.write("\n\nSTDERR:\n")
        f.write(p.stderr)


# ============================================================
# Check execution
# ============================================================

print("Exit code:", p.returncode)

if p.returncode != 0:
    print("\nNVSim failed.")
    print("\nSTDERR:")
    print(p.stderr)
    sys.exit(1)


# ============================================================
# Extract Task 1 metrics
# ============================================================

output = p.stdout


def extract(pattern, name):
    match = re.search(pattern, output, re.MULTILINE)

    if match:
        return match.group(1)

    return "NOT FOUND"


# Cache-level metrics
area = extract(
    r" - Total Area = ([0-9.]+mm\^2)",
    "Total Area"
)

read_latency = extract(
    r" - Cache Hit Latency\s+= ([0-9.]+ns)",
    "Read Latency"
)

write_latency = extract(
    r" - Cache Write Latency = ([0-9.]+ns)",
    "Write Latency"
)

read_energy = extract(
    r" - Cache Hit Dynamic Energy\s+= ([0-9.]+nJ per access)",
    "Read Energy"
)

write_energy = extract(
    r" - Cache Write Dynamic Energy = ([0-9.]+nJ per access)",
    "Write Energy"
)

leakage = extract(
    r" - Cache Total Leakage Power\s+= ([0-9.]+mW)",
    "Leakage"
)


# ============================================================
# Print results
# ============================================================

print("\n")
print("=" * 70)
print("TASK 1 METRICS")
print("=" * 70)

print(f"Read Latency             = {read_latency}")
print(f"Write Latency            = {write_latency}")
print(f"Read Dynamic Energy      = {read_energy}")
print(f"Write Dynamic Energy     = {write_energy}")
print(f"Total Leakage Power      = {leakage}")
print(f"Total Area               = {area}")

print("=" * 70)

print("\nComplete NVSim output saved to:")
print(OUTPUT_FILE)