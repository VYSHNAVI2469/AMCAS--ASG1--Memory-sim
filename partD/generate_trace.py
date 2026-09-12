import os

base_dir = "/mnt/c/Users/lenovo/Downloads/AMCS/Memsim-stack/tools/ramulator2/partD"
src_trace = "/mnt/c/Users/lenovo/Downloads/AMCS/simulators/DRAMsim3/tests/example.trace"
dst_trace = os.path.join(base_dir, "l2miss.trace")

lines_out = [
    "0x7f2a4c00 R\n",
    "0x7f2a4c40 R\n",
    "0x7f2a5000 W\n"
]

with open(src_trace) as f:
    for i, line in enumerate(f):
        if i >= 10000:
            break
        parts = line.strip().split()
        if len(parts) >= 2:
            addr = parts[0]
            op = "R" if parts[1] == "READ" else "W"
            lines_out.append(f"{addr} {op}\n")

with open(dst_trace, "w") as f:
    f.writelines(lines_out)

print(f"Generated {dst_trace} with {len(lines_out)} accesses.")
