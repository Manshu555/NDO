# Complete Presentation Guide & Speaker Script: DSDV Routing Optimisation Using GWO

> **Source Slide Deck:** `NDO FINAL PPT.pptx`  
> **Repository:** `d:\Github\NDO`  
> **Presentation Duration:** 10–12 minutes (~2.5 minutes per presenter) + Q&A

---

## 👥 Team Members & Slide Allocation

| Slide # | Slide Title | Presenter | Roll Number | Key Focus |
|---|---|---|---|---|
| **Slide 1** | **Title & Team** | **Soham Patil** | `2023IMT-080` | Context, Team Introductions, Project Vision |
| **Slide 2** | **01 · Problem Formulation** | **Soham Patil** | `2023IMT-080` | High Mobility Failure Modes, Static DSDV Bottlenecks |
| **Slide 3** | **02 · Architecture** | **Soham Patil** | `2023IMT-080` | Closed-Loop GWO ⇄ Simulator Workflow |
| **Slide 4** | **03 · DSDV Protocol Rules** | **Abhinav Arya** | `2023IMT-002` | Routing Tuples, Sequence Numbers, Settling Time |
| **Slide 5** | **04 · Optimisation Engine** | **Abhinav Arya** | `2023IMT-002` | GWO Hierarchy ($\alpha, \beta, \delta$), Hunting Math, Benchmark Tests |
| **Slide 6** | **05 · Fitness Formulation** | **Manshu Jaiswal** | `2023IMT-051` | Discrete-Event Architecture, Multi-Objective Fitness, Penalty |
| **Slide 7** | **06 · Experimental Setup** | **Manshu Jaiswal** | `2023IMT-051` | 4D Search Space, Test Scenarios (Small, Med, High-Mob) |
| **Slide 8** | **07 · Results & Analysis** | **Ayush Gautam** | `2023IMT-022` | +30% to +59% PDR, Welch's t-test, Overhead Trade-off |
| **Slide 9** | **Thank You & Q&A** | **Ayush Gautam** | `2023IMT-022` | Concluding Takeaways & Defense Coordination |

---

# 🎤 Section 1: Soham Patil (Slides 1, 2, 3)

---

### Slide 1: Title & Overview
- **Visuals on Slide:** Dark navy theme, project title, subtitle, and team member roll numbers.
- **Key Points to Project:**
  - Topic: DSDV Routing Optimisation Using Grey Wolf Optimisation (GWO).
  - Scope: MANETs (Mobile Ad Hoc Networks), dynamic topologies, metaheuristic tuning.

#### 🎙️ Soham's Spoken Script:
> *"Respected faculty, evaluator, and dear peers. A very warm welcome to our project presentation titled: **'Performance Optimisation of DSDV Routing Using Grey Wolf Optimisation'**. 
>
> In Mobile Ad Hoc Networks, nodes move unpredictably without relying on cell towers or central routers. To communicate, devices must route packets cooperatively on the fly. Destination-Sequenced Distance-Vector—or DSDV—is the classic proactive routing protocol designed for this purpose. 
> 
> However, DSDV relies on static default timers that break down when nodes move dynamically. Our project explores whether a bio-inspired metaheuristic—Grey Wolf Optimisation—can systematically discover the optimal operating configuration for DSDV.
>
> Our team consists of:
> - Myself, **Soham Patil** (2023IMT-080), covering the Problem Formulation and System Architecture.
> - **Abhinav Arya** (2023IMT-002), who will detail the mathematical foundations of DSDV and GWO.
> - **Manshu Jaiswal** (2023IMT-051), presenting our Simulation Framework and Fitness Formulation.
> - And **Ayush Gautam** (2023IMT-022), presenting our quantitative experimental results and statistical validation."*

---

### Slide 2: 01 · Problem Formulation
- **Visuals on Slide:**
  - Headline: *"Static DSDV timers break when nodes move fast"*
  - Two Failure Modes: **Failure Mode A** (Stale Routes & Drops) and **Failure Mode B** (Overhead & Congestion).
  - Parameter Cards: Update Interval (15 s), Settling Time (6 s), Queue Length (64 pkts), Queue Hold Time (30 s).
  - Research Question Banner.

#### 🎙️ Soham's Spoken Script:
> *"Moving to Slide 2: The Core Problem. 
>
> DSDV is a proactive protocol—every single node maintains a route to every other node in the network by broadcasting its routing table periodically. However, standard DSDV relies on four hardcoded default parameters: a **15-second update interval**, a **6-second settling time**, a **64-packet queue**, and a **30-second queue timeout**.
>
> When network conditions change, these static timers trigger two catastrophic failure modes:
> 1. **Failure Mode A: Stale Routes and Packet Drops.** When nodes travel at high speeds—between 5 to 20 m/s—the physical links break long before the 15-second timer fires. Packets attempt to traverse nonexistent links and get dropped, cutting the Packet Delivery Ratio down to under 40%.
> 2. **Failure Mode B: Control Overhead and Channel Congestion.** If you naively make the timer too fast to catch broken links, the continuous flooding of full routing tables consumes all wireless bandwidth, causing radio interference and packet collision storms.
>
> This establishes our **Central Research Question**: *Can Grey Wolf Optimisation systematically discover the optimal multi-parameter balance that maximizes Packet Delivery Ratio without causing control overhead collapse under varying mobility?*"*

---

### Slide 3: 02 · Architecture
- **Visuals on Slide:**
  - Headline: *"A closed loop lets GWO tune DSDV against the simulator"*
  - Subhead: *"Protocol core stays untouched, so loop-freedom is preserved."*
  - 4-Step Numbered Feedback Loop: Candidate Vector $\rightarrow$ Simulation Run $\rightarrow$ Metric Extraction $\rightarrow$ Fitness Feedback.
  - Callout Cards: Protocol Core Untouched & Fewer Hyperparameters.

#### 🎙️ Soham's Spoken Script:
> *"To solve this problem, we designed the closed-loop optimization architecture shown on Slide 3. 
>
> Our methodology follows four iterative steps:
> 1. **Step 1 (Candidate Vector):** An individual wolf in the GWO population proposes a candidate 4-dimensional vector containing the update interval, settling time, queue size, and queue timeout.
> 2. **Step 2 (Simulation Run):** The discrete-event MANET simulator instantiates the DSDV protocol with this exact parameter set across stochastic mobile scenarios.
> 3. **Step 3 (Metric Extraction):** The simulator logs the resulting Packet Delivery Ratio, end-to-end latency, and routing overhead ratio.
> 4. **Step 4 (Fitness Feedback):** A scalar penalty score is computed and fed back to the wolf pack, driving the wolves toward higher-performing regions of the parameter space.
>
> Two major design advantages distinguish our approach:
> First, **the protocol core remains untouched**. We do not alter DSDV's sequence number rules or Bellman-Ford metric; therefore, strict loop-freedom is mathematically preserved.
> Second, **GWO possesses fewer hyperparameters** than Genetic Algorithms or PSO, allowing it to converge rapidly without getting trapped in local optima.
>
> Now, I hand over the presentation to **Abhinav Arya** to walk you through the mathematics of DSDV and GWO."*

---

# 🎤 Section 2: Abhinav Arya (Slides 4, 5)

---

### Slide 4: 03 · DSDV Protocol Rules
- **Visuals on Slide:**
  - Headline: *"DSDV accepts routes by sequence number, then hop count"*
  - Subhead: *"Strict destination sequence numbering prevents Bellman-Ford count-to-infinity and routing loops."*
  - Routing Table Schema: `[ Destination Address | Next Hop | Metric m | Sequence Number S | Install Time ]`
  - Three Rule Boxes: **Rule 1 (Route Acceptance)**, **Rule 2 (Settling Delay Filter)**, **Rule 3 (Link Breakage Signal)**.

#### 🎙️ Abhinav's Spoken Script:
> *"Thank you, Soham. On Slide 4, let us look at the mathematical mechanics of DSDV.
>
> In DSDV, every routing entry contains five fields: the destination address, the next-hop node, the metric or hop count $m$, the destination sequence number $S$, and the route install time.
>
> The integrity of the network is governed by three fundamental rules:
> - **Rule 1: Route Acceptance Rule.** When a node receives a route advertisement with sequence number $S'$ and metric $m'$, it adopts the update if and only if:
>   $$S' > S \quad \text{or} \quad (S' = S \text{ and } m' < m)$$
>   Because sequence numbers are generated strictly by the destination node, a higher sequence number always indicates fresher network state. If sequence numbers match, the shorter path wins. This lexicographical condition mathematically guarantees complete loop freedom and eliminates the classic Bellman-Ford count-to-infinity problem.
> - **Rule 2: Settling Delay Filter.** When multiple routes arrive, immediate re-broadcasting would trigger an avalanche of routing ripples. DSDV introduces a settling time window, $\tau_{\text{settling}}$, deferring advertisement until:
>   $$t_{\text{broadcast}} \ge t_{\text{arrival}} + \tau_{\text{settling}}$$
>   This dampens route flap and filters out transient suboptimal paths.
> - **Rule 3: Link Breakage Signal.** When a node detects an active link break, it immediately assigns metric $m = \infty$ and increments the destination sequence number to an **odd integer** ($S \leftarrow S + 1$). In DSDV, even sequence numbers represent active routes, while odd sequence numbers force the network to purge the broken link."*

---

### Slide 5: 04 · Optimisation Engine (GWO)
- **Visuals on Slide:**
  - Headline: *"GWO closes in on the best solution through three leaders"*
  - Subhead: *"The pack mimics grey wolf social hunting hierarchy: $\alpha, \beta, \delta$ represent the best three solutions, guiding the remaining wolves $\omega$."*
  - Three Leader Badges: **Alpha ($\alpha$) - Best Fit**, **Beta ($\beta$) - Second**, **Delta ($\delta$) - Third**.
  - Decay of parameter $a$ from 2 to 0: $|A| \ge 1$ (Exploration) vs $|A| < 1$ (Exploitation).
  - Benchmark Validation Box: Sphere achieves $3.17 \times 10^{-18}$; Rastrigin achieves exact minimum $0.0$.

#### 🎙️ Abhinav's Spoken Script:
> *"Turning to Slide 5: The Optimisation Engine.
>
> Grey Wolf Optimisation, introduced by Mirjalili, models the cooperative hunting behavior of wolf packs based on a clear leadership hierarchy:
> - **Alpha ($\alpha$):** The single best candidate solution found so far.
> - **Beta ($\beta$):** The second best solution.
> - **Delta ($\delta$):** The third best solution.
> - **Omega ($\omega$):** All remaining candidate solutions, which adjust their positions based on $\alpha$, $\beta$, and $\delta$.
>
> The transition from global exploration to local exploitation is driven by vector $\vec{A}$:
> $$\vec{A} = 2\vec{a} \cdot \vec{r}_1 - \vec{a}$$
> Where $\vec{a}$ decays linearly from 2 to 0 across iterations $T$. 
> - In early iterations, when $|\vec{A}| \ge 1$, the wolves diverge across the search space to explore diverse regions and prevent premature entrapment.
> - In later iterations, when $|\vec{A}| < 1$, the wolves converge inwards to exploit and pinpoint the global optimum.
>
> To update positions during hunting, each wolf calculates:
> $$\vec{D} = |\vec{C} \cdot \vec{X}_{\text{leader}} - \vec{X}|, \quad \vec{X}_{\text{new}} = \vec{X}_{\text{leader}} - \vec{A} \cdot \vec{D}$$
> And the final position is the centroid average of updates guided by $\alpha$, $\beta$, and $\delta$:
> $$\vec{X}(t+1) = \frac{\vec{X}_\alpha + \vec{X}_\beta + \vec{X}_\delta}{3}$$
>
> **Algorithmic Validation:** Before applying GWO to network simulations, we validated our implementation against standard synthetic benchmark functions: unimodal **Sphere**, where GWO converged to $3.17 \times 10^{-18}$, and multimodal **Rastrigin**, where it achieved the exact theoretical minimum of $0.0$.
>
> I now hand over to **Manshu Jaiswal** to explain our Simulation Setup and Fitness Formulation."*

---

# 🎤 Section 3: Manshu Jaiswal (Slides 6, 7)

---

### Slide 6: 05 · Fitness Formulation & Simulation Framework
- **Visuals on Slide:**
  - Headline: *"Simulator blocks feed a weighted fitness score"*
  - Pipeline Blocks: **Event Queue**, **Mobility (Random Waypoint)**, **Links (Unit-Disk)**, **Traffic (CBR UDP)**.
  - Multi-Objective Fitness Objective Function Box.
  - Disconnection Penalty Banner: **+10 Penalty for failed or disconnected runs**.

#### 🎙️ Manshu's Spoken Script:
> *"Thank you, Abhinav. On Slide 6, we present our simulation framework architecture and the mathematical formulation of our fitness function.
>
> We built a discrete-event network simulator modeled with four synchronized modules:
> 1. An **Event Queue** executing discrete time steps.
> 2. A **Random Waypoint Mobility Engine** continuously updating node coordinates within a $500 \times 500\text{ m}$ field.
> 3. A **Unit-Disk Physical Channel** with a realistic transmission range of $R_{\text{tx}} = 250\text{ m}$.
> 4. A **Traffic Generator** injecting continuous Constant Bit Rate (CBR) UDP packets across multi-hop routes.
>
> To evaluate candidate parameter configurations holistically, we formulated a **normalized multi-objective fitness minimization function**:
> $$\text{Fitness}(\vec{X}) = w_1 \cdot (1 - \text{PDR}) + w_2 \cdot D_{\text{norm}} + w_3 \cdot OH_{\text{norm}}$$
> We assigned specific weights:
> - **$w_1 = 0.5$ (50% weight):** Packet loss $(1 - \text{PDR})$ is our primary penalty.
> - **$w_2 = 0.3$ (30% weight):** End-to-end packet latency normalized against a 1-second threshold.
> - **$w_3 = 0.2$ (20% weight):** Routing control overhead ratio.
>
> Crucially, if a candidate parameter combination causes protocol instability, zero delivered packets, or disconnected networks, the simulator assigns an immediate **disconnection penalty of $+10.0$**, cleanly steering the wolf pack away from unfeasible configurations."*

---

### Slide 7: 06 · Experimental Setup
- **Visuals on Slide:**
  - Headline: *"Three scenarios test a four-parameter search space"*
  - Subhead: *"Optimiser pack of 10 wolves evaluated across 15 iterations per scenario."*
  - Table 1: **4D Parameter Bounds** (Periodic Update, Settling Time, Queue Length, Queue Time).
  - Table 2: **Test Scenario Definitions** (Small, Medium, High Mobility).
  - Multi-seed validation note.

#### 🎙️ Manshu's Spoken Script:
> *"Moving to Slide 7: Our Experimental Setup.
>
> The optimization search space is defined across four continuous protocol parameters:
> - **Periodic Update Interval:** Searched from $[5.0\text{ s}, 30.0\text{ s}]$ (Default is 15 s).
> - **Settling Time:** Searched from $[1.0\text{ s}, 15.0\text{ s}]$ (Default is 6 s).
> - **Max Queue Length:** Searched from $[16, 256\text{ packets}]$ (Default is 64 pkts).
> - **Max Queue Timeout:** Searched from $[5.0\text{ s}, 120.0\text{ s}]$ (Default is 30 s).
>
> To rigorously assess how GWO performs under differing topological stresses, we constructed three test scenarios:
> 1. **Small Scenario:** 15 nodes, 4 active traffic flows, walking/running speeds of 1 to 10 m/s, evaluated over 3 seeds for 60 seconds.
> 2. **Medium Scenario (Our Benchmark):** 20 nodes, 5 active flows, 1 to 10 m/s, evaluated over 5 independent seeds for 100 seconds.
> 3. **High Mobility Scenario:** 20 nodes, 5 flows, with rapid speeds of **5 to 20 m/s** (up to 72 km/h) over 5 seeds for 100 seconds.
>
> In every scenario, an optimization pack of **10 grey wolves** was evaluated over **15 iterations**. Using multiple random seeds ensured that stochastic variations in node mobility did not bias our findings.
>
> Now, **Ayush Gautam** will present our measured results and statistical analysis."*

---

# 🎤 Section 4: Ayush Gautam (Slides 8, 9)

---

### Slide 8: 07 · Results & Analysis
- **Visuals on Slide:**
  - Headline: *"GWO lifts delivery ratio 30–59%, at the cost of overhead"*
  - Results Table comparing Default DSDV vs GWO DSDV across Small, Medium, and High Mobility.
  - Three Callout Cards: **Learned Policy**, **Trade-Off**, and **Delay Stability**.

#### 🎙️ Ayush Gautam's Spoken Script:
> *"Thank you, Manshu. On Slide 8, we present the measured experimental results from our runs.
>
> Across all scenarios, the GWO-optimised DSDV configuration demonstrated substantial, statistically verified performance gains:
> - In the **Small Scenario (15 nodes)**: Packet Delivery Ratio improved from $64.7\%$ to **$84.0\%$**—a **$+29.7\%$ relative gain** ($p = 0.0379$).
> - In the **Medium Benchmark Scenario (20 nodes)**: PDR jumped from $61.5\%$ to **$80.0\%$**—a **$+30.1\%$ relative improvement** ($p = 0.0064$), while throughput climbed from 40.8 kbps to 53.1 kbps.
> - Most dramatically, in the **High Mobility Scenario (20 m/s)**: where default DSDV collapsed to just $39.7\%$ delivery due to link breakages, GWO-tuned DSDV maintained a robust **$63.1\%$ PDR**—a massive **$+58.9\%$ improvement** with a decisive $p$-value of $2.46 \times 10^{-5}$.
>
> **What Policy Did GWO Discover?**
> Analyzing the tuned parameters reveals the exact strategy discovered by GWO:
> - It shortened the **Periodic Update Interval** from 15 seconds down to **~5.5 seconds**, allowing nodes to detect broken links three times faster.
> - It reduced **Settling Time** from 6 seconds down to **2.5–3.9 seconds**, preventing delayed route propagation.
> - And it expanded the **Queue Capacity** from 64 to **106–113 packets** to buffer transient bursts during link transitions.
>
> **The Engineering Trade-Off:**
> Because updates occur more frequently, routing overhead ratio increased from $0.60$ to $0.80$. However, this extra control traffic was essential to keep routes fresh, and end-to-end delay remained virtually identical—holding steady under 9 milliseconds ($p = 0.138$, not statistically significant).
>
> Every reported improvement has been validated using **Welch’s two-sample t-test**, proving statistical significance well below the $\alpha = 0.05$ threshold."*

---

### Slide 9: Conclusion & Q&A
- **Visuals on Slide:** *"Thank you"* with open floor for questions.

#### 🎙️ Ayush Gautam's Spoken Script:
> *"To conclude: our findings confirm that DSDV's primary vulnerability in mobile networks is not its routing logic, but its rigid static parameter timers. By applying Grey Wolf Optimisation in a closed simulation loop, we achieved up to a 59% improvement in delivery reliability without altering the protocol's core loop-free properties.
>
> All code, benchmark tests, simulation logs, and plots are fully reproducible and available in our GitHub repository.
>
> On behalf of Soham, Abhinav, Manshu, and myself, thank you very much for your time. We are now open to your questions."*

---

## 🎯 Viva Defense & Examiner Q&A Guide

### For Soham Patil:
- **Q: "Why did you optimize parameters instead of proposing a new routing protocol?"**
  - **Answer:** *"Designing a completely new protocol breaks standard compliance and requires redesigning loop-freedom proofs from scratch. Tuning governing parameters preserves DSDV's proven sequence-number loop-freedom while adapting its operational dynamics directly to varying mobility."*

### For Abhinav Arya:
- **Q: "Why does DSDV use odd sequence numbers for broken links?"**
  - **Answer:** *"In DSDV, only the destination node itself can generate an even sequence number. When an intermediate node detects a broken link, it cannot speak on behalf of the destination, so it increments the sequence number by 1 to create an odd sequence number with metric $\infty$. This uniquely signals a broken path and prevents routing loops."*

### For Manshu Jaiswal:
- **Q: "Why did you choose Welch's t-test over a standard Student's t-test?"**
  - **Answer:** *"Standard Student's t-test assumes both populations have equal variances. In our MANET experiments, default DSDV exhibited higher variance due to severe link dropouts compared to the optimized protocol. Welch's t-test does not assume equal variances, making it the statistically sound choice for MANET benchmarks."*

### For Ayush Gautam:
- **Q: "Is a 30% increase in routing overhead acceptable in a wireless network?"**
  - **Answer:** *"Yes, because in high-mobility MANETs, the primary failure mode is stale routes causing packet drops. The modest increase in overhead ratio (from 0.60 to 0.80) was the exact operational cost required to raise delivery ratio from 39% to 63%. Because average delay stayed under 9 ms, the wireless channel was not congested, proving this was a beneficial trade-off."*
