# AMCAS Assignment 1 — Part B: CACTI 7 Analysis

**Course:** ECE2.414 · Advanced Memory Circuits and Systems  
**Instructor:** Dr. Priyesh Shukla · IIIT Hyderabad · Monsoon 2026  
**Topic:** Part B — CACTI: Size the 2 MB SRAM L2  
**Simulator:** CACTI 7.0 (Uniform Cache Access SRAM Model)  
**Technology Node:** 45 nm Bulk CMOS (`itrs-hp`, $T = 350\text{ K}$)  
**Baseline Specification:** $2\text{ MB}$ Capacity, $64\text{ B}$ Line Size, $8$-Way Set-Associative, $4$ UCA Banks, $1$ R/W Port, $\text{ED}^2\text{P}$ Objective

---

## 1. Executive Summary and Main Question

> **Central Question:** *How fast, how big, and how leaky is a 2 MB SRAM L2 at 45 nm?*

### Numerical Baseline Results (Task 1):
* **How Fast (Latency):**
  * **Access Time ($T_{access}$):** **$2.9018\text{ ns}$** (corresponds to $\approx 6\text{–}7$ clock cycles on a $2.0\text{–}2.4\text{ GHz}$ core — this is the exact $L_2$ hit latency carried forward into gem5 in Part E!).
  * **Cycle Time ($T_{cycle}$):** **$2.6523\text{ ns}$** (maximum pipelined throughput of $\approx 377\text{ MHz}$).
* **How Big (Silicon Area):**
  * **Total Footprint:** **$11.474\text{ mm}^2$** ($2.213\text{ mm} \times 5.184\text{ mm}$).
  * **Data Array Area:** $10.271\text{ mm}^2$ (Area Efficiency = $54.33\%$).
  * **Tag Array Area:** $0.387\text{ mm}^2$ (Area Efficiency = $81.58\%$).
* **How Leaky (Power & Energy):**
  * **Leakage Power per Bank:** **$562.63\text{ mW}$** (at $T = 350\text{ K}$).
  * **Total 4-Bank Cache Leakage:** **$2250.53\text{ mW}$ ($2.25\text{ W}$)**.
  * **Gate Leakage Overhead:** $16.37\text{ mW}$ per bank ($65.46\text{ mW}$ total).
  * **Dynamic Read Energy:** **$792.89\text{ pJ}$** per access ($0.7929\text{ nJ}$).
  * **Dynamic Write Energy:** **$851.22\text{ pJ}$** per access ($0.8512\text{ nJ}$).

---

## 2. Quantitative Summary Tables

### Table B1: Baseline 2 MB SRAM L2 Metrics (Task 1 Deliverable)
*Carried forward into Part C (NVSim STT-MRAM comparison), Part D (Ramulator), and Part E (gem5).*

| Metric | CACTI 7 Value | Units | Description / System Significance |
| :--- | :---: | :---: | :--- |
| **Capacity** | $2097152$ | Bytes | $2\text{ MB}$ Total Data Storage |
| **Technology Node** | $45$ | nm | ITRS High-Performance Bulk Planar |
| **Operating Temperature** | $350$ | K | High-activity server die corner ($77\ ^\circ\text{C}$) |
| **Access Time** | **$2.9018$** | **ns** | L2 Hit Latency ($\approx 7$ cycles at $2.4\text{ GHz}$) |
| **Cycle Time** | **$2.6523$** | **ns** | Minimum burst access separation |
| **Dynamic Read Energy** | **$792.89$** | **pJ** | Energy dissipated per 64-byte read access |
| **Dynamic Write Energy** | **$851.22$** | **pJ** | Energy dissipated per 64-byte write access |
| **Leakage Power (1 Bank)**| **$562.63$** | **mW** | Standby dissipation per UCA bank |
| **Total Cache Leakage** | **$2250.53$** | **mW** | Total standby dissipation across all 4 banks ($2.25\text{ W}$) |
| **Total Cache Area** | **$11.474$** | **$\text{mm}^2$** | Macro footprint ($2.213\text{ mm} \times 5.184\text{ mm}$) |
| **Data Array Area** | **$10.271$** | $\text{mm}^2$ | Area allocated to data subarrays |
| **Data Area Efficiency**| **$54.33$** | % | Memory cell area / Total data array area |
| **Optimal Organization**| **$(4, 2, 1)$** | — | Winning $(N_{dwl}, N_{dbl}, N_{spd})$ data triple |

---

### Table B2: Capacity Scaling Sweep (Task 2 Deliverable)
*Capacity swept from $256\text{ kB}$ to $16\text{ MB}$ with associativity ($8$), block size ($64\text{ B}$), banks ($4$), and tech node ($45\text{ nm}$) held fixed.*

| Capacity | $\log_2(\text{Cap/kB})$ | Access Time (ns) | $\Delta T_{access}$ per doubling (ps) | Dyn Read Energy (pJ) | Bank Leakage (mW) | Area ($\text{mm}^2$) | Winning $(N_{dwl}, N_{dbl})$ |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **256 kB** | $8.0$ | **$2.4171$** | — | $658.02$ | $66.19$ | $4.965$ | $(4, 2)$ |
| **512 kB** | $9.0$ | **$2.4845$** | **$+67.4$** | $678.97$ | $133.15$ | $5.946$ | $(4, 2)$ |
| **1 MB** | $10.0$ | **$2.6338$** | **$+149.3$** | $716.64$ | $271.85$ | $7.600$ | $(4, 2)$ |
| **2 MB** | $11.0$ | **$2.9018$** | **$+268.0$** | $792.88$ | $562.63$ | $11.474$ | $(4, 2)$ |
| **4 MB** | $12.0$ | **$3.5308$** | **$+629.0$** | $930.13$ | $1131.75$ | $18.458$ | $(4, 2)$ |
| **8 MB** | $13.0$ | **$4.4727$** | **$+941.9$** | $1219.75$ | $2301.21$ | $39.496$ | $(4, 4)$ |
| **16 MB** | $14.0$ | **$6.3624$** | **$+1889.7$** | $1742.13$ | $4628.94$ | $74.668$ | $(2, 8)$ |

---

### Table B3: Objective Function Optimization Comparison (Task 3 Deliverable)

| Optimization Objective | Winning $(N_{dwl}, N_{dbl}, N_{spd})$ | Data Array Access Time (ns) | Dynamic Read Energy (nJ) | Data Array Area ($\text{mm}^2$) | Full Cache Access Time (ns) | Full Cache Area ($\text{mm}^2$) | Primary Architectural Trade-off |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Pure Delay** (`100:0:0:0:0`) | **$(4, 2, 1)$** | **$2.39947$** | $0.659797$ | $3.278$ | **$2.8923$** | $10.970$ | Aggressive wordline slicing minimizes RC line delays at higher energy. |
| **Pure Area** (`0:0:0:0:100`) | **$(2, 2, 1)$** | **$2.59376$** | $0.589994$ | **$2.8497$** | **$3.3552$** | **$9.245$** | Merges wordline partitions; cuts duplicate row decoders ($19.4\%$ area savings). |
| **$\text{ED}^2\text{P}$** (`-Optimize ED^2`) | **$(4, 2, 1)$** | **$2.41714$** | **$0.658021$** | $3.278$ | **$2.9018$** | $11.474$ | Heavily penalizes latency ($\text{Delay}^2$), retaining fast $(4,2,1)$ layout while tuning energy. |

*Note on Data-Array vs. Full-Cache metrics:* Pure delay and $\text{ED}^2\text{P}$ both choose $(4, 2, 1)$, whereas Pure Area chooses $(2, 2, 1)$. At the data array core level, Pure Delay achieves $2.3995\text{ ns}$ ($0.6598\text{ nJ}$), Pure Area cuts data array footprint to $2.8497\text{ mm}^2$ ($2.5938\text{ ns}$), and $\text{ED}^2\text{P}$ achieves $2.4171\text{ ns}$ with $0.6580\text{ nJ}$. Both perspectives confirm the exact same architectural trade-offs.

---

## 3. Detailed Task Results and Architectural Interpretation

### Task 1: Baseline CACTI Run and Subsystem Delay/Power Breakdown

From the detailed CACTI output for the $2\text{ MB}$ winner:
* **Critical Path Timing Breakdown ($T_{access} = 2.9018\text{ ns}$):**
  * **H-tree Address Input Network:** $0.8504\text{ ns}$ ($29.3\%$)
  * **Decoder + Wordline Delay:** $0.5408\text{ ns}$ ($18.6\%$)
  * **Bitline Discharge Delay:** $0.4069\text{ ns}$ ($14.0\%$)
  * **Sense Amplifier Latch Delay:** $0.0034\text{ ns}$ ($0.1\%$)
  * **H-tree Data Output Network:** $0.5051\text{ ns}$ ($17.4\%$)
  * *Global Interconnect Overhead:* The global H-tree wiring inside and outside the banks accounts for $0.8504 + 0.5051 = \mathbf{1.3555\text{ ns}}$ (**$46.7\%$ of total latency**).

---

### Task 2: Capacity Scaling & Amrutur–Horowitz "One Gate Delay per Doubling"

#### 1. Theory vs. CACTI Reality:
In their seminal work (*A Speed and Power Model for Submicron SRAMs*, IEEE JSSC 2000), Bharadwaj Amrutur and Mark Horowitz postulated that doubling cache capacity adds exactly one address bit to the address decoder, requiring roughly **one additional stage of logic (one FO4 inverter delay, $\approx 15\text{–}25\text{ ps}$ at $45\text{ nm}$)**.

#### 2. Analysis of the Observed Curve:
* **In the Small-Capacity Regime ($256\text{ kB} \rightarrow 512\text{ kB}$):**
  * $\Delta T_{access} = 2.4845 - 2.4171 = \mathbf{67.4\text{ ps}}$.
  * This is roughly $2\text{–}3$ FO4 gate delays, capturing the extra decoder logic stage plus minor local wiring. **Amrutur & Horowitz's rule of thumb is visible here as a lower bound.**
* **In the Large-Capacity Regime ($1\text{ MB} \rightarrow 16\text{ MB}$):**
  * The delay increment per doubling **accelerates exponentially**:
    $$67.4\text{ ps} \longrightarrow 149.3\text{ ps} \longrightarrow 268.0\text{ ps} \longrightarrow 629.0\text{ ps} \longrightarrow 941.9\text{ ps} \longrightarrow 1889.7\text{ ps}$$
  * Total access time nearly triples from $2.417\text{ ns} \rightarrow 6.362\text{ ns}$.
* **Physical explanation:** Cache die area scales from $4.965\text{ mm}^2$ up to $74.668\text{ mm}^2$ ($15\times$ increase). Wire flight distance across the H-tree scales as $L_{wire} \propto \sqrt{\text{Area}} \propto 2^{0.5 \log_2 C}$. While repeated wire delay scales linearly with length, the sheer physical distance across the $75\text{ mm}^2$ die introduces multi-nanosecond wire propagation delays that **completely overwhelm the constant gate-delay contribution**.

---

### Task 3: Objective Function Trade-offs ($N_{dwl}$, $N_{dbl}$, $N_{spd}$)

#### 1. Array Organization Definitions:
* $N_{dwl}$: Number of wordline segments (horizontal subarray slicing).
* $N_{dbl}$: Number of bitline segments (vertical subarray slicing).
* $N_{spd}$: Number of sets mapped to a single subarray column.

#### 2. Physical Explanation of the Organization Shift:
* **Pure Delay Winner $(4, 2, 1)$:**  
  Choosing $N_{dwl} = 4$ divides the wordlines into 4 short segments. Wordline RC delay scales quadratically with length ($\tau_{wl} \propto R_{wl} C_{wl} L_{wl}^2$). Slicing the wordline reduces line resistance and capacitance by $2\times$, providing the fastest row activation ($2.892\text{ ns}$). In contrast, $N_{dwl} = 4$ requires 4 duplicate sets of row decoders and wordline drivers, driving dynamic read energy up to $898.45\text{ pJ}$.
* **Pure Area Winner $(2, 2, 1)$:**  
  Area optimization consolidates the subarrays by reducing $N_{dwl}$ from 4 to 2. This removes half of the row predecoders and driver strips, increasing area efficiency and cutting macro footprint from $11.474\text{ mm}^2$ to **$9.245\text{ mm}^2$ (a $19.4\%$ area reduction)**. The penalty is longer wordlines, which slows down access time to $3.355\text{ ns}$ ($+16\%$ delay).
* **$\text{ED}^2\text{P}$ Winner $(4, 2, 1)$:**  
  Since the metric squares delay ($\text{Energy} \times \text{Delay}^2$), any degradation in latency is heavily penalized. As a result, the optimizer retains the fast $N_{dwl} = 4$ wordline division ($2.9018\text{ ns}$) while choosing optimal multiplexing and sense-amplifier isolation to minimize active column switching, yielding the lowest read energy ($792.88\text{ pJ}$).

---

### Task 4: Comparing the Hand-Calculated and CACTI Bitline Delay

#### 1. Hand Calculation Using Lecture 4 Elmore Wire Model:
From Lecture 4 (Slide 8), the distributed Elmore delay of an unbuffered metal line is:
$$\tau_{wire} = 0.38 \cdot R_{wire} \cdot C_{wire} = 0.38 \cdot r \cdot c \cdot L^2$$

Using CACTI 7's 45 nm semi-global/local metal parameters:
* Subarray height (Bitline length $L_{BL}$): $H_{sub} = 0.336384\text{ mm} = 336.38\ \mu\text{m}$.
* Metal sheet resistance: $r \approx 0.18\ \Omega/\mu\text{m}$ ($R_{BL} \approx 60.5\ \Omega$).
* Wire capacitance: $c \approx 0.15\text{ fF}/\mu\text{m}$ ($C_{BL,metal} \approx 50.4\text{ fF}$).
* **Hand-Calculated Distributed Wire Delay:**
  $$\tau_{hand} = 0.38 \times (60.5\ \Omega) \times (50.4\text{ fF}) \approx \mathbf{1.16\text{ ps}}$$

#### 2. CACTI's Reported Bitline Delay:
$$\tau_{CACTI} = \mathbf{0.406901\text{ ns} = 406.9\text{ ps}}$$

#### 3. Discrepancy Analysis:
$$\text{Discrepancy} = \frac{\tau_{CACTI}}{\tau_{hand}} = \frac{406.9\text{ ps}}{1.16\text{ ps}} \approx \mathbf{350\times}$$

#### 4. Effects Modeled by CACTI that the Hand Calculation Ignores:
The large difference between the hand estimate and CACTI occurs because it models an **isolated metal wire driven by an ideal zero-impedance source**. In an actual implementation:
1. **Transistor ON-Resistance ($R_{cell}$ dominates!):** The bitline is discharged by tiny, minimum-sized NMOS transistors ($MA1$ and $MN2$) operating in series. The effective channel resistance is $R_{cell} = R_{pull\_down} + R_{access} \approx \mathbf{8\text{–}12\text{ k}\Omega}$. This driving resistance is **$>150\times$ larger than the metal wire resistance** ($R_{cell} \gg R_{wire}$).
2. **Access Transistor Junction Loading:** In CACTI, $C_{bl}$ is not just metal capacitance; it includes the parasitic drain junction capacitance ($C_{drain}$) of all 512 unselected access transistors connected to the column, which triples the effective capacitive load ($C_{total} \approx 180\text{ fF}$ vs $50\text{ fF}$ wire only).
3. **Peripheral & Multiplexer Loading:** CACTI incorporates the loading from bitline multiplexers, sense-amplifier isolation gates, and precharge circuitry ($C_{drain\_bit\_mux} + C_{sense\_amp\_latch}$).
4. **Small-Signal Sensing Threshold:** CACTI calculates the delay to discharge the bitline by $\Delta V_{sense} \approx 100\text{ mV}$ using:
   $$\tau = (R_{cell} + R_{wire}/2) C_{total}, \quad tstep = \tau \ln\left(\frac{V_{pre}}{V_{pre} - \Delta V_{sense}}\right)$$
   rather than a rail-to-rail $50\%$ step transition ($0.38 RC$).

---

## 4. Generated Files and Scripts

All Part B CACTI configuration files and generated output files are located in:
`/mnt/c/Users/lenovo/Downloads/AMCS/Memory-sim/partB/`

1. `cache.cfg` — Baseline CACTI configuration file.
2. `cache.cfg.out` — CACTI output generated from the baseline configuration.
3. `task3_delay.cfg` — Task 3 configuration for the delay-optimized design.
4. `task3_delay.cfg.out` — CACTI output for the delay-optimized configuration.
5. `task3_area.cfg` — Task 3 configuration for the area-optimized design.
6. `task3_area.cfg.out` — CACTI output for the area-optimized configuration.
7. `task3_ed2p.cfg` — Task 3 configuration for the ED²P-optimized design.
8. `task3_ed2p.cfg.out` — CACTI output for the ED²P-optimized configuration.
9. `task4.cfg` — Task 4 configuration used for the bitline-delay analysis.
10. `task4.cfg.out` — CACTI output generated for Task 4.

The files can be accessed from the WSL Ubuntu terminal using:
`cd /mnt/c/Users/lenovo/Downloads/AMCS/Memory-sim/partB`
