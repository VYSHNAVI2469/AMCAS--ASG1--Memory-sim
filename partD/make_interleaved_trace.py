import os
import sys

# Generate an interleaved trace representative of graph analytics / multi-stream L2 misses:
# Stream A accesses Row 0x1000 in Bank 0: 0x10000000, 0x10000040, 0x10000080, ...
# Stream B accesses Row 0x2000 in Bank 0: 0x20000000, 0x20000040, 0x20000080, ...
# When interleaved: A0, B0, A1, B1, A2, B2...
# FRFCFS will batch A together and B together, maintaining ~50-80% row hit rate.
# FCFS will thrash: A0 closes B, B0 closes A, A1 closes B... hit rate collapses to 0%!

base_dir = "/mnt/c/Users/lenovo/Downloads/AMCS/Memsim-stack/tools/ramulator2/partD"
interleaved_trace = os.path.join(base_dir, "interleaved_l2miss.trace")

lines = []
# Create 5000 accesses with alternating row locality
for i in range(2500):
    addr_a = 0x10000000 + (i % 64) * 64
    addr_b = 0x20000000 + (i % 64) * 64
    lines.append(f"{hex(addr_a)} R\n")
    lines.append(f"{hex(addr_b)} R\n")

with open(interleaved_trace, "w") as f:
    f.writelines(lines)

print(f"Created interleaved trace with {len(lines)} accesses.")
