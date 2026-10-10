# Can Cultural Beliefs Generate Spurious Blood-Type–Personality Associations?

### An Agent-Based Simulation and Causal Modeling of the Blood-Type Personality Myth

[![JASSS](<https://img.shields.io/badge/Submitted%20to-JASSS-blue.svg>)](https://www.jasss.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**Author:** Suhyun Kim
**Affiliation:** Korea University College of Medicine, Seoul 02841, Republic of Korea
**Contact:** `ktngus5043@korea.ac.kr`

---

## 📖 Overview

The belief that ABO blood type dictates human personality traits—popularized across East Asia (notably South Korea and Japan) for over half a century—is widely dismissed by molecular geneticists and psychologists as pseudoscientific.

This repository hosts the official open-science replication package for our computational investigation submitted to the **Journal of Artificial Societies and Social Simulation (JASSS)**. Using an agent-based simulation model ($N = 5,000$ agents tracked across 25 discrete generations with independent Monte Carlo replications), we formalize three candidate social and demographic mechanisms capable of generating statistical associations in the absence of biological causality:

1. **Belief-driven assortative mating** ($\alpha$)
2. **Subpopulation stratification and panmictic intermarriage** ($\Delta$)
3. **Social labeling and developmental socialization feedback** ($\beta$)

---

## 📂 Repository Structure

```text
blood-type-personality-abm/
├── README.md                      # Comprehensive documentation and reproduction guide
├── LICENSE                        # MIT License
├── requirements.txt               # Python package dependencies
├── run_reproduction.py            # One-click master replication script
├── src/
│   ├── simulation.py              # Core vectorized agent-based simulation engine (NumPy)
│   └── analytics.py               # Statistical evaluation, ANOVA, and Figure 1–4 generation
├── data/                          # Raw simulation datasets (CSV)
│   ├── experiment1_assortative.csv
│   ├── experiment2_stratification.csv
│   ├── experiment3_feedback.csv
│   ├── experiment4_combined.csv
│   └── summary_metrics.csv
├── figures/                       # Publication-quality figures (strict JASSS graphics compliance)
│   ├── fig1_assortative_mating.png
│   ├── fig2_population_stratification.png
│   ├── fig3_social_feedback.png
│   └── fig4_model_comparisons.png
└── paper/
    ├── Manuscript_JASSS_Full.docx          # Full submission manuscript
    └── Manuscript_JASSS_Anonymised.docx    # Blinded manuscript for peer review
```

---

## ⚙️ Model Architecture & Equations

The simulation implements Fisher's (1918) infinitesimal polygenic model combined with Mendelian segregation at the ABO locus on chromosome 9q34.2:

$$
P_c = \frac{1}{2} G_m + \frac{1}{2} G_f + \varepsilon_{\text{seg}} + E_c + \beta S(X_c)
$$

- **Additive Genetic Inheritance:** $G_c = 0.5 G_m + 0.5 G_f + \varepsilon_{\text{seg}}$, where $\varepsilon_{\text{seg}} \sim \mathcal{N}(0, 0.5 h^2)$.
- **Environmental Component:** $E_c \sim \mathcal{N}(0, 1 - h^2)$ independently sampled each generation.
- **Social Labeling Feedback:** $F_c = \beta S(X_c)$, where $S(X_c)$ maps ABO blood groups to cultural stereotype scores ($A = -1.0, B = +1.0, O = +0.5, AB = 0.0$).
- **Assortative Mating:** With probability $\alpha$, mating pairs choose candidates that minimize $|P_i - S(X_j)|$ from a candidate pool of $k = 5$.

---

## 🚀 Quick Start & Reproduction

### 1. Installation

Clone this repository and install dependencies:

```bash
git clone https://github.com/Suhyun211/blood-type-personality-abm.git
cd blood-type-personality-abm
pip install -r requirements.txt
```

### 2. One-Click Full Reproduction

Execute the master reproduction script:

```bash
python run_reproduction.py
```

This single command executes:

- All 5 multi-generational simulation experiments ($N = 5,000$, 25 generations, 5 Monte Carlo runs per condition).
- Statistical analysis, two-way factorial ANOVA, and effect size calculations.
- Re-generation of all publication figures in `figures/`.
- Automated numerical verification against the published manuscript benchmarks.

### 3. Step-by-Step Execution

Alternatively, execute the modules individually:

```bash
# Step 1: Run ABM simulation experiments (saves CSV data to data/)
python src/simulation.py

# Step 2: Generate figures and calculate summary metrics
python src/analytics.py
```

---

## 📊 Summary of Key Findings

| Experimental Condition | Generation 25 Correlation (*r*) | Cohen's *d* (*B* vs *A*) | Explained Variance (*R*²) | Theoretical Verdict |
| :--- | :---: | :---: | :---: | :--- |
| **Null Control** (α = 0, β = 0) | -0.003 ± 0.014 | -0.006 ± 0.032 | 0.00% | Theorem 1 Confirmed: Parallel transmission preserves independence |
| **Assortative Mating** (α = 0.2) | 0.031 ± 0.015 | 0.072 ± 0.035 | 0.10% | Sub-benchmark: Mating preference alone is insufficient |
| **Assortative Mating** (α = 0.8) | 0.145 ± 0.006 | 0.342 ± 0.014 | 2.10% | Exceeds benchmark only under implausibly severe social constraints |
| **Stratification** (Δ = 0.5) | -0.007 ± 0.013 | -0.016 ± 0.030 | 0.00% | Dissipates within 3–5 generations under panmictic mixing |
| **Social Feedback** (β = 0.25) | 0.193 ± 0.021 | 0.463 ± 0.046 | 3.72% | Rapid, quasi-instantaneous convergence (*d* → 2β = 0.50) |
| **Coupled Illustrative Model** | **0.108 ± 0.020** | **0.251 ± 0.045** | **1.17%** | **Aligns with Cohen's (1988) small-effect benchmark (*r* = 0.10)** |

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## ✍️ Citation

If you use this model or code in your research, please cite:

```bibtex
@article{kim2026bloodtypeabm,
  author    = {Kim, Suhyun},
  title     = {Can Cultural Beliefs Generate Spurious Blood-Type--Personality Associations? An Agent-Based Simulation and Causal Modeling of the Blood-Type Personality Myth},
  journal   = {Journal of Artificial Societies and Social Simulation},
  year      = {2026},
  note      = {Submitted}
}
```
