# PPT Presentation Prompt & Slide Deck Script: DSDV Routing Optimisation Using Grey Wolf Optimisation (GWO)

> **Team Presentation Division:**
> - **Soham:** Slide 1 (Introduction) + Slide 2 (Problem Statement) + Slide 3 (Proposed Solution)
> - **Abhinav:** Slide 4 (Working of DSDV Maths) + Slide 5 (Working of GWO Mathematically)
> - **Manshu:** Slide 6 (Simulation Architecture & Model) + Slide 7 (Simulation Scenarios & Tuning Space)
> - **Aayush Gautam:** Slide 8 (Experimental Results, Statistical Validation & Conclusion)

---

## Part 1: Master AI Prompt (Copy-Paste Ready for Gamma / ChatGPT / SlidesAI)

```text
Act as a senior computer networks researcher and elite presentation designer. Create an 8-slide, visually stunning, academically rigorous presentation for our university computer science project titled "DSDV Routing Protocol Optimisation in MANETs Using Grey Wolf Optimisation (GWO)".

Format the slides cleanly with a modern dark tech aesthetic (slate navy #0F172A background, cyan/teal #06B6D4 accents, clean white #F8FAFC text, elegant typography, LaTeX mathematical equations, structured metric tables, and clear visual layout descriptions).

The presentation is divided among 4 team members across exactly 8 slides:
- Slide 1 (Soham): Title & Introduction to MANET Routing Challenges
- Slide 2 (Soham): Problem Statement & Flaws of Static DSDV
- Slide 3 (Soham): Proposed Solution — Closed-Loop GWO Parameter Optimization
- Slide 4 (Abhinav): Mathematical Formulation & Operation of DSDV
- Slide 5 (Abhinav): Mathematical Formulation of Grey Wolf Optimisation (GWO)
- Slide 6 (Manshu): Simulation Framework Architecture & Multi-Objective Fitness Formulation
- Slide 7 (Manshu): Experimental Scenarios, Node Mobility & GWO Parameter Search Space
- Slide 8 (Aayush Gautam): Experimental Results, Statistical Validation (Welch's t-test), & Key Findings

Include exact mathematical equations, quantitative benchmark and simulation figures, parameter comparison tables, and speaker-specific talking points as outlined in the detailed slide deck specification below.
```

---

## Part 2: Complete Slide-by-Slide Content & Speaker Script

---

### Slide 1: Title & Introduction
**Presenter:** Soham  
**Slide Type:** Title & Context Slide  
**Visual Style:** Deep navy background, glowing network topology mesh graphic, clean hierarchy.

#### Slide Content:
- **Title:** DSDV Routing Protocol Optimisation Using Grey Wolf Optimisation (GWO)
- **Subtitle:** Enhancing MANET Performance Through Metaheuristic Parameter Tuning
- **Project Scope:** Academic Evaluation of Dynamic Metaheuristic Adaptation on Proactive Ad-Hoc Routing
- **Project Team & Roles:**
  - **Soham:** Introduction, Problem Formulation, & Proposed Architecture
  - **Abhinav:** Mathematical Mechanics of DSDV & Grey Wolf Optimisation
  - **Manshu:** Discrete-Event MANET Simulation Engine & Parameter Search Setup
  - **Aayush Gautam:** Quantitative Results, Statistical Validation (Welch's t-test), & Trade-Off Analysis
- **Key MANET Context:**
  - Mobile Ad Hoc Networks (MANETs) operate without fixed infrastructure; nodes serve concurrently as hosts and routers.
  - Frequent topology changes, variable wireless link quality, and energy constraints make routing protocol parameter configuration decisive for Quality of Service (QoS).

#### 🎙️ Soham's Spoken Script:
> *"Good morning, esteemed faculty and fellow peers. Today, our team is presenting our project: 'DSDV Routing Protocol Optimisation Using Grey Wolf Optimisation'. In Mobile Ad Hoc Networks, devices must route data cooperatively without any centralised towers or fixed infrastructure. Because nodes move dynamically, wireless links break and reform continuously. Traditional routing protocols use static, hardcoded configuration values that fail to adapt when mobility surges. Over the next eight slides, our team will walk you through the problem, the underlying mathematics of both DSDV and GWO, our simulation setup, and our experimentally verified results."*

---

### Slide 2: Problem Statement
**Presenter:** Soham  
**Slide Type:** Problem Analysis / Conceptual Conflict Diagram  
**Visual Style:** Two-sided tension diagram (Overhead vs. Route Staleness), red alert accent boxes.

#### Slide Content:
- **Core Dilemma in DSDV (Destination-Sequenced Distance-Vector):**
  - DSDV is fundamentally proactive; every node maintains a complete routing table for all destinations.
  - Standard RFC/NS-3 default parameters are fixed:
    - `PeriodicUpdateInterval = 15.0 s`
    - `SettlingTime = 6.0 s`
    - `MaxQueueLen = 64 packets`
    - `MaxQueueTime = 30.0 s`
- **The Mobility Breakdown:**
  - **Static Timers in Dynamic Topologies:** If nodes move rapidly (5–20 m/s), a 15-second update interval leaves routing tables stale for prolonged periods, causing high packet drops.
  - **The Settling Time Bottleneck:** A 6-second settling time delays advertising newer routes to prevent route fluctuations, causing buffered packets to expire during handoffs.
  - **The Routing Overhead Trade-off:** Naively broadcasting updates too frequently congests the shared wireless channel, creating packet collision storms.
- **The Research Question:**
  > *Can a nature-inspired metaheuristic (Grey Wolf Optimisation) automatically discover the optimal multi-parameter balance for DSDV to maximise Packet Delivery Ratio (PDR) without causing network congestion under varying mobility regimes?*

#### 🎙️ Soham's Spoken Script:
> *"To understand why optimisation is necessary, consider the fundamental trade-off of DSDV. DSDV guarantees loop-free routes using destination sequence numbers. However, its default parameters were designed decades ago under benign, low-mobility assumptions. In real mobile environments, if nodes travel at 15 to 20 metres per second, waiting 15 seconds between periodic updates results in stale paths, dropped packets, and broken links. Conversely, if you naively broadcast updates every second, the control packets flood the wireless medium and choke payload data. There is an intricate sweet spot between route freshness, settling time, and buffer queues. Hand-tuning these four coupled parameters across different topologies is practically impossible—which brings us to our proposed solution."*

---

### Slide 3: Proposed Solution — Closed-Loop GWO Parameter Tuning
**Presenter:** Soham  
**Slide Type:** System Architecture & Workflow Pipeline  
**Visual Style:** Circular feedback loop diagram connecting GWO Optimizer ⇄ Network Simulation Engine.

#### Slide Content:
- **Solution Paradigm:** Closed-Loop Simulation-Guided Metaheuristic Search
  - Rather than redesigning DSDV's core routing logic (preserving strict loop freedom and standard sequence numbers), we optimize its governing operational parameters.
- **Architecture Pipeline:**
  1. **Candidate Parameter Vector:** A wolf in the GWO population proposes a 4D configuration vector:
     $$\vec{X} = [\text{PeriodicUpdateInterval}, \text{SettlingTime}, \text{MaxQueueLen}, \text{MaxQueueTime}]$$
  2. **Simulation Execution:** The MANET simulation engine instantiates DSDV with candidate vector $\vec{X}$ under deterministic mobility seeds.
  3. **Multi-Metric Evaluation:** The simulator extracts Packet Delivery Ratio ($PDR$), Mean Latency ($D$), and Routing Overhead ($OH$).
  4. **Fitness Feedback:** A scalar penalty score is computed and returned to guide the GWO pack towards the global optimum.
- **Why Grey Wolf Optimisation (GWO)?**
  - Superior balance between exploration (global diversification) and exploitation (local intensification).
  - Faster convergence rate and fewer hyper-parameters compared to Genetic Algorithms (GA) or Particle Swarm Optimisation (PSO).

#### 🎙️ Soham's Spoken Script:
> *"Our proposed solution couples the metaheuristic search power of Grey Wolf Optimisation directly with a packet-level network simulation model in a closed feedback loop. Each wolf represents a candidate 4-dimensional parameter set: update interval, settling time, queue length, and queue expiration time. The simulation executes with these parameters under realistic mobile conditions, measures the resulting network performance, and feeds back a multi-objective fitness score. GWO iteratively refines the pack until it finds the optimal operational parameters for that specific mobility profile. Now, my teammate Abhinav will present the exact mathematical mechanics of both DSDV and GWO."*

---

### Slide 4: Working of DSDV — Mathematical Formulation
**Presenter:** Abhinav  
**Slide Type:** Mathematical Foundation & Algorithmic Mechanics  
**Visual Style:** Routing table schema alongside clean LaTeX mathematical formulas.

#### Slide Content:
- **DSDV Routing Table Tuple:**
  Each node $i$ maintains an entry for destination $j$:
  $$R_i(j) = \langle \text{Dest}_j, \text{NextHop}_k, \text{Metric } m, \text{SeqNum } S_j, \text{InstallTime } t_{\text{inst}} \rangle$$
- **1. Route Selection & Loop-Freedom Invariant:**
  When node $i$ receives an update $\langle j, m', S_j' \rangle$ from neighbour $k$, the route is accepted if and only if:
  $$S_j' > S_j \quad \lor \quad (S_j' = S_j \;\land\; m' + 1 < m)$$
  *Strict sequence number ordering guarantees loop-freedom at all times without counting to infinity.*
- **2. Settling Time Delay Inequality:**
  To suppress route flap and unnecessary broadcast ripple effects:
  $$t_{\text{broadcast}} \ge t_{\text{arrival}} + \tau_{\text{settling}}$$
  If a better metric arrives within $\tau_{\text{settling}}$, only the best metric is advertised.
- **3. Route Metric Increment (Bellman-Ford Metric):**
  $$m_{new} = m_{\text{received}} + \text{Cost}(i, k)$$
- **4. Broken Link Sequence Number Update:**
  When link $(i, k)$ breaks, metric is set to $\infty$ and the sequence number is incremented to an odd integer:
  $$S_j \leftarrow S_j + 1 \quad (\text{odd indicates broken route})$$

#### 🎙️ Abhinav's Spoken Script:
> *"Thank you, Soham. Let us examine the mathematical foundations of DSDV. In DSDV, every routing entry contains five critical parameters, most importantly the Destination Sequence Number, $S_j$, and the hop metric, $m$. Route updates are governed by a strict lexicographical inequality: an update is adopted if it possesses a strictly higher sequence number, or an identical sequence number with a lower hop count. This mathematical condition formally guarantees complete loop-freedom. Furthermore, DSDV implements a Settling Time window, denoted here as $\tau_{\text{settling}}$. When a route with a new sequence number arrives, the node holds back immediate broadcast until $\tau_{\text{settling}}$ elapses to verify if a shorter path arrives. If $\tau_{\text{settling}}$ is too high, packets stall; if too low, routing ripples flood the network. Tuning this mathematically balances convergence stability against path latency."*

---

### Slide 5: Working of GWO — Mathematical Formulation
**Presenter:** Abhinav  
**Slide Type:** Metaheuristic Algorithm & Vector Calculus  
**Visual Style:** Wolf hierarchy pyramid ($\alpha, \beta, \delta, \omega$) + 2D/3D hunting vector diagram.

#### Slide Content:
- **1. Social Hierarchy:**
  - $\vec{X}_\alpha$: Best candidate solution (Fittest)
  - $\vec{X}_\beta$: Second-best candidate
  - $\vec{X}_\delta$: Third-best candidate
  - $\vec{X}_\omega$: Remaining candidate solutions guided by $\alpha, \beta, \delta$
- **2. Mathematical Model of Encircling Prey:**
  $$\vec{D} = |\vec{C} \cdot \vec{X}_p(t) - \vec{X}(t)|$$
  $$\vec{X}(t+1) = \vec{X}_p(t) - \vec{A} \cdot \vec{D}$$
  Where coefficient vectors $\vec{A}$ and $\vec{C}$ are generated via:
  $$\vec{A} = 2\vec{a} \cdot \vec{r}_1 - \vec{a}, \qquad \vec{C} = 2 \cdot \vec{r}_2$$
  *$\vec{r}_1, \vec{r}_2 \in [0, 1]$ are uniform random vectors.*
- **3. Linear Exploration-Exploitation Decay:**
  Parameter $a$ linearly decreases from 2 to 0 across $T$ iterations:
  $$a(t) = 2 - 2 \left(\frac{t}{T}\right)$$
  - $|\vec{A}| > 1$: Global exploration (wolves diverge to discover new regions).
  - $|\vec{A}| < 1$: Local exploitation (wolves converge towards prey).
- **4. Position Hunting Equation:**
  $$\vec{D}_\alpha = |\vec{C}_1 \cdot \vec{X}_\alpha - \vec{X}|, \quad \vec{D}_\beta = |\vec{C}_2 \cdot \vec{X}_\beta - \vec{X}|, \quad \vec{D}_\delta = |\vec{C}_3 \cdot \vec{X}_\delta - \vec{X}|$$
  $$\vec{X}_1 = \vec{X}_\alpha - \vec{A}_1 \cdot \vec{D}_\alpha, \quad \vec{X}_2 = \vec{X}_\beta - \vec{A}_2 \cdot \vec{D}_\beta, \quad \vec{X}_3 = \vec{X}_\delta - \vec{A}_3 \cdot \vec{D}_\delta$$
  $$\vec{X}(t+1) = \frac{\vec{X}_1 + \vec{X}_2 + \vec{X}_3}{3}$$

#### 🎙️ Abhinav's Spoken Script:
> *"Now let us turn to the mathematical engine driving our optimisation: Mirjalili's Grey Wolf Optimiser. GWO mimics the leadership hierarchy and cooperative hunting behavior of grey wolves. The top three fittest solutions are designated as Alpha, Beta, and Delta, while all remaining wolves, Omega, update their positions relative to these three leaders. Encircling is governed by the vector difference equation $\vec{D} = |\vec{C} \cdot \vec{X}_p - \vec{X}|$. The crucial transition between global exploration and local exploitation is controlled by parameter $a$, which decays linearly from 2 to 0. When $|A| > 1$, the wolves scatter across the search space to avoid local minima. When $|A| < 1$, the pack closes in on the global optimum. In the hunting phase, each wolf calculates three distinct position vectors relative to Alpha, Beta, and Delta, and takes their mathematical average. Next, Manshu will detail our simulation architecture and how this fitness function evaluates candidate solutions."*

---

### Slide 6: Simulation Architecture & Multi-Objective Fitness
**Presenter:** Manshu  
**Slide Type:** System Architecture & Simulation Engine  
**Visual Style:** Block diagram showing Event Queue, Mobility Engine, Routing Core, and Metrics Collector.

#### Slide Content:
- **Simulation Engine Architecture:**
  - **Core:** Event-driven packet simulation with discrete time steps ($dt = 0.1 \text{ s}$).
  - **Mobility Model:** Random Waypoint (RWP) with continuous spatial coordinate tracking:
    $$\vec{p}_i(t + \Delta t) = \vec{p}_i(t) + \vec{v}_i \cdot \Delta t, \quad v_i \in [v_{\min}, v_{\max}]$$
  - **Propagation & Channel:** Unit Disk Graph (UDG) model with radio range $R_{\text{tx}} = 250\text{ m}$. Link state between nodes $i$ and $j$:
    $$\text{Link}(i, j) = \begin{cases} 1 & \text{if } \|\vec{p}_i - \vec{p}_j\|_2 \le R_{\text{tx}} \\ 0 & \text{otherwise} \end{cases}$$
  - **Traffic Generator:** Continuous Bit Rate (CBR) UDP traffic flows over multi-hop paths.
- **Mathematical Multi-Objective Fitness Formulation:**
  To optimize QoS comprehensively, we formulate a normalized minimization objective:
  $$\text{Fitness}(\vec{X}) = w_1 \cdot (1 - \text{PDR}) + w_2 \cdot \left(\frac{\bar{D}}{D_{\max}}\right) + w_3 \cdot \left(\frac{OH}{OH + \text{Payload}}\right)$$
  - **Primary Weight:** $w_1 = 0.5$ (Penalizes lost packets heavily).
  - **Latency Weight:** $w_2 = 0.3$ ($D_{\max} = 1.0\text{ s}$ normalization).
  - **Overhead Weight:** $w_3 = 0.2$ (Ratio of routing control packets to total traffic).
  - **Constraint Penalty:** Failed or disconnected runs return a penalty value of $+10.0$.

#### 🎙️ Manshu's Spoken Script:
> *"Thank you, Abhinav. To evaluate candidate parameter vectors, we implemented an event-driven packet-level MANET simulation engine. Nodes move according to the continuous Random Waypoint mobility model inside a 500 by 500 metre field, with a transmission radius of 250 metres. Over multi-hop paths, nodes exchange constant bit rate UDP traffic. The evaluation of each wolf is governed by our multi-objective fitness function. We assign a 50% weight to packet loss (1 - PDR), 30% to normalized end-to-end latency, and 20% to routing overhead ratio. This prevents the optimizer from cheating by simply flooding the network to gain delivery at the expense of overwhelming control overhead. Any unstable configuration that causes network collapse is penalised with an immediate fitness score of 10."*

---

### Slide 7: Experimental Scenarios & Parameter Tuning Space
**Presenter:** Manshu  
**Slide Type:** Experimental Setup & Configuration Matrix  
**Visual Style:** Side-by-side comparative tables with highlighted search bounds.

#### Slide Content:
- **4D GWO Search Space & Bounds:**
  $$\vec{X} = [x_1, x_2, x_3, x_4] \in \mathbb{R}^4$$

  | Parameter | Symbol | Default DSDV | Search Bounds $[\text{LB}, \text{UB}]$ | Operational Role |
  |-----------|--------|--------------|--------------------------------------|------------------|
  | Periodic Update Interval | $x_1$ | $15.0\text{ s}$ | $[5.0\text{ s}, 30.0\text{ s}]$ | Frequency of full routing table broadcasts |
  | Settling Time | $x_2$ | $6.0\text{ s}$ | $[1.0\text{ s}, 15.0\text{ s}]$ | Damping delay before propagating better routes |
  | Max Queue Length | $x_3$ | $64\text{ pkts}$ | $[16, 256]\text{ pkts}$ | Intermediate buffer size during route discovery |
  | Max Queue Timeout | $x_4$ | $30.0\text{ s}$ | $[5.0\text{ s}, 120.0\text{ s}]$ | Time-to-live for buffered packets |

- **Three Evaluated Simulation Scenarios:**

  | Parameter | Scenario 1: Small | Scenario 2: Medium (Benchmark) | Scenario 3: High Mobility |
  |-----------|-------------------|--------------------------------|---------------------------|
  | Number of Nodes | 15 nodes | 20 nodes | 20 nodes |
  | Simulation Field | $500 \times 500\text{ m}$ | $500 \times 500\text{ m}$ | $500 \times 500\text{ m}$ |
  | Node Speed Range | $1.0 - 10.0\text{ m/s}$ | $1.0 - 10.0\text{ m/s}$ | $\mathbf{5.0 - 20.0\text{ m/s}}$ |
  | Active CBR Flows | 4 flows | 5 flows | 5 flows |
  | Simulation Duration | $60\text{ s}$ | $100\text{ s}$ | $100\text{ s}$ |
  | GWO Hyperparameters | $N=10$ wolves, $T=15$ iterations | $N=10$ wolves, $T=15$ iterations | $N=10$ wolves, $T=15$ iterations |
  | Independent Seeds | 3 random seeds | 5 random seeds | 5 random seeds |

#### 🎙️ Manshu's Spoken Script:
> *"On this slide, you see our exact experimental setup. We defined a 4-dimensional continuous search space spanning update interval, settling time, buffer capacity, and queue timeout. To evaluate the algorithm robustly, we designed three test scenarios: a Small 15-node baseline, a Medium 20-node benchmark, and a challenging High Mobility scenario where nodes travel up to 20 metres per second—equivalent to 72 km/h vehicular speeds. For each scenario, the GWO algorithm deployed 10 wolves across 15 iterations. To ensure strict academic integrity and avoid stochastic flukes, all final evaluations were executed across multiple independent pseudo-random seeds with paired Welch's t-tests. Now, Aayush Gautam will reveal the quantitative results and statistical analysis."*

---

### Slide 8: Experimental Results & Statistical Validation
**Presenter:** Aayush Gautam  
**Slide Type:** Results, Charts, Statistical Rigor & Conclusion  
**Visual Style:** High-contrast data table with green improvement badges, p-value verification, and conclusion cards.

#### Slide Content:
- **Optimal Parameters Discovered by GWO:**
  - **Periodic Update Interval:** Reduced from **15.0 s** $\rightarrow$ **5.2–5.8 s** (Adapts ~3× faster to topology shifts).
  - **Settling Time:** Reduced from **6.0 s** $\rightarrow$ **2.5–3.9 s** (Accelerates convergence).
  - **Queue Length:** Expanded from **64** $\rightarrow$ **106–113 pkts** (Absorbs transient handoff bursts).

- **Measured Performance Comparison Table (Real Experimental Data):**

  | Scenario | Metric | Default DSDV (Mean $\pm$ Std) | GWO-Optimised DSDV (Mean $\pm$ Std) | Improvement (%) | Welch's t-test ($p$-value) | Statistical Significance |
  |----------|--------|-------------------------------|--------------------------------------|-----------------|-----------------------------|--------------------------|
  | **Small (15 nodes)** | **PDR** | $64.72\% \pm 8.19\%$ | $\mathbf{83.95\% \pm 7.04\%}$ | $\mathbf{+29.7\%}$ | $p = 0.0379$ | **Significant ($p < 0.05$)** |
  | | Throughput | $34.8\text{ kbps}$ | $\mathbf{45.2\text{ kbps}}$ | $+29.7\%$ | $p = 0.0320$ | **Significant** |
  | | Mean Delay | $8.05\text{ ms}$ | $8.01\text{ ms}$ | Neutral ($-0.5\%$) | $p = 0.9793$ | Not Significant |
  | **Medium (20 nodes)** | **PDR** | $61.45\% \pm 8.72\%$ | $\mathbf{79.95\% \pm 3.37\%}$ | $\mathbf{+30.1\%}$ | $p = 0.0064$ | **Highly Significant ($p < 0.01$)** |
  | | Throughput | $40.8\text{ kbps}$ | $\mathbf{53.1\text{ kbps}}$ | $+30.1\%$ | $p = 0.0073$ | **Highly Significant** |
  | | Overhead Ratio | $0.601$ | $0.796$ | $-32.4\%$ (Trade-off) | $p < 0.0001$ | Significant Overhead Rise |
  | **High Mobility (20 m/s)** | **PDR** | $39.71\% \pm 3.18\%$ | $\mathbf{63.08\% \pm 4.48\%}$ | $\mathbf{+58.9\%}$ | $p = 0.000025$ | **Decisive ($p < 0.001$)** |
  | | Throughput | $26.5\text{ kbps}$ | $\mathbf{42.1\text{ kbps}}$ | $+58.8\%$ | $p = 0.000038$ | **Decisive** |
  | | Mean Delay | $7.35\text{ ms}$ | $8.30\text{ ms}$ | $-13.0\%$ ($+0.95\text{ ms}$) | $p = 0.1379$ | Not Significant ($p > 0.05$) |

- **Key Research Takeaways:**
  1. **Massive Reliability Boost:** GWO delivers a **+29.7% to +58.9% gain in Packet Delivery Ratio**, with the greatest advantage occurring under extreme mobility.
  2. **Honest Engineering Trade-off:** The higher update frequency increases routing control overhead from 0.60 to 0.80. This overhead trade-off is necessary to keep routes fresh and avoid catastrophic packet loss.
  3. **Statistical Certainty:** With $p = 0.0064$ (Medium) and $p = 2.46 \times 10^{-5}$ (High Mobility), the performance improvement is statistically validated beyond doubt.

#### 🎙️ Aayush Gautam's Spoken Script:
> *"Thank you, Manshu. Here are the definitive results from our experimental runs. Across all three scenarios, GWO uncovered a consistent, highly logical policy: it shortened the periodic update interval from 15 seconds down to approximately 5.5 seconds, reduced settling time to around 3 seconds, and enlarged buffer queues. Looking at the numbers, in the Medium benchmark scenario, Packet Delivery Ratio increased from 61.45% to 79.95%—a 30.1% relative improvement with a p-value of 0.0064, proving statistical significance at the 99% confidence level. Under High Mobility, where default DSDV collapsed to under 40% delivery, the GWO-tuned protocol maintained 63.08% delivery—a massive 58.9% improvement with p = 0.000025. In accordance with academic honesty, we also report the trade-off: routing overhead increased from 0.60 to 0.79 due to faster broadcasts. However, latency remained virtually unaffected at under 9 milliseconds. In conclusion, GWO successfully proved that metaheuristic parameter tuning substantially improves DSDV routing reliability in mobile ad hoc networks. We are now happy to take any questions."*

---

## Part 3: Viva & Defense Q&A Cheatsheet (For Each Team Member)

### Q&A for Soham (Introduction & Problem Statement):
- **Examiner:** *"Why did you choose DSDV instead of AODV or DSR?"*
  - **Soham's Answer:** *"DSDV is the classic proactive distance-vector protocol. Unlike reactive protocols like AODV that initiate route discovery on demand, DSDV relies entirely on background periodic updates and destination sequence numbers to guarantee loop freedom. Because its updates are timer-driven, DSDV is far more sensitive to parameter misconfiguration, making it an ideal testbed for parameter optimisation."*
- **Examiner:** *"Why not just rewrite the routing protocol code rather than tune parameters?"*
  - **Soham's Answer:** *"Preserving the protocol core ensures 100% standard compliance and mathematical loop-freedom guarantees. By tuning operational parameters rather than rewriting the protocol, our framework can be deployed directly into existing networking firmware without breaking RFC interoperability."*

### Q&A for Abhinav (Mathematical Models):
- **Examiner:** *"How does DSDV mathematically guarantee there are no routing loops?"*
  - **Abhinav's Answer:** *"Through monotonically increasing destination sequence numbers generated exclusively by the destination node itself. An update is only accepted if its sequence number is strictly greater, or if equal, the hop count is strictly smaller. Since sequence numbers form a strictly monotonic partial order, closed cycles or loops cannot form."*
- **Examiner:** *"Why use GWO over traditional Particle Swarm Optimization (PSO) or Genetic Algorithms (GA)?"*
  - **Abhinav's Answer:** *"GWO incorporates an adaptive leader-follower hierarchy $(\alpha, \beta, \delta)$ with a linearly decaying exploration parameter $a(t)$. Studies by Mirjalili et al. demonstrated that GWO has fewer tuning hyperparameters than GA or PSO, suffers less from premature convergence on continuous parameter landscapes, and converges in fewer function evaluations—which is vital when each evaluation involves a full network simulation."*

### Q&A for Manshu (Simulation Setup):
- **Examiner:** *"Why is there a penalty of 10.0 in the fitness function?"*
  - **Manshu's Answer:** *"The multi-objective fitness components (1-PDR, delay, and overhead) are bounded between 0 and 1, resulting in normal fitness values between 0.0 and 1.0. A penalty score of 10.0 is an artificial death penalty assigned if a parameter combination causes simulator crashes, zero delivered packets, or disconnected topologies, ensuring that the GWO pack immediately steers away from fatal regions."*
- **Examiner:** *"How did you validate your GWO implementation before applying it to the MANET simulator?"*
  - **Manshu's Answer:** *"We validated GWO against standard mathematical benchmark functions: the unimodal Sphere function and the multimodal Rastrigin function with known analytical minima at 0.0. GWO achieved 3.17 × 10⁻¹⁸ on Sphere and 0.0 on Rastrigin, confirming algorithmic correctness before coupling it to network simulations."*

### Q&A for Aayush Gautam (Results & Statistics):
- **Examiner:** *"Why did the routing overhead increase in the GWO-optimised version?"*
  - **Aayush's Answer:** *"GWO reduced the periodic update interval from 15 seconds to ~5.5 seconds. Faster periodic broadcasts inherently transmit more control packets per unit time. However, this extra overhead is what refreshed broken links in time to rescue PDR from 39% to 63% in high mobility. Our fitness function actively balanced this trade-off using a 0.2 overhead penalty weight."*
- **Examiner:** *"What does Welch's t-test prove about your results?"*
  - **Aayush's Answer:** *"Because the baseline and optimised runs have different variances, standard Student's t-test is invalid. Welch's t-test does not assume equal variances. Our obtained p-values of 0.0064 for Medium and 0.000025 for High Mobility are far below the significance threshold ($\alpha = 0.05$), proving with over 99.9% statistical confidence that the improvements are genuinely due to GWO tuning and not random simulation variance."*
