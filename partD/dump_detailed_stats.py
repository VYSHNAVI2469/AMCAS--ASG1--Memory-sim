import os
import sys
import json

sim_dir = "/mnt/c/Users/lenovo/Downloads/AMCS/Memsim-stack/tools/ramulator2"
sys.path.insert(0, os.path.join(sim_dir, "python"))
import ramulator

trace_path = "/mnt/c/Users/lenovo/Downloads/AMCS/Memsim-stack/tools/ramulator2/partD/l2miss.trace"
interleaved_trace = "/mnt/c/Users/lenovo/Downloads/AMCS/Memsim-stack/tools/ramulator2/partD/interleaved_l2miss.trace"

def get_stats(sched_type, mapper_type, nch, trace, n_inst=10000):
    fe = ramulator.frontend.SimpleO3(
        clock_ratio=8,
        traces=[trace],
        num_expected_insts=n_inst,
        translation=ramulator.translation.NoTranslation(max_addr=2147483648),
        inst_window_depth=128,
        llc_capacity_per_core="2MB",
        llc_associativity=8,
    )
    ctrls = []
    for c in range(nch):
        ddr4 = ramulator.dram.DDR4(org_preset='DDR4_8Gb_x8', timing_preset='DDR4_3200AA', rank=2)
        sched = ramulator.scheduler.FRFCFS() if sched_type == 'FRFCFS' else ramulator.scheduler.FCFS()
        mapper = ramulator.addr_mapper.RoBaRaCoCh() if mapper_type == 'RoBaRaCoCh' else ramulator.addr_mapper.ChRaBaRoCo()
        ctrl = ramulator.controller.GenericDDR(
            dram=ddr4,
            scheduler=sched,
            refresh_manager=ramulator.refresh_manager.AllBank(),
            row_policy=ramulator.row_policy.Open(),
            addr_mapper=mapper,
        )
        ctrls.append(ctrl)
    mem = ramulator.memory_system.GenericDRAM(
        clock_ratio=3,
        controllers=ctrls,
        channel_mapper=ramulator.channel_mapper.CacheLineInterleave(),
    )
    sim = ramulator.Simulation(fe, mem)
    sim.run()
    return sim.stats

configs = [
    ('Task 1 (Baseline)', 'FRFCFS', 'RoBaRaCoCh', 1, trace_path, 10000),
    ('Task 2 (FCFS)', 'FCFS', 'RoBaRaCoCh', 1, trace_path, 10000),
    ('Task 2b (Interleaved FRFCFS)', 'FRFCFS', 'RoBaRaCoCh', 1, interleaved_trace, 5000),
    ('Task 2b (Interleaved FCFS)', 'FCFS', 'RoBaRaCoCh', 1, interleaved_trace, 5000),
    ('Task 3 (ChRaBaRoCo)', 'FRFCFS', 'ChRaBaRoCo', 1, trace_path, 10000),
    ('Task 4 (2 Channels)', 'FRFCFS', 'RoBaRaCoCh', 2, trace_path, 10000)
]

all_data = {}
for name, s, m, ch, tr, n in configs:
    print(f"Running {name}...")
    st = get_stats(s, m, ch, tr, n)
    all_data[name] = st

out_file = "/mnt/c/Users/lenovo/Downloads/AMCS/Memsim-stack/tools/ramulator2/partD/detailed_stats.json"
with open(out_file, 'w') as f:
    json.dump(all_data, f, indent=2)
print(f"Detailed stats successfully saved to {out_file}!")
