#!/usr/bin/env bash
set -euo pipefail

# Directory paths
AMCAS_BUILD="/root/amcas_build"
GEM5="$AMCAS_BUILD/gem5/build/X86/gem5.opt"
SE_SCRIPT="$AMCAS_BUILD/gem5/configs/deprecated/example/se.py"
GAPBS="$AMCAS_BUILD/gapbs"
FAST_RUNS_DIR="$AMCAS_BUILD/runs"
WINDOWS_OUTPUT_DIR="/mnt/c/Users/lenovo/Downloads/AMCS/Memsim-stack/partE/runs"

mkdir -p "$FAST_RUNS_DIR"
mkdir -p "$WINDOWS_OUTPUT_DIR"

echo "=== AMCAS Part E Simulation Runner ==="
echo "gem5 binary: $GEM5"
echo "GAPBS directory: $GAPBS"
echo "Fast ext4 Run dir: $FAST_RUNS_DIR"
echo "Windows Output dir: $WINDOWS_OUTPUT_DIR"
date

# Fast-forward instruction counts (measured in atomic mode for trial 1 warm-up)
FF_BFS=20385460
FF_SSSP=150137297

GRAPH_BFS="$GAPBS/graphs/kron18.sg"
GRAPH_SSSP="$GAPBS/graphs/kron18.wsg"

run_simulation() {
    local tag=$1
    local kernel=$2
    local l2_size=$3
    local hit_lat=$4
    local cpu=$5
    local ff_insts=$6
    local graph=$7

    local outdir="$FAST_RUNS_DIR/$tag"
    mkdir -p "$outdir"

    echo "[$(date +'%H:%M:%S')] Starting: $tag ($kernel | $cpu | L2: $l2_size @ ${hit_lat}cy)"
    
    $GEM5 --outdir="$outdir" \
        "$SE_SCRIPT" \
        --cpu-type="$cpu" --caches --l2cache \
        --l1d_size=32kB --l1i_size=32kB --l1d_assoc=8 --l1i_assoc=8 \
        --l2_size="$l2_size" --l2_assoc=8 --l2-hit-latency="$hit_lat" \
        --mem-type=DDR4_2400_8x8 --mem-size=4GB \
        --fast-forward="$ff_insts" \
        --cmd="$GAPBS/$kernel" --options="-f $graph -n 2" \
        > "$outdir/run.log" 2>&1

    echo "[$(date +'%H:%M:%S')] COMPLETED: $tag"
    # Mirror results to Windows directory
    mkdir -p "$WINDOWS_OUTPUT_DIR/$tag"
    cp -rf "$outdir/"* "$WINDOWS_OUTPUT_DIR/$tag/" 2>/dev/null || true
}

echo "=========================================================================="
echo "--- TASK 1: Out-of-Order CPU (DerivO3CPU) - BFS ---"
echo "=========================================================================="
run_simulation "bfs_sram_2mb_7cy" "bfs" "2MB" "7" "DerivO3CPU" "$FF_BFS" "$GRAPH_BFS" &
run_simulation "bfs_mram_8mb_14cy" "bfs" "8MB" "14" "DerivO3CPU" "$FF_BFS" "$GRAPH_BFS" &
wait
echo "--> Completed Task 1 BFS pair."
python3 /mnt/c/Users/Viswas/OneDrive/Desktop/4_1/AMCAS/assignment1_work/part_e/extract_gem5_stats.py "$FAST_RUNS_DIR"

echo "=========================================================================="
echo "--- TASK 1: Out-of-Order CPU (DerivO3CPU) - SSSP ---"
echo "=========================================================================="
run_simulation "sssp_sram_2mb_7cy" "sssp" "2MB" "7" "DerivO3CPU" "$FF_SSSP" "$GRAPH_SSSP" &
run_simulation "sssp_mram_8mb_14cy" "sssp" "8MB" "14" "DerivO3CPU" "$FF_SSSP" "$GRAPH_SSSP" &
wait
echo "--> Completed Task 1 SSSP pair."
python3 /mnt/c/Users/Viswas/OneDrive/Desktop/4_1/AMCAS/assignment1_work/part_e/extract_gem5_stats.py "$FAST_RUNS_DIR"

echo "=========================================================================="
echo "--- TASK 3: In-Order CPU (TimingSimpleCPU) - BFS ---"
echo "=========================================================================="
run_simulation "inorder_bfs_sram_2mb_7cy" "bfs" "2MB" "7" "TimingSimpleCPU" "$FF_BFS" "$GRAPH_BFS" &
run_simulation "inorder_bfs_mram_8mb_14cy" "bfs" "8MB" "14" "TimingSimpleCPU" "$FF_BFS" "$GRAPH_BFS" &
wait
echo "--> Completed Task 3 In-Order BFS pair."
python3 /mnt/c/Users/Viswas/OneDrive/Desktop/4_1/AMCAS/assignment1_work/part_e/extract_gem5_stats.py "$FAST_RUNS_DIR"

echo "=========================================================================="
echo "--- TASK 3: In-Order CPU (TimingSimpleCPU) - SSSP ---"
echo "=========================================================================="
run_simulation "inorder_sssp_sram_2mb_7cy" "sssp" "2MB" "7" "TimingSimpleCPU" "$FF_SSSP" "$GRAPH_SSSP" &
run_simulation "inorder_sssp_mram_8mb_14cy" "sssp" "8MB" "14" "TimingSimpleCPU" "$FF_SSSP" "$GRAPH_SSSP" &
wait
echo "--> Completed Task 3 In-Order SSSP pair."

echo ""
echo "=========================================================================="
echo "=== All 8 Part E Simulations Finished Successfully! Final Summary: ==="
echo "=========================================================================="
python3 /mnt/c/Users/Viswas/OneDrive/Desktop/4_1/AMCAS/assignment1_work/part_e/extract_gem5_stats.py "$FAST_RUNS_DIR"

# Final sync to Windows
cp -rf "$FAST_RUNS_DIR/"* "$WINDOWS_OUTPUT_DIR/" 2>/dev/null || true
echo "All statistics synced to $WINDOWS_OUTPUT_DIR"
