import os
import sys

sim_dir = "/mnt/c/Users/lenovo/Downloads/AMCS/Memsim-stack/tools/ramulator2"
sys.path.insert(0, os.path.join(sim_dir, "python"))
import ramulator

trace_path = "/mnt/c/Users/lenovo/Downloads/AMCS/Memsim-stack/tools/ramulator2/partD/l2miss.trace"

frontend = ramulator.frontend.SimpleO3(
    clock_ratio=8,
    traces=[trace_path],
    num_expected_insts=10000,
    translation=ramulator.translation.NoTranslation(max_addr=2147483648),
)
ddr4_0 = ramulator.dram.DDR4(org_preset="DDR4_8Gb_x8", timing_preset="DDR4_3200AA", rank=2)
ddr4_1 = ramulator.dram.DDR4(org_preset="DDR4_8Gb_x8", timing_preset="DDR4_3200AA", rank=2)

ctrl0 = ramulator.controller.GenericDDR(
    dram=ddr4_0,
    scheduler=ramulator.scheduler.FRFCFS(),
    refresh_manager=ramulator.refresh_manager.AllBank(),
    row_policy=ramulator.row_policy.Open(),
    addr_mapper=ramulator.addr_mapper.RoBaRaCoCh(),
)
ctrl1 = ramulator.controller.GenericDDR(
    dram=ddr4_1,
    scheduler=ramulator.scheduler.FRFCFS(),
    refresh_manager=ramulator.refresh_manager.AllBank(),
    row_policy=ramulator.row_policy.Open(),
    addr_mapper=ramulator.addr_mapper.RoBaRaCoCh(),
)
mem = ramulator.memory_system.GenericDRAM(
    clock_ratio=3,
    controllers=[ctrl0, ctrl1],
    channel_mapper=ramulator.channel_mapper.CacheLineInterleave(),
)

sim = ramulator.Simulation(frontend, mem)
sim.run()

print("Full stats dictionary structure:")
import pprint
pprint.pprint(sim.stats)
