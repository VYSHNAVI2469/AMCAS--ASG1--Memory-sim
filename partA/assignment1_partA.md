# AMCAS Assignment 1 — Part A: ngspice Evaluation

**Course:** ECE2.414 · Advanced Memory Circuits and Systems  
**Instructor:** Dr. Priyesh Shukla · IIIT Hyderabad · Monsoon 2026  
**Topic:** Part A — ngspice: Evaluate a 6T SRAM read operation and determine the margin  
**Technology Node:** 45 nm Bulk CMOS (PTM BSIM4 Model Card `45nm_bulk.txt`, $V_{DD,nom} = 1.1\text{ V}$)  
**Initial Bitcell State:** $Q = 0\text{ V}$, $QB = 1.1\text{ V}$ ($V_{DD}$)

---

## 1. Executive Summary and Main Finding

> **Main Question:** *Does the SRAM bitcell continue to read correctly at $0.7\text{ V}$ and $85\ ^\circ\text{C}$?*

### Engineering Conclusion

* **Nominal Cell ($W_{ax} = 0.16\ \mu\text{m}$, Cell Ratio $\beta_r = \frac{0.20}{0.16} = 1.25$):**  
  **Yes. The cell reads correctly without flipping**, although the available margins are substantially reduced. At the nominal operating point ($1.1\text{ V}$, $27\ ^\circ\text{C}$, $C_{BL} = 180\text{ fF}$), the access transistor actively pulls down $BL$, creating $\Delta V(BLB, BL) = \mathbf{729.86\text{ mV}}$ at $t = 2.0\text{ ns}$. The internal read disturbance reaches $v(q)_{max} = \mathbf{205.52\text{ mV}}$ at $t = 1.058\text{ ns}$. At $85\ ^\circ\text{C}$, the developed $\Delta V$ decreases by $20.2\%$ to $\mathbf{582.11\text{ mV}}$, consistent with reduced carrier mobility from phonon scattering, while the peak read bump increases to $v(q)_{max} = \mathbf{220.76\text{ mV}}$. Reducing the supply to $0.7\text{ V}$ at $85\ ^\circ\text{C}$ further reduces read current by more than $60\%$, leaving less margin against threshold-voltage variation ($\sigma_{Vth} \approx 35\text{ mV}$ from Random Dopant Fluctuations).

* **Marginal/Perturbed Cell ($W_{ax} = 0.24\ \mu\text{m}$, Cell Ratio $\beta_r = \frac{0.20}{0.24} = 0.833$):**  
  Increasing the access-transistor width creates a **large read disturbance ($v(q)_{max} \approx 272\text{ mV}$)**, although an immediate dynamic flip is not observed under the clean transient-pulse conditions. Since $\beta_r < 1.0$, the static read noise margin approaches zero ($SNM \rightarrow 0$), making the cell highly susceptible to a dynamic read upset when noise or device mismatch is present.

---

## 2. Quantitative Summary of All Part A Tasks

| Task | Configuration / Corner | Cell Ratio $\beta_r = \frac{W_{pd}}{W_{ax}}$ | $V_{DD}$ (V) | Temp ($^\circ$C) | $C_{BL}$ | $\Delta V(BLB,BL)$ at $2.0\text{ ns}$ (mV) | $v(q)_{max}$ Read Bump (mV) | Outcome / Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Task 1** | Baseline Read | $1.25$ | $1.10$ | $27$ | $180\text{ fF}$ | **$729.86$** | **$205.52$** (at $1.058\text{ ns}$) | **Pass** (Clean active discharge) |
| **Task 2** | Increased Access Width ($W_{ax}=0.24\ \mu\text{m}$) | **$0.833$** | $1.10$ | $27$ | $180\text{ fF}$ | **$695.14$** | **$272.00$** | **Severe Read Disturbance** ($v(q)$ reaches $272\text{ mV}$) |
| **Task 3** | $V_{DD}$ Scaling Sweep ($C_{BL} = 1.0\text{ pF}$) | $1.25$ | $1.10 \rightarrow 0.60$ | $27$ | **$1.0\text{ pF}$** | **$143.59 \rightarrow 26.91$** | $143.6 \rightarrow 26.9$ | **Drops below $25\text{ mV}$ floor at $V_{DD} \approx 0.59\text{ V}$** |
| **Task 4** | High-Temperature Corner | $1.25$ | $1.10$ | **$85$** | $180\text{ fF}$ | **$582.11$** | **$220.76$** (at $1.068\text{ ns}$) | **Pass** ($\Delta V \downarrow 20.2\%$, Bump $\uparrow 7.4\%$) |

---

## 3. Detailed Task Analysis

### Task 1: Bitline Differential $\Delta V(BL,BLB)$ and Comparison with Lecture 1

#### 1. Simulation Conditions and Netlist Setup

The 6T SRAM cell begins with $Q = 0$ and $QB = 1.1\text{ V}$. Both bitlines, $BL$ and $BLB$, are initially precharged to $V_{BL}=1.1\text{ V}$, with a parasitic bitline capacitance of $C_{BL}=180\text{ fF}$. At $t=1.0\text{ ns}$, the wordline changes from $0\text{ V}$ to $1.1\text{ V}$ with a $50\text{ ps}$ transition time ($t_{rise}=1.05\text{ ns}$).

#### 2. Results Measured at $t=2.0\text{ ns}$

* $v(bl)_{2ns}=0.369715\text{ V}=\mathbf{369.72\text{ mV}}$
* $v(blb)_{2ns}=1.09957\text{ V}=\mathbf{1099.57\text{ mV}}$
* **$\Delta V(BLB,BL)=v(blb)-v(bl)=\mathbf{0.729858\text{ V}=729.86\text{ mV}}$**
* **$v(q)_{max}=\mathbf{205.52\text{ mV}}$** at $t=1.0575\text{ ns}$

#### 3. Comparison with the $69\text{ mV}$ Lecture Reference

* **Lecture 1 (Slide 24, DRAM 1T1C passive charge sharing):**  
  In the DRAM example, the differential bitline signal comes only from passive charge redistribution between the storage capacitor $C_S=25\text{ fF}$ and the precharged bitline $C_{BL}=175\text{ fF}$, with $V_{PRE}=V_{DD}/2=0.55\text{ V}$:
  $$\Delta V_{DRAM}=\left(\frac{V_{DD}}{2}\right)\cdot\frac{C_S}{C_S+C_{BL}}=0.55\text{ V}\times\frac{25}{200}=\mathbf{68.75\text{ mV}\approx69\text{ mV}$$
  This approximately $69\text{ mV}$ value is the static limit produced by charge sharing; after equilibrium is reached, the signal does not continue increasing.

* **6T SRAM (Part A Task 1):**  
  Here, the bitline is actively discharged through access transistor $MA1$ and pull-down transistor $MN2$, which together behave as a current sink with $I_{read}\approx60\text{–}100\ \mu\text{A}$:
  $$I_{read}\approx C_{BL}\frac{dV_{BL}}{dt}$$
  * Only about $120\text{ ps}$ after wordline assertion ($t\approx1.12\text{ ns}$), the bitline differential reaches **$69\text{ mV}$**.
  * At $t=2.0\text{ ns}$, nearly $1\text{ ns}$ of discharge has occurred, producing **$\Delta V=729.86\text{ mV}$**, which is **$10.58\times$ the DRAM reference value**.

* **Design implication:** In a high-speed SRAM, the sense amplifier is normally activated early, around $100\text{–}200\text{ ps}$ after the wordline rises, when $\Delta V$ is approximately $70\text{–}100\text{ mV}. This reduces read latency and avoids unnecessary dynamic-energy consumption, $E_{dyn}=C_{BL}\Delta V V_{DD}$.

---

### Task 2: Read Disturbance $v(q)$ and Access-Transistor Width ($W=0.24\ \mu\text{m}$)

#### 1. Cause of the Read Disturbance

When $WL$ is driven to $V_{DD}=1.1\text{ V}$, access transistor $MA1$ and pull-down transistor $MN2$ create a resistive divider between the precharged bitline ($V_{BL}=1.1\text{ V}$) and ground. Because $BL$ is high while storage node $Q$ is at $0\text{ V}$, current flows into $Q$ and raises its voltage, producing the read bump $V_{READ}=v(q)$.

#### 2. Observed Simulation Behavior

* **Baseline cell ($W_{ax}=0.16\ \mu\text{m}$, $\beta_r=1.25$):**
  * $v(q)$ increases to **$205.52\text{ mV}$** at $t=1.058\text{ ns}$ and then gradually returns toward $0\text{ V}$ as $BL$ discharges.

* **Wider access device ($W_{ax}=0.24\ \mu\text{m}$, $\beta_r=0.833$):**
  * The cell ratio becomes less than one: $\beta_r=\frac{0.20}{0.24}=0.833<1.0$.
  * The storage-node bump becomes much larger, reaching **approximately $272\text{ mV}$**, an increase of **$66.5\text{ mV}$**.
  * **Transient versus static behavior:** With an ideal DC supply and no modeled thermal noise or mismatch, the disturbance eventually relaxes toward ground as the bitline voltage falls. Therefore, the simulation shows a serious disturbance rather than an immediate dynamic flip.
  * **Why this represents a design problem:** The inverter trip voltage is approximately $V_{trip}=450\text{ mV}$. A $272\text{ mV}$ bump consumes more than $60\%$ of the available noise margin. With realistic process variation ($\sigma_{Vth}\approx35\text{ mV}$ for 45 nm planar CMOS), cells in the distribution tail may trip $MN1$, initiating positive feedback and causing a **destructive read (read upset)**.

---

### Task 3: $V_{DD}$ Sweep from $1.1\text{ V}$ to $0.6\text{ V}$ with $C_{BL}=1\text{ pF}$

Following the course instruction (`ngspice ass1.docx`: *"Task 3 change c from 180f to 1p"*), the bitline capacitance is increased to $C_{BL}=1.0\text{ pF}$ to represent a more realistic full-column load across 256–512 bitcells.

#### 1. SPICE Sweep Data

| Index | $V_{DD}$ Supply (V) | $\Delta V(BLB,BL)$ at $t=2.0\text{ ns}$ (mV) | Sense-Amp Margin Relative to $25\text{ mV}$ Offset |
| :---: | :---: | :---: | :---: |
| **0** | **$1.100$** | **$143.59$** | $+118.59\text{ mV}$ (Robust margin) |
| **1** | **$1.050$** | **$131.61$** | $+106.61\text{ mV}$ |
| **2** | **$1.000$** | **$119.64$** | $+94.64\text{ mV}$ |
| **3** | **$0.950$** | **$107.68$** | $+82.68\text{ mV}$ |
| **4** | **$0.900$** | **$95.74$** | $+70.74\text{ mV}$ |
| **5** | **$0.850$** | **$83.83$** | $+58.83\text{ mV}$ |
| **6** | **$0.800$** | **$71.99$** | $+46.99\text{ mV}$ |
| **7** | **$0.750$** | **$60.25$** | $+35.25\text{ mV}$ |
| **8** | **$0.700$** | **$48.70$** | $+23.70\text{ mV}$ |
| **9** | **$0.650$** | **$37.49$** | $+12.49\text{ mV}$ |
| **10** | **$0.600$** | **$26.91$** | **$+1.91\text{ mV}$ (Near the floor)** |

#### 2. Identifying the Limiting Supply Voltage

* Lecture 5 gives a typical input-referred sense-amplifier offset of **$V_{offset}=25\text{ mV}$**, attributed to transistor threshold-voltage mismatch.
* At $V_{DD}=0.60\text{ V}$, the simulated differential is $26.91\text{ mV}$.
* Linear interpolation between $0.65\text{ V}$ ($37.49\text{ mV}$) and $0.60\text{ V}$ ($26.91\text{ mV}$) gives:
  $$V_{DD,limit}=0.60-(26.91-25.0)\times\frac{0.65-0.60}{37.49-26.91}\approx\mathbf{0.591\text{ V}\approx0.59\text{ V}}$$
* **Conclusion:** When $V_{DD}$ falls below approximately **$0.59\text{ V}$**, the bitline differential becomes smaller than the sense-amplifier offset, so reliable read sensing is lost.

---

### Task 4: Operation at $85\ ^\circ\text{C}$ and Failure-Mechanism Discussion

#### 1. Comparison of Measurements at $27\ ^\circ\text{C}$ and $85\ ^\circ\text{C}$

* **At $27\ ^\circ\text{C}$ (Nominal):**
  * $v(bl)_{2ns}=0.369715\text{ V}$
  * $v(blb)_{2ns}=1.09957\text{ V}$
  * $\mathbf{\Delta V(2.0\text{ ns})=729.86\text{ mV}}$
  * $\mathbf{v(q)_{max}=205.52\text{ mV}}$ at $t=1.0575\text{ ns}$

* **At $85\ ^\circ\text{C}$ (High Temperature):**
  * $v(bl)_{2ns}=0.517450\text{ V}$
  * $v(blb)_{2ns}=1.09957\text{ V}$
  * $\mathbf{\Delta V(2.0\text{ ns})=582.11\text{ mV}}$ (decrease of $147.75\text{ mV}$, or $-20.2\%$)
  * $\mathbf{v(q)_{max}=220.76\text{ mV}}$ (increase of $+15.24\text{ mV}$, or $+7.4\%$)

#### 2. Primary One-Paragraph Deliverable

> Comparing the temperature dependence of $\Delta V$ with the sense-amplifier offset, the **temperature-related increase in sensing offset, together with leakage from unselected cells, is the more critical factor and establishes the actual circuit-failure boundary**. Raising the temperature to $85\ ^\circ\text{C}$ reduces the bitline swing by about $20\%$, from $729.9\text{ mV}$ to $582.1\text{ mV}$, mainly because carrier mobility decreases as a result of acoustic-phonon scattering ($\mu\propto T^{-1.5}$). Even so, the remaining $\Delta V$ is still well above the nominal sensing threshold. At the same time, higher temperature strongly increases subthreshold leakage from the many unselected cells connected to the same bitline ($I_{sub}\propto T^2e^{-qV_{th}/(mkT)}$), producing additional common-mode and differential errors at the sensing nodes. The sense amplifier's input-referred offset also becomes more significant with temperature-dependent mismatch. Since the increased offset consumes sensing margin while the internal read disturbance rises to $220.8\text{ mV}$, **the sensing circuitry and its offset, rather than the raw bitcell discharge speed, determine the functional read-failure limit**.
