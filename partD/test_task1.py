import os
import sys

sim_dir = "/mnt/c/Users/lenovo/Downloads/AMCS/Memsim-stack/tools/ramulator2"
sys.path.insert(0, os.path.join(sim_dir, "python"))
import ramulator

trace_path = "/mnt/c/Users/lenovo/Downloads/AMCS/Memsim-stack/tools/ramulator2/partD/l2miss.trace"

print("Setting up Task 1...")
frontend = ramulator.frontend.SimpleO3(
    clock_ratio=8,
    traces=[trace_path],
    num_expected_insts=10000,
    translation=ramulator.translation.NoTranslation(max_addr=2147483648),
)

ddr4 = ramulator.dram.DDR4(
    org_preset="DDR4_8Gb_x8",
    timing_preset="DDR4_3200AA",
    rank=2,
    verbose=True
)

ctrl = ramulator.controller.GenericDDR(
    dram=ddr4,
    scheduler=ramulator.scheduler.FRFCFS(),
    refresh_manager=ramulator.refresh_manager.AllBank(),
    row_policy=ramulator.row_policy.Open(),
    addr_mapper=ramulator.addr_mapper.RoBaRaCoCh(),
)

mem = ramulator.memory_system.GenericDRAM(
    clock_ratio=3,
    controllers=[ctrl],
    channel_mapper=ramulator.channel_mapper.CacheLineInterleave(),
)

print("Starting Task 1 simulation...")
sim = ramulator.Simulation(frontend, mem)
sim.run()

stats = sim.stats
print("Simulation finished! Stats keys:", list(stats.keys()))
ctrl_stats = stats["memory_system"]["controller"]
for k, v in ctrl_stats.items():
    print(f"  {k}: {v}")
