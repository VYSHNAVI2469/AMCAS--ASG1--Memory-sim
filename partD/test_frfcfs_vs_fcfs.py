import os
import sys

sim_dir = "/mnt/c/Users/lenovo/Downloads/AMCS/Memsim-stack/tools/ramulator2"
sys.path.insert(0, os.path.join(sim_dir, "python"))
import ramulator

trace_path = "/mnt/c/Users/lenovo/Downloads/AMCS/Memsim-stack/tools/ramulator2/partD/interleaved_l2miss.trace"

def run_sched(scheduler_type):
    frontend = ramulator.frontend.SimpleO3(
        clock_ratio=8,
        traces=[trace_path],
        num_expected_insts=5000,
        translation=ramulator.translation.NoTranslation(max_addr=2147483648),
        inst_window_depth=256,
        llc_num_mshr_per_core=64,
        llc_capacity_per_core="128KB", # Small LLC so misses bypass to memory controller
    )
    ddr4 = ramulator.dram.DDR4(org_preset="DDR4_8Gb_x8", timing_preset="DDR4_3200AA", rank=2)
    sched = ramulator.scheduler.FRFCFS() if scheduler_type == "FRFCFS" else ramulator.scheduler.FCFS()
    ctrl = ramulator.controller.GenericDDR(
        dram=ddr4,
        scheduler=sched,
        refresh_manager=ramulator.refresh_manager.AllBank(),
        row_policy=ramulator.row_policy.Open(),
        addr_mapper=ramulator.addr_mapper.RoBaRaCoCh(),
    )
    mem = ramulator.memory_system.GenericDRAM(
        clock_ratio=3,
        controllers=[ctrl],
        channel_mapper=ramulator.channel_mapper.CacheLineInterleave(),
    )
    sim = ramulator.Simulation(frontend, mem)
    sim.run()
    s = sim.stats["memory_system"]["controller"]
    hits = s['row_hits']
    misses = s['row_misses']
    conflicts = s['row_conflicts']
    tot = hits + misses + conflicts
    hr = (hits / tot * 100) if tot > 0 else 0
    return {
        "cycles": s['cycles'],
        "avg_read_lat": s['avg_read_latency'],
        "hits": hits,
        "misses": misses,
        "conflicts": conflicts,
        "hit_rate": hr
    }

res_frfcfs = run_sched("FRFCFS")
res_fcfs = run_sched("FCFS")

print("==================================================")
print(f"FRFCFS: cycles={res_frfcfs['cycles']}, avg_lat={res_frfcfs['avg_read_lat']:.2f}, hits={res_frfcfs['hits']}, conflicts={res_frfcfs['conflicts']}, hit_rate={res_frfcfs['hit_rate']:.2f}%")
print(f"FCFS:   cycles={res_fcfs['cycles']}, avg_lat={res_fcfs['avg_read_lat']:.2f}, hits={res_fcfs['hits']}, conflicts={res_fcfs['conflicts']}, hit_rate={res_fcfs['hit_rate']:.2f}%")
print("==================================================")
