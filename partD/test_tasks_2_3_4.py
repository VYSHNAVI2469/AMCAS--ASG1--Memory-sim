import os
import sys

sim_dir = "/mnt/c/Users/lenovo/Downloads/AMCS/Memsim-stack/tools/ramulator2"
sys.path.insert(0, os.path.join(sim_dir, "python"))
import ramulator

trace_path = "/mnt/c/Users/lenovo/Downloads/AMCS/Memsim-stack/tools/ramulator2/partD/l2miss.trace"

# Test Task 2 (FCFS)
print("Testing Task 2 (FCFS)...")
frontend2 = ramulator.frontend.SimpleO3(
    clock_ratio=8,
    traces=[trace_path],
    num_expected_insts=10000,
    translation=ramulator.translation.NoTranslation(max_addr=2147483648),
)
ddr4_2 = ramulator.dram.DDR4(org_preset="DDR4_8Gb_x8", timing_preset="DDR4_3200AA", rank=2)
ctrl2 = ramulator.controller.GenericDDR(
    dram=ddr4_2,
    scheduler=ramulator.scheduler.FCFS(),
    refresh_manager=ramulator.refresh_manager.AllBank(),
    row_policy=ramulator.row_policy.Open(),
    addr_mapper=ramulator.addr_mapper.RoBaRaCoCh(),
)
mem2 = ramulator.memory_system.GenericDRAM(
    clock_ratio=3,
    controllers=[ctrl2],
    channel_mapper=ramulator.channel_mapper.CacheLineInterleave(),
)
sim2 = ramulator.Simulation(frontend2, mem2)
sim2.run()
s2 = sim2.stats["memory_system"]["controller"]
print(f"Task 2 (FCFS): cycles={s2['cycles']}, avg_lat={s2['avg_read_latency']:.2f}, hits={s2['row_hits']}, misses={s2['row_misses']}, conflicts={s2['row_conflicts']}")

# Test Task 3 (ChRaBaRoCo)
print("\nTesting Task 3 (ChRaBaRoCo)...")
frontend3 = ramulator.frontend.SimpleO3(
    clock_ratio=8,
    traces=[trace_path],
    num_expected_insts=10000,
    translation=ramulator.translation.NoTranslation(max_addr=2147483648),
)
ddr4_3 = ramulator.dram.DDR4(org_preset="DDR4_8Gb_x8", timing_preset="DDR4_3200AA", rank=2)
ctrl3 = ramulator.controller.GenericDDR(
    dram=ddr4_3,
    scheduler=ramulator.scheduler.FRFCFS(),
    refresh_manager=ramulator.refresh_manager.AllBank(),
    row_policy=ramulator.row_policy.Open(),
    addr_mapper=ramulator.addr_mapper.ChRaBaRoCo(),
)
mem3 = ramulator.memory_system.GenericDRAM(
    clock_ratio=3,
    controllers=[ctrl3],
    channel_mapper=ramulator.channel_mapper.CacheLineInterleave(),
)
sim3 = ramulator.Simulation(frontend3, mem3)
sim3.run()
s3 = sim3.stats["memory_system"]["controller"]
print(f"Task 3 (ChRaBaRoCo): cycles={s3['cycles']}, avg_lat={s3['avg_read_latency']:.2f}, hits={s3['row_hits']}, misses={s3['row_misses']}, conflicts={s3['row_conflicts']}")

# Test Task 4 (2 channels)
print("\nTesting Task 4 (2 Channels)...")
frontend4 = ramulator.frontend.SimpleO3(
    clock_ratio=8,
    traces=[trace_path],
    num_expected_insts=10000,
    translation=ramulator.translation.NoTranslation(max_addr=2147483648),
)
ddr4_4a = ramulator.dram.DDR4(org_preset="DDR4_8Gb_x8", timing_preset="DDR4_3200AA", channel=2, rank=2)
ddr4_4b = ramulator.dram.DDR4(org_preset="DDR4_8Gb_x8", timing_preset="DDR4_3200AA", channel=2, rank=2)
ctrl4a = ramulator.controller.GenericDDR(
    dram=ddr4_4a,
    scheduler=ramulator.scheduler.FRFCFS(),
    refresh_manager=ramulator.refresh_manager.AllBank(),
    row_policy=ramulator.row_policy.Open(),
    addr_mapper=ramulator.addr_mapper.RoBaRaCoCh(),
)
ctrl4b = ramulator.controller.GenericDDR(
    dram=ddr4_4b,
    scheduler=ramulator.scheduler.FRFCFS(),
    refresh_manager=ramulator.refresh_manager.AllBank(),
    row_policy=ramulator.row_policy.Open(),
    addr_mapper=ramulator.addr_mapper.RoBaRaCoCh(),
)
mem4 = ramulator.memory_system.GenericDRAM(
    clock_ratio=3,
    controllers=[ctrl4a, ctrl4b],
    channel_mapper=ramulator.channel_mapper.CacheLineInterleave(),
)
sim4 = ramulator.Simulation(frontend4, mem4)
sim4.run()
s4 = sim4.stats["memory_system"]
print("Task 4 (2 Channels):")
for k, v in s4.items():
    if "controller" in k:
        print(f"  {k}: cycles={v.get('cycles')}, avg_lat={v.get('avg_read_latency', 0):.2f}, hits={v.get('row_hits')}, misses={v.get('row_misses')}, conflicts={v.get('row_conflicts')}")
