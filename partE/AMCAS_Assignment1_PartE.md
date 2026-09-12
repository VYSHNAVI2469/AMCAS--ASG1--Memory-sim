# AMCAS Assignment 1 — Part E: gem5 Full-System Simulation Report

**Course:** ECE2.414 — Advanced Memory Circuits and Systems  
**Instructor:** Dr. Priyesh Shukla · IIIT Hyderabad · Monsoon 2026  
**Topic:** Memory Simulation: From Devices to Systems (Part E — gem5)  
**Deliverable:** Full-System Performance Evaluation, Architectural Analysis & Final Design Decision  

---

## Overview & Simulation Methodology

The main architectural question addressed throughout this assignment is:

> **Should the 2 MB L2 cache in our accelerator use SRAM or STT-MRAM?**

The earlier tools in the simulation flow—ngspice, CACTI, NVSim, and Ramulator—focused on device behavior, memory-array organization, non-volatile switching characteristics, and DRAM scheduling. **gem5 completes this hierarchy by translating cache capacity and latency differences into processor cycles and actual application execution time.**

### Simulation Setup & Hierarchy Parameters

All experiments were performed using **native gem5 v24.0.0.0 (X86)** under WSL with Ubuntu Linux, GCC 13, and statically linked binaries.

- **Processor configurations evaluated:**
  - **Task 1:** Out-of-Order `DerivO3CPU`, 2.0 GHz, 8-wide issue, 192-entry ROB.
  - **Task 3:** In-Order `TimingSimpleCPU`, 2.0 GHz, single-issue pipeline.
- **L1 caches:** 32 kB, 8-way L1 Data Cache and 32 kB, 8-way L1 Instruction Cache, each with a 2-cycle hit latency.
- **L2 cache configurations:**
  - **Baseline SRAM (from CACTI Part B):** 2 MB, 8-way associative, **7-cycle hit latency**, corresponding to CACTI's 2.90 ns access time.
  - **STT-MRAM alternative (from NVSim Part C):** 8 MB, 8-way associative, **14-cycle hit latency**. The 8 MB cache occupies 11.11 mm², approximately matching the 11.47 mm² area of the 2 MB SRAM. This represents an approximately 2× hit-latency penalty.
- **Main memory:** DDR4-2400 8x8, 4 GB address space, single channel, dual rank.
- **Workloads:** GAP Benchmark Suite (GAPBS) using synthetic scale-18 Kronecker graphs:
  - `kron18.sg` for BFS
  - `kron18.wsg` for SSSP
  - Graph size: 262,143 vertices and 3,805,449 undirected edges.
- **Breadth-First Search (`bfs`):** 20,385,460 instructions were fast-forwarded through graph loading and Trial 1 warmup using `AtomicSimpleCPU`. Detailed simulation began at the Trial 2 boundary.
- **Single-Source Shortest Path (`sssp`):** 150,137,297 instructions were fast-forwarded through graph loading and Trial 1 warmup using `AtomicSimpleCPU`. Detailed simulation began at Trial 2.
- `m5.stats.reset()` was called when switching to the detailed CPU so that the reported statistics represent only the detailed kernel execution.

---

## Task 1: Out-of-Order Simulation Results (`DerivO3CPU`)

The cycle-accurate results obtained from the gem5 `stats.txt` files are summarized below.

### Table E1. Full-System Performance on Out-of-Order Core (`DerivO3CPU`)

| Kernel | L2 Cache Configuration | Capacity | Hit Latency | IPC | L2 Miss Rate | Simulated Time (simSeconds) | Total L2 Accesses | Avg L2 Miss Latency | Speedup (MRAM vs SRAM) |
|---|---|---|---|---|---|---|---|---|---|
| **bfs** | Baseline SRAM | 2 MB | 7 cy (3.5 ns) | **0.5266** | **0.6873 (68.73%)** | **0.015496 s** | 428,034 | 66.14 ns | Baseline (1.000×) |
| **bfs** | STT-MRAM Alternative | 8 MB | 14 cy (7.0 ns) | **0.7420** | **0.1822 (18.22%)** | **0.010998 s** | 424,650 | 71.89 ns | **1.4090× (+40.90%)** |
| **sssp** | Baseline SRAM | 2 MB | 7 cy (3.5 ns) | **0.4178** | **0.6052 (60.52%)** | **0.110702 s** | 3,293,898 | 72.29 ns | Baseline (1.000×) |
| **sssp** | STT-MRAM Alternative | 8 MB | 14 cy (7.0 ns) | **0.4469** | **0.4470 (44.70%)** | **0.103506 s** | 3,293,570 | 77.31 ns | **1.0695× (+6.95%)** |

---

## Task 2: Architectural Analysis of the Capacity–Latency Tradeoff

The key consequence of replacing SRAM with STT-MRAM at approximately the same silicon area is a trade between **greater cache capacity and higher hit latency**. The STT-MRAM cache is **4× larger (8 MB instead of 2 MB)**, but its assumed hit latency is **2× higher (14 cycles instead of 7 cycles)**.

### Which kernel benefits most from this tradeoff?

The benefit is particularly strong for **Breadth-First Search (`bfs`)**, where the end-to-end speedup reaches **1.4090× (+40.90%)**.

For **Single-Source Shortest Path (`sssp`)**, the improvement is much smaller, at **1.0695× (+6.95%)**.

### What workload characteristic explains the difference?

The major factor is whether the application's frequently reused working set falls between the capacities of the two caches, together with the balance between L2 hits and accesses that must go to DRAM.

### 1. Working-Set Behavior in BFS

- In the scale-18 BFS workload, the complete edge array is approximately 32 MB. It is streamed linearly once per level, providing spatial locality but little long-term temporal reuse. Therefore, neither a 2 MB nor an 8 MB L2 can contain the entire graph.
- The frequently accessed traversal metadata—such as the `parent` array (262,143 vertices × 4 B ≈ 1.05 MB), the approximately 32 kB visited bitmap, and frontier/queue buffers—requires roughly **2.2–3.5 MB**.
- With only 2 MB of SRAM, this hot working set repeatedly overflows the cache and causes substantial main-memory traffic, resulting in an **L2 miss rate of 68.73%**.
- Increasing the L2 capacity to 8 MB allows the important working set to remain on-chip. The miss rate therefore drops from **0.6873 to 0.1822**, a reduction of approximately **3.77×**.
- Avoiding more than 215,000 DRAM accesses is more valuable than the additional 7-cycle latency on L2 hits. A DRAM access costs roughly **140–160 CPU cycles (~70 ns)**, so the reduction in off-chip traffic dominates the hit-latency penalty.

### 2. Access Density and Reuse in SSSP

- The SSSP workload uses the Δ-stepping approach, which performs repeated priority-bucket relaxation and vertex-distance updates. It produces **3,293,898 L2 accesses**, around **7.7× the number of BFS accesses (428,034)**.
- The access pattern is more scattered and covers a larger effective footprint. As a result, increasing the cache from 2 MB to 8 MB reduces the miss rate only from **60.52% to 44.70%**, or approximately **1.35×**.
- SSSP also produces more than **1.82 million L2 hits**. Each of these hits experiences the additional 7-cycle latency of the assumed STT-MRAM cache.
- The latency cost accumulated across millions of hits therefore offsets much of the performance gained by avoiding DRAM misses. The final improvement is only **6.95%**.

### Architectural Takeaway

An equal-area increase in cache capacity is beneficial when the additional capacity eliminates a sufficiently large amount of expensive miss traffic compared with the number of cache hits that are exposed to the higher hit latency.

---

## Task 3: In-Order Core Comparison (`TimingSimpleCPU`)

To examine how processor microarchitecture affects the memory-hierarchy results, both workloads were rerun using the in-order `TimingSimpleCPU` while keeping the cache configurations unchanged.

### Table E2. In-Order Core Performance (`TimingSimpleCPU`)

| Kernel | L2 Cache Configuration | Capacity | Hit Latency | IPC | L2 Miss Rate | Simulated Time (simSeconds) | Speedup (MRAM vs SRAM) |
|---|---|---|---|---|---|---|---|
| **bfs** | Baseline SRAM | 2 MB | 7 cy | **0.1803** | **0.6895** | **0.045263 s** | Baseline (1.000×) |
| **bfs** | STT-MRAM Alternative | 8 MB | 14 cy | **0.2401** | **0.1586** | **0.033986 s** | **1.3318× (+33.18%)** |
| **sssp** | Baseline SRAM | 2 MB | 7 cy | **0.1505** | **0.6076** | **0.307957 s** | Baseline (1.000×) |
| **sssp** | STT-MRAM Alternative | 8 MB | 14 cy | **0.1601** | **0.4511** | **0.289435 s** | **1.0640× (+6.40%)** |

### How did Out-of-Order execution influence the Task 1 results?

The out-of-order processor was able to **hide a significant portion of the STT-MRAM hit-latency penalty while still taking advantage of the larger cache capacity**.

### 1. Latency Hiding Through Dynamic Scheduling

- `DerivO3CPU` uses a **192-entry Reorder Buffer (ROB)**, register renaming, and multiple MSHRs.
- When an L2 hit increases from 7 to 14 cycles, the scheduler can continue searching for independent arithmetic, address-generation, and non-blocking memory operations.
- Consequently, much of the additional 7-cycle latency can overlap with useful work instead of appearing directly as wall-clock delay.
- A DRAM miss is very different: with a roughly **140–180 cycle** memory delay, the ROB eventually fills and the processor stalls even with aggressive out-of-order execution. Therefore, reducing DRAM misses remains highly valuable.

### 2. Greater Latency Exposure on an In-Order Core

- `TimingSimpleCPU` does not have a ROB, out-of-order execution, or speculative issue.
- When a load encounters a dependency, the pipeline must wait for the memory operation to complete.
- Therefore, the additional 7 cycles of STT-MRAM hit latency are exposed more directly on the critical path.
- IPC decreases by roughly 3× compared with the OoO case, falling from about **0.53 to 0.18 for BFS**.
- The BFS MRAM speedup consequently decreases from **1.409× on the OoO core to 1.332× on the in-order core**.
- This demonstrates that the measured STT-MRAM advantage is influenced not only by the memory technology, but also by the processor's ability to hide memory latency.

---

## Task 4: Primary Deliverable

### (i) Final Recommendation & Overall Synthesis Across Parts A–E

Considering the complete simulation flow, the **2 MB SRAM L2 should be replaced with an 8 MB STT-MRAM cache when the accelerator mainly executes workloads with access patterns similar to graph traversal, particularly BFS, and uses an out-of-order processor**.

Part A, using ngspice, showed that the 45 nm bulk BSIM4 SRAM storage node remains physically stable at nominal \(V_{DD}\), while the sense margin decreases by **19.5% at 85 °C**. Part B, using CACTI, estimated the 2 MB SRAM cache area at **11.474 mm²** and reported substantial standby leakage of **2250.5 mW** across four UCA banks. Part C, using NVSim, showed that the **54 \(F^2\) 1T-1MTJ STT-MRAM cell** provides approximately **3.4× better area density than 6T SRAM**. This makes it possible to implement 8 MB of STT-MRAM in approximately **11.113 mm²**, which is close to the SRAM footprint, while reducing array-related leakage by **56% to 991 mW** (with the reported leakage originating from peripheral circuits). Part D, using Ramulator, indicated that a single DDR4-2400 channel with an FRFCFS scheduler is strongly limited by the data-bus cycle time \(t_{CCD}\), rather than activation timing, making the reduction of off-chip traffic particularly important. Finally, Part E demonstrated through gem5 full-system, cycle-accurate simulation that increasing the L2 capacity from 2 MB to 8 MB reduces the BFS L2 miss rate by approximately **3.77×**, from **68.7% to 18.2%**, and produces a **1.409× end-to-end performance improvement**.

The main limitation is STT-MRAM's asymmetric write behavior. Its reported **10.36 ns write latency** is about **3.91× slower than SRAM**, primarily due to the approximately 10 ns spin-transfer-torque switching pulse. For read-heavy accelerator applications such as graph search and neural-network inference, write buffering and MSHRs can help absorb much of this overhead, allowing the capacity advantage to remain dominant.

### (ii) Three Assumptions That Should Be Challenged by a Reviewer

A critical reviewer could question the following three assumptions in the methodology.

#### 1. Assumed 2× Hit-Latency Penalty (14 vs. 7 Cycles)

Part E assumes that the 8 MB STT-MRAM cache requires twice the hit latency of the 2 MB SRAM cache. However, the earlier physical modeling does not directly support this assumption. CACTI reports approximately **2.902 ns** access latency for the 2 MB SRAM, including about **0.85 ns** associated with H-tree routing across four UCA banks. NVSim, in contrast, estimates approximately **1.998 ns** access latency for the 8 MB STT-MRAM. The difference means that the 14-cycle STT-MRAM latency used in gem5 is primarily a pedagogical assumption rather than a direct physical result. A rigorous evaluation should model both memories with a common and consistent wire, routing, and cache-access methodology.

#### 2. Open-Loop DRAM Trace Replay Does Not Include Processor Feedback

In Part D, the L2 miss stream was replayed in Ramulator using an open-loop approach. Requests are generated without direct backpressure from processor stalls, dependencies, or the reorder buffer. In an actual processor, memory latency influences the rate at which new requests can be generated. Therefore, open-loop replay can artificially increase queue occupancy—reported at approximately **36–50 requests**—and may distort DRAM scheduler hit behavior. A stronger methodology would connect the DDR4 controller to gem5 so that requests and processor stalls interact in a closed-loop simulation.

#### 3. A Single Kronecker Graph Does Not Represent General Graph Workloads

The gem5 evaluation uses only one synthetic scale-18 Kronecker topology: `kron18.sg` / `kron18.wsg`, containing approximately **262k vertices and 3.8M edges**. Kronecker graphs have heavy-tailed degree distributions in which a relatively small number of hub vertices can generate a large fraction of accesses. Real-world sparse graphs—such as road networks, web graphs, and biological interaction networks—can have very different degree distributions, clustering, diameters, and working-set characteristics. Therefore, claiming a technology-wide advantage for STT-MRAM based on one synthetic graph may not generalize to workloads whose active data set does not fall between the 2 MB and 8 MB cache capacities.

---

## Final Verification Checklist

- [x] gem5 v24.0.0.0 was compiled and linked natively in WSL without compiler warnings or errors.
- [x] All 8 Part E full-system simulations completed successfully and their statistics were extracted.
- [x] **Task 1:** BFS and SSSP were evaluated on the O3 CPU, with IPC, miss rate, and simulation time reported.
- [x] **Task 2:** The working-set capacity effect and access-density differences were analyzed.
- [x] **Task 3:** BFS and SSSP were evaluated on the in-order CPU, including an explanation of OoO latency hiding.
- [x] **Task 4:** The final design recommendation and three major reviewer concerns were addressed.
- [x] No external code or text was intentionally copied; the reported numerical results are stated as being obtained from native execution.
