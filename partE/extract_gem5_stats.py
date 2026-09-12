#!/usr/bin/env python3
import os
import re
import sys
import glob

def parse_stats(stats_path):
    stats = {}
    if not os.path.exists(stats_path):
        return None
    with open(stats_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('---'):
                continue
            parts = line.split()
            if len(parts) >= 2:
                key = parts[0]
                val = parts[1]
                stats[key] = val
    return stats

def main():
    runs_dir = sys.argv[1] if len(sys.argv) > 1 else "runs"
    configs = [
        ("Task 1 (O3)", "bfs_sram_2mb_7cy", "bfs", "SRAM 2MB @ 7cy", "O3"),
        ("Task 1 (O3)", "bfs_mram_8mb_14cy", "bfs", "MRAM 8MB @ 14cy", "O3"),
        ("Task 1 (O3)", "sssp_sram_2mb_7cy", "sssp", "SRAM 2MB @ 7cy", "O3"),
        ("Task 1 (O3)", "sssp_mram_8mb_14cy", "sssp", "MRAM 8MB @ 14cy", "O3"),
        ("Task 3 (In-Order)", "inorder_bfs_sram_2mb_7cy", "bfs", "SRAM 2MB @ 7cy", "TimingSimple"),
        ("Task 3 (In-Order)", "inorder_bfs_mram_8mb_14cy", "bfs", "MRAM 8MB @ 14cy", "TimingSimple"),
        ("Task 3 (In-Order)", "inorder_sssp_sram_2mb_7cy", "sssp", "SRAM 2MB @ 7cy", "TimingSimple"),
        ("Task 3 (In-Order)", "inorder_sssp_mram_8mb_14cy", "sssp", "MRAM 8MB @ 14cy", "TimingSimple"),
    ]

    print(f"{'Task / Core':<20} {'Kernel':<6} {'Configuration':<22} {'IPC':<8} {'L2 Miss Rate':<14} {'simSeconds':<12} {'L2 Accesses':<12} {'Avg Miss Lat (ps)':<18}")
    print("-" * 115)

    results = {}
    for task_group, tag, kernel, config_desc, cpu in configs:
        stats_file = os.path.join(runs_dir, tag, "stats.txt")
        stats = parse_stats(stats_file)
        if not stats:
            print(f"{task_group:<20} {kernel:<6} {config_desc:<22} [NOT YET COMPLETED]")
            continue
        
        ipc = None
        for k in ["system.switch_cpus.ipc", "system.cpu.ipc", "system.switch_cpus.cpi", "system.cpu.cpi"]:
            if k in stats and str(stats[k]).lower() != "nan":
                val = float(stats[k])
                ipc = val if "ipc" in k else (1.0 / val if val > 0 else 0.0)
                break
        if ipc is None:
            insts = float(stats.get("system.switch_cpus.committedInsts",
                          stats.get("system.cpu.committedInsts", 
                          stats.get("system.switch_cpus.exec_context.thread_0.numInsts",
                          stats.get("system.cpu.exec_context.thread_0.numInsts", 0)))))
            cycles = float(stats.get("system.switch_cpus.numCycles", stats.get("system.cpu.numCycles", 0)))
            ipc = (insts / cycles) if cycles > 0 else 0.0


        miss_rate = float(stats.get("system.l2.overallMissRate::total", 0.0))
        sim_sec = float(stats.get("simSeconds", 0.0))
        acc = int(float(stats.get("system.l2.overallAccesses::total", 0)))
        miss_lat = float(stats.get("system.l2.overallAvgMissLatency::total", 0.0))

        results[tag] = {
            "kernel": kernel,
            "config": config_desc,
            "cpu": cpu,
            "ipc": ipc,
            "miss_rate": miss_rate,
            "sim_sec": sim_sec,
            "acc": acc,
            "miss_lat": miss_lat
        }

        print(f"{task_group:<20} {kernel:<6} {config_desc:<22} {ipc:<8.4f} {miss_rate:<14.4f} {sim_sec:<12.6f} {acc:<12d} {miss_lat:<18.1f}")

    # Compute Speedups
    print("\n=== Computed Speedups (STT-MRAM 8MB vs SRAM 2MB) ===")
    pairs = [
        ("O3 - bfs", "bfs_sram_2mb_7cy", "bfs_mram_8mb_14cy"),
        ("O3 - sssp", "sssp_sram_2mb_7cy", "sssp_mram_8mb_14cy"),
        ("In-Order - bfs", "inorder_bfs_sram_2mb_7cy", "inorder_bfs_mram_8mb_14cy"),
        ("In-Order - sssp", "inorder_sssp_sram_2mb_7cy", "inorder_sssp_mram_8mb_14cy"),
    ]

    for label, sram_tag, mram_tag in pairs:
        if sram_tag in results and mram_tag in results:
            sram_time = results[sram_tag]["sim_sec"]
            mram_time = results[mram_tag]["sim_sec"]
            if mram_time > 0:
                speedup = sram_time / mram_time
                diff_pct = (speedup - 1.0) * 100
                verdict = "MRAM WINS" if speedup > 1.0 else "SRAM WINS (MRAM LOSS)"
                print(f"  {label:<18}: {speedup:.4f}x ({diff_pct:+.2f}%) -> {verdict}")

if __name__ == "__main__":
    main()
