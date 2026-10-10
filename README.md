# Can Cultural Beliefs Generate Spurious Blood-Type–Personality Associations?

### An Agent-Based Simulation and Causal Modeling of the Blood-Type Personality Myth

[![JASSS](https://img.shields.io/badge/Submitted%20to-JASSS-blue.svg)](https://www.jasss.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**Author:** Suhyun Kim  
**Affiliation:** Korea University College of Medicine, Seoul 02841, Republic of Korea  
**Contact:** `ktngus5043@korea.ac.kr`  

---

## 📖 Overview

The belief that ABO blood type dictates human personality traits—popularized across East Asia (notably South Korea and Japan) for over half a century—is widely dismissed by molecular geneticists and psychologists as pseudoscientific.

This repository hosts the official open-science replication package for our computational investigation submitted to the **Journal of Artificial Societies and Social Simulation (JASSS)**. Using a multi-generational agent-based model ($N = 5,000$ agents across 25 generations with independent Monte Carlo replications managed via `np.random.SeedSequence`), we evaluate three candidate social and demographic mechanisms capable of generating statistical associations in the absence of biological causality:

1. **Belief-driven assortative mating** ($\alpha$)
2. **Subpopulation stratification and panmictic intermarriage** ($\Delta$)
3. **Social labeling and developmental socialization feedback** ($\beta$)

Furthermore, we investigate counterfactual **cultural belief withdrawal**, demonstrating how phenotypic feedback decays immediately upon cessation of socialization, while latent cross-trait genetic-component associations (between the ABO locus and polygenic breeding values) accumulated via assortative mating exhibit multi-generational inertia.

---

## 📂 Repository Structure

```text
blood-type-personality-abm/
├── README.md                              # Comprehensive documentation and reproduction guide
├── LICENSE                                # MIT License
├── requirements.txt                       # Python package dependencies
├── run_reproduction.py                    # One-click master replication & verification script
├── src/
│   ├── simulation.py                      # Vectorized multi-generational ABM engine (NumPy)
│   └── analytics.py                       # Factorial ANOVA, metrics summary, and Figures 1–4
├── data/                                  # Simulation datasets (CSV)
│   ├── experiment1_assortative.csv        # Assortative mating sweep (alpha in [0.0, 0.8])
│   ├── experiment2_stratification.csv     # Ancestral stratification dilution (Delta in [0.2, 1.0])
│   ├── experiment3_feedback.csv           # Social feedback sweep (beta in [0.10, 0.50])
│   ├── experiment4_combined.csv           # Unconfounded mechanism deconstruction (5 conditions)
│   ├── experiment5_factorial_grid.csv     # Full 4 x 3 factorial grid (N = 60) for ANOVA
│   ├── experiment6_belief_withdrawal.csv  # Generational inertia & counterfactual withdrawal
│   ├── experiment7_sensitivity_robustness.csv # Symmetric scales & bidirectional mate choice
│   ├── anova_results.csv                  # Complete 2-Way Factorial ANOVA table
│   └── summary_metrics.csv                # Exact empirical metrics for Table 1
└── figures/                               # Clean figures (strictly <= 800px width, no in-image text)
    ├── fig1_assortative_mating.png
    ├── fig2_population_stratification.png
    ├── fig3_social_feedback.png
    └── fig4_model_comparisons.png
```

---

## ⚙️ Model Architecture & Equations

The simulation implements Fisher's (1918) infinitesimal polygenic model combined with Mendelian segregation at the ABO locus on chromosome 9q34.2:

$$
P_c = \frac{1}{2} G_m + \frac{1}{2} G_f + \varepsilon_{\text{seg}} + E_c + \beta S(X_c)
$$

- **Additive Genetic Inheritance:** $G_c = 0.5 G_m + 0.5 G_f + \varepsilon_{\text{seg}}$, where $\varepsilon_{\text{seg}} \sim \mathcal{N}(0, 0.5 h^2)$.
- **Environmental Component:** $E_c \sim \mathcal{N}(0, 1 - h^2)$ independently sampled for each offspring.
- **Social Labeling Feedback:** $F_c = \beta S(X_c)$, where $S(X_c)$ maps ABO blood groups to cultural stereotype scores ($A = -1.0, B = +1.0, O = +0.5, AB = 0.0$).
- **Assortative Mating:** With probability $\alpha$, mating pairs choose candidates that minimize $|P_i - S(X_j)|$ from a candidate pool of $k = 5$.
- **RNG Management:** Master seed `SeedSequence(20261010)` spawns independent streams per experimental module and repetition.

---

## 🚀 Quick Start & Reproduction

### 1. Installation

Clone this repository and install dependencies:

```bash
git clone https://github.com/Suhyun211/blood-type-personality-abm.git
cd blood-type-personality-abm
pip install -r requirements.txt
```

### 2. One-Click Full Reproduction & Verification

Execute the master reproduction script:

```bash
python run_reproduction.py
```

This single command automatically executes:
1. Multi-generational simulation across all 7 experimental modules.
2. Two-way factorial ANOVA pipeline on the $4 \times 3$ grid ($N = 60$).
3. Generation of all publication-quality Figures 1 to 4 in `figures/` and packaging into `paper/figures_JASSS.zip`.
4. Automated numerical regression assertions verifying all Table 1 benchmarks, ANOVA F-ratios, and belief withdrawal dynamics.

### 3. Step-by-Step Execution

```bash
# Step 1: Run ABM simulation suite (saves all CSV datasets to data/)
python src/simulation.py

# Step 2: Run ANOVA, generate figures, and calculate summary metrics
python src/analytics.py
```

---

## 📊 Summary of Empirical Findings (Generation 25)

The table below summarizes the exact empirical results replicated across 5 independent Monte Carlo runs per condition ($N = 5,000$ agents, 25 generations):

| Theoretical Model / Condition | Phenotypic Correlation (*r_P*) | Std. Dev. (*σ*) | Explained Variance (*R*²) | Cohen's *d* (*B* vs *A*) | Empirical Verdict |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Null Control** (α = 0, β = 0) | -0.010 | 0.008 | 0.01% | -0.017 | Theorem 1 Confirmed: Parallel transmission preserves independence |
| **Weak Assortative** (α = 0.2) | 0.025 | 0.018 | 0.06% | 0.050 | Sub-benchmark: Mating preference alone accumulates negligibly |
| **Strong Assortative** (α = 0.8) | 0.139 | 0.025 | 1.92% | 0.343 | Exceeds benchmark only under severe, unrealistic mating constraints |
| **Stratification** (Δ = 0.5 SD) | -0.000 | 0.013 | 0.00% | 0.007 | Dissipates within 3–5 generations under panmictic intermarriage |
| **Social Feedback Mild** (β = 0.10) | 0.079 | 0.017 | 0.63% | 0.195 | Quasi-instantaneous developmental shift (analytical: *r* ≈ 0.0827) |
| **Social Feedback Moderate** (β = 0.25) | 0.199 | 0.017 | 3.98% | 0.494 | Matches closed-form analytical benchmark (*d* → 2β = 0.50) |
| **Coupled Pure Model** (α = 0.15, β = 0.10) | **0.102** | **0.014** | **1.05%** | **0.247** | **Aligns with Cohen's (1988) small-effect benchmark (*r* = 0.10)** |
| **Coupled + Stratified** (α = 0.15, β = 0.10, Δ = 0.2) | 0.104 | 0.022 | 1.09% | 0.255 | Similar to Coupled Pure; stratification adds no persistent effect |

---

## 📈 Two-Way Factorial ANOVA Results ($4 \times 3$ Grid, $N = 60$)

- **Assortative Mating ($\alpha$):** $F(3, 48) = 282.23$, $p < 0.001$, $\eta_p^2 = 0.946$
- **Social Feedback ($\beta$):** $F(2, 48) = 1016.64$, $p < 0.001$, $\eta_p^2 = 0.977$
- **Interaction ($\alpha \times \beta$):** $F(6, 48) = 0.50$, $p = 0.805$ (non-significant), $\eta_p^2 = 0.059$

*Interpretation:* The absence of a statistically significant interaction is compatible with an approximately additive combination of cultural mechanisms within the tested parameter regime.

---

## 🔄 Cultural Belief Withdrawal & Generational Inertia

In Experiment 6, cultural beliefs ($\alpha = 0.15, \beta = 0.10$) are active for the first 10 generations, and counterfactually withdrawn at Generation 10 ($N = 20$ independent Monte Carlo replications with 95% confidence intervals):
- **Complete Withdrawal ($\alpha = 0, \beta = 0$):** Phenotypic correlation collapses quasi-instantaneously to $r_P = 0.009 \pm 0.007$ at Generation 11, dissipating to $r_P = -0.002 \pm 0.008$ (95% CI $[-0.011, 0.006]$) and $r_G = -0.005 \pm 0.007$ (95% CI $[-0.012, 0.002]$) by Generation 25 under panmixia.
- **Feedback Cessation ($\beta = 0$, $\alpha = 0.15$ maintained):** Expressed correlation drops immediately to $r_P = 0.022 \pm 0.008$ at Generation 11, unmasking the underlying genetic-component association ($r_G = 0.034 \pm 0.007$). Because mate choice continues to sort on phenotypic personality, this latent cross-trait genetic association persists stably across subsequent cohorts ($r_G = 0.032 \pm 0.007$, with 95% CI $[0.026, 0.039]$ strictly excluding zero at Generation 25), demonstrating generational inertia.

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
