import os
import sys

sim_dir = "/mnt/c/Users/lenovo/Downloads/AMCS/Memsim-stack/tools/ramulator2"
sys.path.insert(0, os.path.join(sim_dir, "python"))
import ramulator

trace_path = "/mnt/c/Users/lenovo/Downloads/AMCS/Memsim-stack/tools/ramulator2/partD/l2miss.trace"
interleaved_trace = "/mnt/c/Users/lenovo/Downloads/AMCS/Memsim-stack/tools/ramulator2/partD/interleaved_l2miss.trace"

def run_ramulator(name, trace_file, scheduler_type="FRFCFS", mapper_type="RoBaRaCoCh", num_channels=1, num_insts=10000):
    print(f"\n=======================================================")
    print(f"Running {name}...")
    print(f"Config: Scheduler={scheduler_type}, Mapper={mapper_type}, Channels={num_channels}, Trace={os.path.basename(trace_file)}")
    print(f"=======================================================")
    
    frontend = ramulator.frontend.SimpleO3(
        clock_ratio=8,
        traces=[trace_file],
        num_expected_insts=num_insts,
        translation=ramulator.translation.NoTranslation(max_addr=2147483648),
        inst_window_depth=128,
        llc_capacity_per_core="2MB",
        llc_associativity=8,
    )
    
    controllers = []
    for c in range(num_channels):
        ddr4 = ramulator.dram.DDR4(
            org_preset="DDR4_8Gb_x8",
            timing_preset="DDR4_3200AA",
            rank=2,
            verbose=(c == 0 and name == "Task 1 (Baseline)")
        )
        
        sched = ramulator.scheduler.FRFCFS() if scheduler_type == "FRFCFS" else ramulator.scheduler.FCFS()
        mapper = ramulator.addr_mapper.RoBaRaCoCh() if mapper_type == "RoBaRaCoCh" else ramulator.addr_mapper.ChRaBaRoCo()
        
        ctrl = ramulator.controller.GenericDDR(
            dram=ddr4,
            scheduler=sched,
            refresh_manager=ramulator.refresh_manager.AllBank(),
            row_policy=ramulator.row_policy.Open(),
            addr_mapper=mapper,
        )
        controllers.append(ctrl)
        
    mem = ramulator.memory_system.GenericDRAM(
        clock_ratio=3,
        controllers=controllers,
        channel_mapper=ramulator.channel_mapper.CacheLineInterleave(),
    )
    
    sim = ramulator.Simulation(frontend, mem)
    sim.run()
    
    stats = sim.stats
    mem_stats = stats["memory_system"]
    
    # Aggregate stats across controllers
    tot_cycles = 0
    tot_reads = 0
    tot_writes = 0
    tot_hits = 0
    tot_misses = 0
    tot_conflicts = 0
    tot_read_lat = 0
    tot_write_lat = 0
    
    controllers_stat = mem_stats.get("controller", [])
    if isinstance(controllers_stat, dict):
        controllers_stat = [controllers_stat]
        
    for v in controllers_stat:
        if isinstance(v, dict):
            tot_cycles = max(tot_cycles, v.get("cycles", 0))
            tot_reads += v.get("num_read_reqs", 0)
            tot_writes += v.get("num_write_reqs", 0)
            tot_hits += v.get("row_hits", 0)
            tot_misses += v.get("row_misses", 0)
            tot_conflicts += v.get("row_conflicts", 0)
            tot_read_lat += v.get("read_latency", 0)
            tot_write_lat += v.get("write_latency", 0)
            
    tot_accesses = tot_hits + tot_misses + tot_conflicts
    hit_rate = (tot_hits / tot_accesses * 100.0) if tot_accesses > 0 else 0.0
    avg_read_lat = (tot_read_lat / tot_reads) if tot_reads > 0 else 0.0
    avg_write_lat = (tot_write_lat / tot_writes) if tot_writes > 0 else 0.0
    
    res = {
        "name": name,
        "cycles": tot_cycles,
        "reads": tot_reads,
        "writes": tot_writes,
        "total_accesses": tot_accesses,
        "hits": tot_hits,
        "misses": tot_misses,
        "conflicts": tot_conflicts,
        "hit_rate": hit_rate,
        "total_read_latency": tot_read_lat,
        "avg_read_latency": avg_read_lat,
        "total_write_latency": tot_write_lat,
        "avg_write_latency": avg_write_lat,
    }
    
    print(f"Results for {name}:")
    print(f"  Memory Cycles:       {tot_cycles}")
    print(f"  Total Read Latency:  {tot_read_lat} (Avg: {avg_read_lat:.2f} cycles)")
    print(f"  Total Write Latency: {tot_write_lat} (Avg: {avg_write_lat:.2f} cycles)")
    print(f"  Row Hits:            {tot_hits}")
    print(f"  Row Misses:          {tot_misses}")
    print(f"  Row Conflicts:       {tot_conflicts}")
    print(f"  Row-Buffer Hit Rate: {hit_rate:.2f}%")
    
    return res

results = []

# Task 1: Baseline (FRFCFS, RoBaRaCoCh, 1 Channel)
t1 = run_ramulator("Task 1 (Baseline)", trace_path, scheduler_type="FRFCFS", mapper_type="RoBaRaCoCh", num_channels=1)
results.append(t1)

# Task 2: FCFS (FCFS, RoBaRaCoCh, 1 Channel) on both main trace and interleaved trace
t2 = run_ramulator("Task 2 (FCFS)", trace_path, scheduler_type="FCFS", mapper_type="RoBaRaCoCh", num_channels=1)
results.append(t2)

# Also run Task 2 on interleaved trace to demonstrate classic row-buffer collapse
t2_interleaved_fr = run_ramulator("Task 2b (Interleaved FRFCFS)", interleaved_trace, scheduler_type="FRFCFS", mapper_type="RoBaRaCoCh", num_channels=1, num_insts=5000)
t2_interleaved_fc = run_ramulator("Task 2b (Interleaved FCFS)", interleaved_trace, scheduler_type="FCFS", mapper_type="RoBaRaCoCh", num_channels=1, num_insts=5000)

# Task 3: Address Mapping (FRFCFS, ChRaBaRoCo - Row below Bank, 1 Channel)
t3 = run_ramulator("Task 3 (ChRaBaRoCo - Row below Bank)", trace_path, scheduler_type="FRFCFS", mapper_type="ChRaBaRoCo", num_channels=1)
results.append(t3)

# Task 4: Double Channels (FRFCFS, RoBaRaCoCh, 2 Channels)
t4 = run_ramulator("Task 4 (2 Channels)", trace_path, scheduler_type="FRFCFS", mapper_type="RoBaRaCoCh", num_channels=2)
results.append(t4)

print("\n\n" + "="*95)
print(f"{'Configuration':38s} | {'Memory Cycles':14s} | {'Avg Read Lat (cyc)':18s} | {'Row Hit Rate (%)':16s}")
print("="*95)
for r in results:
    print(f"{r['name']:38s} | {r['cycles']:14d} | {r['avg_read_latency']:18.2f} | {r['hit_rate']:16.2f}%")
print("="*95)
print(f"{t2_interleaved_fr['name']:38s} | {t2_interleaved_fr['cycles']:14d} | {t2_interleaved_fr['avg_read_latency']:18.2f} | {t2_interleaved_fr['hit_rate']:16.2f}%")
print(f"{t2_interleaved_fc['name']:38s} | {t2_interleaved_fc['cycles']:14d} | {t2_interleaved_fc['avg_read_latency']:18.2f} | {t2_interleaved_fc['hit_rate']:16.2f}%")
print("="*95)
