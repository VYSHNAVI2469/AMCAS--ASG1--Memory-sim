# AMCAS Assignment 1 — Memory Circuits & Systems: From Devices to Systems

**Course:** ECE2.414 · Advanced Memory Circuits and Systems
**Instructor:** Dr. Priyesh Shukla · IIIT Hyderabad · Monsoon 2026
**Central Question:** *Should the 2 MB L2 cache in our accelerator use SRAM or STT-MRAM?*

This assignment walks the same 2 MB L2 cache design question through five simulation tools, each operating at a different level of abstraction — from transistor-level SPICE decks up to full-system, cycle-accurate execution:

| Part | Tool | Abstraction Level | What It Answers |
|---|---|---|---|
| **A** | ngspice | Device / transistor | Does the 6T SRAM bitcell read correctly, and with how much margin? |
| **B** | CACTI 7.0 | Array / circuit | How fast, how big, and how leaky is a 2 MB SRAM L2 at 45 nm? |
| **C** | NVSim | Array / circuit (NVM) | How does a 1T-1MTJ STT-MRAM array compare to the SRAM baseline? |
| **D** | Ramulator | DRAM subsystem | How does the L2 miss stream behave on a real DDR4 channel? |
| **E** | gem5 | Full system | Does the SRAM-vs-STT-MRAM trade-off actually change application performance? |

---

## Repository Structure

```
.
├── assets/                     # Terminal/plot screenshots referenced below
├── partA_ngspice.md            # 6T SRAM read-margin analysis
├── partB_cacti.md              # 2 MB SRAM sizing, sweeps, ED²P study
├── partC_nvsim.md              # STT-MRAM array comparison
├── partD_ramulator.md          # DDR4 trace-driven DRAM analysis
├── partE_gem5.md               # Full-system BFS/SSSP evaluation & final recommendation
└── README.md                   # This file
```

---

## Part A — ngspice: 6T SRAM Read Margin (45 nm Bulk CMOS, PTM BSIM4)

**Question answered:** *Does the SRAM bitcell continue to read correctly at 0.7 V and 85 °C?*

**Bottom line:** Yes at the nominal cell sizing — the cell reads correctly at every corner tested, but the margin shrinks substantially as supply voltage drops and temperature rises. A wider access transistor (lower cell ratio) creates a much larger read disturbance and pushes the design toward a real read-upset risk.

| Task | Configuration | Cell Ratio β_r | V_DD (V) | Temp (°C) | ΔV(BLB,BL) @ 2 ns | v(q)_max | Result |
|---|---|---|---|---|---|---|---|
| 1 | Baseline read | 1.25 | 1.10 | 27 | **729.86 mV** | 205.52 mV | Pass — clean active discharge |
| 2 | Wide access Tx (W=0.24 µm) | **0.833** | 1.10 | 27 | 695.14 mV | **272.00 mV** | Severe read disturbance |
| 3 | V_DD sweep, C_BL = 1 pF | 1.25 | 1.10 → 0.60 | 27 | 143.6 → 26.9 mV | — | Fails sense margin below **≈0.59 V** |
| 4 | High-temp corner | 1.25 | 1.10 | **85** | 582.11 mV (−20.2%) | 220.76 mV (+7.4%) | Pass, but margin erodes |

**Key figures (see `assets/`):**
- `image5.png` — Task 1/2 bitline differential transient (W = 0.16 µm vs 0.24 µm access transistors)
- `image6.png` — Storage-node read disturbance v(q)
- `image7.png` — ΔV vs V_DD sweep (1.1 V → 0.6 V, 50 mV steps)
- `image8.png` — 85 °C read transient

**Takeaways:**
1. The 6T cell's *active* discharge produces a bitline swing ~10× larger than a DRAM 1T1C cell's passive charge-sharing signal (69 mV reference) at the same time point — SRAM sensing can fire much earlier.
2. Cell ratio β_r < 1 (oversized access transistor) is the classic read-upset failure mode: the storage-node bump consumes >60% of the inverter trip margin.
3. At low V_DD, the limiting factor is the **sense-amplifier offset (25 mV)**, not raw bitcell discharge speed — reliable sensing is lost below ≈0.59 V.
4. At 85 °C, degraded carrier mobility shrinks ΔV by ~20%, and temperature-dependent sense-amp offset (plus subthreshold leakage from unselected cells) — not the raw discharge — sets the practical read-failure boundary.

*(The same docx also includes an earlier DRAM 1T1C retention-time exercise — V_PP sweep, log I_D–V_GS subthreshold-swing extraction, and droop-rate extrapolation to a 200 mV retention limit at 27 °C vs 85 °C — captured in `image1.png`–`image4.png` for reference.)*

---

## Part B — CACTI 7.0: Sizing the 2 MB SRAM L2 (45 nm, ED²P objective)

**Question answered:** *How fast, how big, and how leaky is a 2 MB SRAM L2 at 45 nm?*

### Baseline result (Task 1)

| Metric | Value |
|---|---|
| Access time | **2.9018 ns** (≈7 cycles @ 2.4 GHz) |
| Cycle time | 2.6523 ns (≈377 MHz) |
| Total area | **11.474 mm²** (2.213 mm × 5.184 mm) |
| Dynamic read energy | 792.89 pJ/access |
| Dynamic write energy | 851.22 pJ/access |
| Leakage / bank | 562.63 mW → **2.25 W total** (4 banks) |
| Winning organization | (N_dwl, N_dbl, N_spd) = (4, 2, 1) |

*Critical path: 46.7% of latency (1.36 ns) is H-tree address/data routing overhead — decoder+wordline (18.6%), bitline discharge (14.0%), sense-amp (0.1%).*

**Figure:** `image9.png` — raw CACTI baseline output.

### Capacity sweep (Task 2): 256 kB → 16 MB

Access time nearly triples (2.42 ns → 6.36 ns) as capacity scales 64×. In the small-capacity regime (256 kB→512 kB, +67.4 ps) the delay increment matches Amrutur & Horowitz's "one gate delay per doubling" rule; beyond ~1 MB the per-doubling delay **accelerates** (+149 ps → +1890 ps) because H-tree wire flight distance (∝√Area) starts to dominate over constant gate delay.

**Figure:** `image10.png` — access time vs log₂(capacity).

### Objective-function comparison (Task 3): Pure Delay vs Pure Area vs ED²P

| Objective | (N_dwl, N_dbl, N_spd) | Access time | Read energy | Area |
|---|---|---|---|---|
| Pure Delay | (4, 2, 1) | 2.399 ns | 0.660 nJ | 3.278 mm² (data array) |
| Pure Area | **(2, 2, 1)** | 2.594 ns | 0.590 nJ | **2.850 mm²** (−19.4%) |
| ED²P | (4, 2, 1) | 2.417 ns | 0.658 nJ | 3.278 mm² |

Pure Delay and ED²P agree on (4,2,1) because ED²P's Delay² term heavily penalizes latency; Pure Area trades wordline length (and thus delay) for fewer duplicated row decoders.

**Figures:** `image11.png`–`image16.png` — CACTI outputs for the pure-delay, pure-area, and ED²P runs (two views each).

### Hand-calculated vs CACTI bitline delay (Task 4)

Elmore-model hand calculation (0.38·R·C·L²) gives ≈1.16 ps; CACTI reports **406.9 ps** — a ~350× discrepancy. The gap comes from effects the hand model ignores: the access-transistor's ON-resistance (8–12 kΩ, ≫ metal R), junction capacitance from ~512 unselected cells on the column, mux/sense-amp/precharge loading, and the fact that CACTI solves for a small-signal sense threshold (ΔV≈100 mV) rather than a rail-to-rail 50% step.

**Figures:** `image17.png`, `image18.png`.

---

## Part C — NVSim: STT-MRAM Array Comparison

**Question answered:** *How does a 2 MB 1T-1MTJ STT-MRAM array compare to the CACTI SRAM baseline, and what does the MTJ's TMR ratio actually buy at the array level?*

### Task 1 — Baseline STT-MRAM vs SRAM baseline (2 MB, 8-way, 64 B line)

MTJ cell: 54 F² area, aspect ratio 2.0, R_on = 3 kΩ / R_off = 6 kΩ (TMR 2:1), read current 40 µA, set/reset current 200 µA with a 10 ns pulse.

| Metric | STT-MRAM (NVSim) | SRAM (CACTI, Part B) |
|---|---|---|
| Total area | **3.590 mm²** | 11.474 mm² (per 2 MB — SRAM shown at same capacity) |
| Read (hit) latency | **1.589 ns** | 2.902 ns |
| Write latency | **10.608 ns** | ≈2.6 ns (cycle time) |
| Read dynamic energy | 0.760 nJ/access | 0.793 nJ/access |
| Write dynamic energy | 0.531 nJ/access | 0.851 nJ/access |
| Total leakage power | **425.2 mW** | 2250.5 mW (4 banks) |

**Figures:** `image19.png`–`image22.png` — NVSim summary, data-array, and tag-array breakdowns.

**Task 2 — Which metrics flip, and why (device-level reasoning):**
- **Dramatically better:** *Area* (~3.2× denser — the 1T-1MTJ cell needs one access transistor instead of six) and *leakage power* (~5.3× lower — MTJs are non-volatile, so standby state costs no static current; leakage here is almost entirely peripheral CMOS, not the storage element).
- **Dramatically worse:** *Write latency* (10.6 ns vs ~2.6 ns) and, implicitly, write energy/current — because writing an MTJ requires a sustained spin-transfer-torque current pulse (10 ns, 200 µA) to switch the free layer's magnetization, versus simply overpowering a bistable 6T latch, which SRAM does in one cycle.

**Task 3 — Re-run with R_on = 4 kΩ / R_off = 12 kΩ (TMR 3:1):**

| Metric | Baseline (TMR 2:1) | Re-run (TMR 3:1) | Δ |
|---|---|---|---|
| Total area | 3.590 mm² | 3.580 mm² | −0.3% |
| Read (hit) latency | 1.589 ns | 1.594 ns | +0.3% |
| Write latency | 10.608 ns | 10.657 ns | +0.5% |
| Read dynamic energy | 0.760 nJ | 0.758 nJ | −0.3% |
| Write dynamic energy | 0.531 nJ | 0.529 nJ | −0.4% |
| Leakage power | 425.227 mW | 425.227 mW | 0% |

**Figures:** `image23.png`–`image25.png`.

Almost nothing moves. Doubling the resistance pair (and keeping the 2:1→3:1 TMR ratio change) barely touches NVSim's reported array-level numbers, because NVSim's array timing/energy model is driven mainly by the read/reset/set *currents* and *pulse widths* set in the cell config, not directly by the absolute resistance values — TMR affects the achievable read *sensing margin* (bit-error rate under process/noise variation), which is a reliability metric NVSim's default array-level report doesn't surface. In other words, a device paper's headline TMR number buys you sensing margin and yield, not a faster or smaller array by itself; it only shows up at the array level once it is translated into a sense-amp design point (offset, timing, or supply headroom).

**Task 4 — Halve ResetCurrent to 100 µA:** the single most important coupling in NVM array design is that **write (reset/set) current sets the access-transistor width**, because the access device must be sized to pass that current without violating its own compliance/resistance limits. Halving ResetCurrent lets the access transistor shrink, which directly shrinks the 1T-1MTJ cell area — i.e., **write-current specification is an area lever**, not just a power/latency one, unlike in SRAM where cell area is essentially fixed by the 6T ratio constraints.

---

## Part D — Ramulator: DDR4-2400 Trace-Driven DRAM Analysis

**Question answered:** *Once requests miss the L2, how does a real DDR4 channel behave, and what limits its throughput?*

- **Configuration:** Single-channel DDR4-2400 8×8, FR-FCFS scheduler, L2-miss address trace replayed open-loop (no processor feedback).
- **Key finding:** the channel is **bandwidth/t_CCD-limited** — bounded by the data-bus burst cycle time rather than by row-activation (t_RCD/t_RAS) timing — so reducing the *number* of L2 misses (not just their individual latency) is what matters most for end-to-end throughput.
- **Queue occupancy:** the request queue in the open-loop replay sits around **36–50 requests**, reflecting the fact that misses are injected without waiting on processor backpressure.
- **Methodological caveat carried into Part E:** because the replay is open-loop, it can overstate queue occupancy and understate the benefit of any latency-hiding the real processor would otherwise provide — this is one of the assumptions flagged for review in Part E.

> This section summarizes the figures Part E cross-references from the Ramulator run; the full Ramulator sweep tables/configs were not available to fold into this README (`assignment1_partD.md` did not come through in the upload) — happy to merge them in once you re-share that file or its scfg/output logs.

---

## Part E — gem5: Full-System Evaluation (BFS & SSSP, GAP Benchmark Suite)

**Question answered:** *Does swapping the 2 MB SRAM L2 for an (area-matched) 8 MB STT-MRAM L2 actually help real application performance?*

**Setup:** `DerivO3CPU` (OoO, 2.0 GHz, 8-wide, 192-entry ROB) and `TimingSimpleCPU` (in-order), 32 kB 8-way L1 I/D ($2$-cycle hit), DDR4-2400 main memory, scale-18 Kronecker graphs (262,143 vertices / 3,805,449 edges) for BFS and SSSP.

| Config | Capacity | Hit latency | (from) |
|---|---|---|---|
| Baseline SRAM | 2 MB | 7 cy (3.5 ns) | CACTI, Part B |
| STT-MRAM alt. | 8 MB | 14 cy (7.0 ns) | NVSim, Part C — 8 MB STT-MRAM ≈ 11.11 mm², matching the 11.47 mm² SRAM footprint |

### Out-of-order core (Task 1)

| Kernel | Config | IPC | L2 Miss Rate | Sim Time | Speedup |
|---|---|---|---|---|---|
| bfs | SRAM 2 MB | 0.5266 | 68.73% | 0.015496 s | 1.000× |
| bfs | STT-MRAM 8 MB | 0.7420 | 18.22% | 0.010998 s | **1.409× (+40.9%)** |
| sssp | SRAM 2 MB | 0.4178 | 60.52% | 0.110702 s | 1.000× |
| sssp | STT-MRAM 8 MB | 0.4469 | 44.70% | 0.103506 s | **1.070× (+6.95%)** |

**Why BFS benefits far more than SSSP:** BFS's hot working set (parent array + visited bitmap + frontier buffers, ≈2.2–3.5 MB) just barely overflows 2 MB but fits comfortably in 8 MB, so miss rate drops 3.77× (68.7%→18.2%) and each avoided DRAM miss (~140–160 cycles) vastly outweighs the extra 7-cycle hit penalty. SSSP's Δ-stepping access pattern is far more scattered (7.7× more L2 accesses than BFS) and its footprint doesn't fit any better in 8 MB than in 2 MB, so the miss-rate improvement is smaller (1.35×) while >1.8M L2 *hits* now each pay the extra latency — largely cancelling the DRAM-miss savings.

### In-order core (Task 3) — does OoO scheduling change the story?

| Kernel | Config | IPC | Miss Rate | Sim Time | Speedup |
|---|---|---|---|---|---|
| bfs | SRAM | 0.1803 | 68.95% | 0.045263 s | 1.000× |
| bfs | STT-MRAM | 0.2401 | 15.86% | 0.033986 s | 1.332× (+33.2%) |
| sssp | SRAM | 0.1505 | 60.76% | 0.307957 s | 1.000× |
| sssp | STT-MRAM | 0.1601 | 45.11% | 0.289435 s | 1.064× (+6.4%) |

The 192-entry ROB in `DerivO3CPU` overlaps much of the extra 7-cycle STT-MRAM hit latency with independent work, so BFS's speedup is even larger under OoO (1.409×) than in-order (1.332×) — OoO hides *hit* latency but cannot hide the ~140–180 cycle DRAM-*miss* latency, which is why avoiding misses stays valuable either way.

### Final recommendation

Adopt the **8 MB STT-MRAM L2** for accelerator workloads whose access pattern resembles graph traversal (BFS-like), especially on an OoO core — the capacity win from eliminating DRAM misses dominates the write-latency and per-hit latency penalties. STT-MRAM's ~10.4 ns write latency (≈3.9× slower than SRAM) is the main risk and should be masked with write buffering/MSHRs for read-heavy workloads.

**Three assumptions a reviewer should challenge:**
1. The **2× hit-latency assumption** (14 vs. 7 cycles) is a pedagogical simplification — CACTI's 2.902 ns SRAM access and NVSim's 1.998 ns 8 MB STT-MRAM read latency don't actually support a clean 2× ratio when modeled consistently.
2. **Open-loop Ramulator replay** (Part D) has no processor backpressure, which can distort queue occupancy (36–50 requests) and over/under-state the real memory-latency-hiding available on a real core.
3. **A single synthetic Kronecker graph** (heavy-tailed degree distribution) may not generalize to real-world sparse graphs with different locality/working-set characteristics.

---

## Tool Chain / Reproduction Notes

- **ngspice:** PTM BSIM4 45 nm bulk model card, `question2.cir` netlist, transient + `.control` sweeps.
- **CACTI 7.0:** `itrs-hp` 45 nm library, T = 350 K, UCA model, configs in `partB/*.cfg`.
- **NVSim:** shipped STT-MRAM cell config (`STT_cache.cfg`), current-sensing read, current-mode set/reset.
- **Ramulator:** DDR4-2400 8×8 config, FR-FCFS scheduler, L2-miss trace replay.
- **gem5 v24.0.0.0 (X86):** `DerivO3CPU` / `TimingSimpleCPU`, GAPBS `bfs`/`sssp` on scale-18 Kronecker graphs, fast-forwarded with `AtomicSimpleCPU` then switched to the detailed CPU with `m5.stats.reset()`.

All raw CACTI/NVSim terminal outputs referenced above are captured as screenshots in `assets/` (`image1.png`–`image25.png`).
