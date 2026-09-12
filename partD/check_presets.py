import sys
import os

# Add ramulator to sys.path
sim_dir = "/mnt/c/Users/lenovo/Downloads/AMCS/Memsim-stack/tools/ramulator2"
sys.path.insert(0, os.path.join(sim_dir, "python"))

import ramulator

print("Imported ramulator successfully!")

# Test DRAM DDR4
ddr4 = ramulator.dram.DDR4(
    org_preset="DDR4_8Gb_x8",
    timing_preset="DDR4_3200AA",
    rank=2,
    verbose=True
)
print("DDR4 configured with DDR4_3200AA!")
