"""
Statistical Analytics, ANOVA Pipeline, and Publication Figure Suite
Strictly Compliant with JASSS Guidelines:
- Figures <= 800 pixels in width (typical 750-780 x 480-500px, 100 DPI)
- NO in-image figure captions (titles/captions in manuscript text only)
- Automated Two-Way Factorial ANOVA calculation and output table
- Multi-Generational Generational Inertia and Belief Withdrawal Visualization
- Automated packaging of figures into paper/figures_JASSS.zip
"""

import os
import zipfile
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import statsmodels.api as sm
from statsmodels.formula.api import ols

# Set styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
mpl.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
mpl.rcParams['axes.edgecolor'] = '#333333'
mpl.rcParams['axes.linewidth'] = 0.8
mpl.rcParams['font.size'] = 10.5

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
FIGURES_DIR = os.path.join(BASE_DIR, "figures")
PAPER_DIR = os.path.join(BASE_DIR, "paper")
os.makedirs(FIGURES_DIR, exist_ok=True)
os.makedirs(PAPER_DIR, exist_ok=True)


def compute_anova_pipeline():
    """
    Compute 2-way Factorial ANOVA on Generation 25 data from Experiment 5:
    Factors: alpha (4 levels: 0.0, 0.2, 0.5, 0.8) x beta (3 levels: 0.0, 0.10, 0.25)
    Repetitions: 5 per cell (Total N = 60 observations)
    Computes SS, df, F, p-value, and partial eta-squared (eta_p^2).
    """
    print("\n--- Running 2-Way Factorial ANOVA Pipeline ---")
    grid_path = os.path.join(DATA_DIR, "experiment5_factorial_grid.csv")
    df_grid = pd.read_csv(grid_path)
    
    # Filter to Generation 25 (gen == 24)
    df_gen25 = df_grid[df_grid['gen'] == 24].copy()
    
    # Fit OLS model with interaction
    model = ols('corr ~ C(alpha) + C(beta) + C(alpha):C(beta)', data=df_gen25).fit()
    anova_table = sm.stats.anova_lm(model, typ=2)
    
    # Compute partial eta-squared: SS_effect / (SS_effect + SS_residual)
    ss_resid = anova_table.loc['Residual', 'sum_sq']
    anova_table['eta_p2'] = anova_table['sum_sq'] / (anova_table['sum_sq'] + ss_resid)
    # Residual eta_p2 set to NaN
    anova_table.loc['Residual', 'eta_p2'] = np.nan
    
    anova_path = os.path.join(DATA_DIR, "anova_results.csv")
    anova_table.to_csv(anova_path)
    print(f"Saved ANOVA table to: {anova_path}")
    print(anova_table[['df', 'sum_sq', 'F', 'PR(>F)', 'eta_p2']])
    
    return anova_table


def compute_summary_metrics():
    """
    Compute and aggregate exact statistical metrics across all key experimental models
    at Generation 25 for Table 1 and manuscript reporting.
    """
    print("\n--- Computing Empirical Summary Metrics for Table 1 ---")
    df_exp1 = pd.read_csv(os.path.join(DATA_DIR, "experiment1_assortative.csv"))
    df_exp2 = pd.read_csv(os.path.join(DATA_DIR, "experiment2_stratification.csv"))
    df_exp3 = pd.read_csv(os.path.join(DATA_DIR, "experiment3_feedback.csv"))
    df_exp4 = pd.read_csv(os.path.join(DATA_DIR, "experiment4_combined.csv"))

    summary_rows = []

    # 1. Null Control
    null_sub = df_exp4[df_exp4['condition'] == 'Null_Control'].query('gen == 24')
    r_null = null_sub['corr'].mean()
    s_null = null_sub['corr'].std()
    summary_rows.append({
        'Model': 'Null Control (Pure Random Mating)',
        'r_mean': r_null,
        'r_std': s_null,
        'r_ci95_low': r_null - 1.96 * (s_null / np.sqrt(len(null_sub))),
        'r_ci95_high': r_null + 1.96 * (s_null / np.sqrt(len(null_sub))),
        'r_genetic': null_sub['corr_genetic'].mean(),
        'r2_pct': (r_null**2) * 100,
        'cohens_d': null_sub['cohens_d'].mean(),
        'verdict': 'Consistent with independence assumption (r ~ 0)'
    })

    # 2. Weak Assortative (alpha = 0.2)
    a_weak = df_exp1[df_exp1['assortative_strength'] == 0.2].query('gen == 24')
    r_aw = a_weak['corr'].mean()
    s_aw = a_weak['corr'].std()
    summary_rows.append({
        'Model': 'Weak Assortative (alpha = 0.2)',
        'r_mean': r_aw,
        'r_std': s_aw,
        'r_ci95_low': r_aw - 1.96 * (s_aw / np.sqrt(len(a_weak))),
        'r_ci95_high': r_aw + 1.96 * (s_aw / np.sqrt(len(a_weak))),
        'r_genetic': a_weak['corr_genetic'].mean(),
        'r2_pct': (r_aw**2) * 100,
        'cohens_d': a_weak['cohens_d'].mean(),
        'verdict': 'Sub-benchmark (Negligible accumulation)'
    })

    # 3. Strong Assortative (alpha = 0.8)
    a_str = df_exp1[df_exp1['assortative_strength'] == 0.8].query('gen == 24')
    r_as = a_str['corr'].mean()
    s_as = a_str['corr'].std()
    summary_rows.append({
        'Model': 'Strong Assortative (alpha = 0.8)',
        'r_mean': r_as,
        'r_std': s_as,
        'r_ci95_low': r_as - 1.96 * (s_as / np.sqrt(len(a_str))),
        'r_ci95_high': r_as + 1.96 * (s_as / np.sqrt(len(a_str))),
        'r_genetic': a_str['corr_genetic'].mean(),
        'r2_pct': (r_as**2) * 100,
        'cohens_d': a_str['cohens_d'].mean(),
        'verdict': 'Exceeds benchmark (Severe cultural constraint)'
    })

    # 4. Stratification (Delta = 0.5)
    strat_sub = df_exp2[df_exp2['strat_diff'] == 0.5].query('gen == 24')
    r_strat = strat_sub['corr'].mean()
    s_strat = strat_sub['corr'].std()
    summary_rows.append({
        'Model': 'Stratification (Delta = 0.5 SD)',
        'r_mean': r_strat,
        'r_std': s_strat,
        'r_ci95_low': r_strat - 1.96 * (s_strat / np.sqrt(len(strat_sub))),
        'r_ci95_high': r_strat + 1.96 * (s_strat / np.sqrt(len(strat_sub))),
        'r_genetic': strat_sub['corr_genetic'].mean(),
        'r2_pct': (r_strat**2) * 100,
        'cohens_d': strat_sub['cohens_d'].mean(),
        'verdict': 'Dissipated within 5 generations under panmixia'
    })

    # 5. Social Feedback Mild (beta = 0.10)
    fb_mild = df_exp3[df_exp3['feedback_strength'] == 0.10].query('gen == 24')
    r_fbm = fb_mild['corr'].mean()
    s_fbm = fb_mild['corr'].std()
    summary_rows.append({
        'Model': 'Social Feedback Mild (beta = 0.10)',
        'r_mean': r_fbm,
        'r_std': s_fbm,
        'r_ci95_low': r_fbm - 1.96 * (s_fbm / np.sqrt(len(fb_mild))),
        'r_ci95_high': r_fbm + 1.96 * (s_fbm / np.sqrt(len(fb_mild))),
        'r_genetic': fb_mild['corr_genetic'].mean(),
        'r2_pct': (r_fbm**2) * 100,
        'cohens_d': fb_mild['cohens_d'].mean(),
        'verdict': 'Quasi-instantaneous developmental shift'
    })

    # 6. Social Feedback Moderate (beta = 0.25)
    fb_mod = df_exp3[df_exp3['feedback_strength'] == 0.25].query('gen == 24')
    r_fbo = fb_mod['corr'].mean()
    s_fbo = fb_mod['corr'].std()
    summary_rows.append({
        'Model': 'Social Feedback Moderate (beta = 0.25)',
        'r_mean': r_fbo,
        'r_std': s_fbo,
        'r_ci95_low': r_fbo - 1.96 * (s_fbo / np.sqrt(len(fb_mod))),
        'r_ci95_high': r_fbo + 1.96 * (s_fbo / np.sqrt(len(fb_mod))),
        'r_genetic': fb_mod['corr_genetic'].mean(),
        'r2_pct': (r_fbo**2) * 100,
        'cohens_d': fb_mod['cohens_d'].mean(),
        'verdict': 'Substantial effect, matches analytical benchmark'
    })

    # 7. Coupled Pure Model (alpha = 0.15, beta = 0.10, strat = False)
    c_pure = df_exp4[df_exp4['condition'] == 'Coupled_Pure'].query('gen == 24')
    r_cp = c_pure['corr'].mean()
    s_cp = c_pure['corr'].std()
    summary_rows.append({
        'Model': 'Coupled Pure Model (alpha = 0.15, beta = 0.10)',
        'r_mean': r_cp,
        'r_std': s_cp,
        'r_ci95_low': r_cp - 1.96 * (s_cp / np.sqrt(len(c_pure))),
        'r_ci95_high': r_cp + 1.96 * (s_cp / np.sqrt(len(c_pure))),
        'r_genetic': c_pure['corr_genetic'].mean(),
        'r2_pct': (r_cp**2) * 100,
        'cohens_d': c_pure['cohens_d'].mean(),
        'verdict': "Aligns with Cohen's benchmark (r = 0.10)"
    })

    # 8. Coupled + Stratified (alpha = 0.15, beta = 0.10, Delta = 0.2)
    c_strat = df_exp4[df_exp4['condition'] == 'Coupled_Stratified'].query('gen == 24')
    r_cs = c_strat['corr'].mean()
    s_cs = c_strat['corr'].std()
    summary_rows.append({
        'Model': 'Coupled + Stratified (alpha = 0.15, beta = 0.10, Delta = 0.2)',
        'r_mean': r_cs,
        'r_std': s_cs,
        'r_ci95_low': r_cs - 1.96 * (s_cs / np.sqrt(len(c_strat))),
        'r_ci95_high': r_cs + 1.96 * (s_cs / np.sqrt(len(c_strat))),
        'r_genetic': c_strat['corr_genetic'].mean(),
        'r2_pct': (r_cs**2) * 100,
        'cohens_d': c_strat['cohens_d'].mean(),
        'verdict': 'Similar to Coupled Pure; stratification dissipated'
    })

    df_sum = pd.DataFrame(summary_rows)
    sum_path = os.path.join(DATA_DIR, "summary_metrics.csv")
    df_sum.to_csv(sum_path, index=False)
    print(f"Saved summary metrics to: {sum_path}")
    print(df_sum[['Model', 'r_mean', 'r_std', 'r2_pct', 'cohens_d']])

    return df_sum


def generate_clean_figures():
    """
    Generate all 4 JASSS-compliant figures (PNG, <= 800px width, NO in-image captions).
    """
    print("\n=== Generating Clean JASSS-Compliant Figures (<= 800px Width) ===")

    # -------------------------------------------------------------
    # Figure 1: Assortative Mating Dynamics across Generations
    # -------------------------------------------------------------
    df_exp1 = pd.read_csv(os.path.join(DATA_DIR, "experiment1_assortative.csv"))
    
    # 750x480 pixels: figsize=(7.5, 4.8), dpi=100
    fig, ax = plt.subplots(figsize=(7.5, 4.8), dpi=100)
    grouped = df_exp1.groupby(['assortative_strength', 'gen'])['corr'].agg(['mean', 'std']).reset_index()
    
    colors = {0.0: '#7f7f7f', 0.2: '#2ca02c', 0.5: '#1f77b4', 0.8: '#d62728'}
    labels = {
        0.0: 'Control (alpha=0.0, Random Mating)',
        0.2: 'Weak Preference (alpha=0.2)',
        0.5: 'Moderate Preference (alpha=0.5)',
        0.8: 'Extreme Preference (alpha=0.8)'
    }

    for alpha in [0.0, 0.2, 0.5, 0.8]:
        sub = grouped[grouped['assortative_strength'] == alpha]
        ax.plot(sub['gen'], sub['mean'], label=labels[alpha], color=colors[alpha], linewidth=2.2)
        ax.fill_between(sub['gen'], sub['mean'] - sub['std'], sub['mean'] + sub['std'], color=colors[alpha], alpha=0.15)

    ax.axhline(0.10, color='black', linestyle='--', alpha=0.6, label="Cohen's Benchmark (r = 0.10)")
    ax.axhline(0.00, color='gray', linestyle=':', alpha=0.5)

    ax.set_xlabel("Generation", fontsize=11, fontweight='bold')
    ax.set_ylabel("Correlation Coefficient (r)", fontsize=11, fontweight='bold')
    ax.set_ylim(-0.05, 0.45)
    ax.legend(frameon=True, facecolor='white', framealpha=0.9, loc='upper left', fontsize=9.5)
    plt.tight_layout()
    fig1_path = os.path.join(FIGURES_DIR, "fig1_assortative_mating.png")
    plt.savefig(fig1_path, dpi=100)
    plt.close()
    print("Saved clean fig1_assortative_mating.png")

    # -------------------------------------------------------------
    # Figure 2: Population Stratification Effect
    # -------------------------------------------------------------
    df_exp2 = pd.read_csv(os.path.join(DATA_DIR, "experiment2_stratification.csv"))
    
    fig, ax = plt.subplots(figsize=(7.5, 4.8), dpi=100)
    grouped2 = df_exp2.groupby(['strat_diff', 'gen'])['corr'].agg(['mean', 'std']).reset_index()
    
    colors2 = {0.2: '#17becf', 0.5: '#ff7f0e', 1.0: '#9467bd'}
    labels2 = {
        0.2: 'Small Gap (Delta = 0.2 SD)',
        0.5: 'Moderate Gap (Delta = 0.5 SD)',
        1.0: 'Large Gap (Delta = 1.0 SD)'
    }

    for diff in [0.2, 0.5, 1.0]:
        sub = grouped2[grouped2['strat_diff'] == diff]
        ax.plot(sub['gen'], sub['mean'], label=labels2[diff], color=colors2[diff], linewidth=2.2)
        ax.fill_between(sub['gen'], sub['mean'] - sub['std'], sub['mean'] + sub['std'], color=colors2[diff], alpha=0.15)

    ax.axhline(0.10, color='black', linestyle='--', alpha=0.6, label="Cohen's Benchmark (r = 0.10)")
    ax.axhline(0.00, color='gray', linestyle=':', alpha=0.5)

    ax.set_xlabel("Generation (Panmictic Intermarriage)", fontsize=11, fontweight='bold')
    ax.set_ylabel("Correlation Coefficient (r)", fontsize=11, fontweight='bold')
    ax.set_ylim(-0.05, 0.45)
    ax.legend(frameon=True, facecolor='white', framealpha=0.9, loc='upper right', fontsize=9.5)
    plt.tight_layout()
    fig2_path = os.path.join(FIGURES_DIR, "fig2_population_stratification.png")
    plt.savefig(fig2_path, dpi=100)
    plt.close()
    print("Saved clean fig2_population_stratification.png")

    # -------------------------------------------------------------
    # Figure 3: Social Feedback (Self-fulfilling Prophecy)
    # -------------------------------------------------------------
    df_exp3 = pd.read_csv(os.path.join(DATA_DIR, "experiment3_feedback.csv"))
    
    # 780x420 pixels: figsize=(7.8, 4.2), dpi=100
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.8, 4.2), dpi=100)
    grouped3 = df_exp3.groupby(['feedback_strength', 'gen']).agg({'corr': ['mean', 'std'], 'cohens_d': ['mean', 'std']}).reset_index()
    
    colors3 = {0.1: '#8c564b', 0.25: '#e377c2', 0.5: '#bcbd22'}
    labels3 = {
        0.1: 'Mild (beta = 0.1)',
        0.25: 'Moderate (beta = 0.25)',
        0.5: 'Strong (beta = 0.5)'
    }

    for beta in [0.1, 0.25, 0.5]:
        sub = grouped3[grouped3['feedback_strength'] == beta]
        ax1.plot(sub['gen'], sub['corr']['mean'], label=labels3[beta], color=colors3[beta], linewidth=2.0)
        ax1.fill_between(sub['gen'], sub['corr']['mean'] - sub['corr']['std'], sub['corr']['mean'] + sub['corr']['std'], color=colors3[beta], alpha=0.15)

        ax2.plot(sub['gen'], sub['cohens_d']['mean'], label=labels3[beta], color=colors3[beta], linewidth=2.0)
        ax2.fill_between(sub['gen'], sub['cohens_d']['mean'] - sub['cohens_d']['std'], sub['cohens_d']['mean'] + sub['cohens_d']['std'], color=colors3[beta], alpha=0.15)

    ax1.axhline(0.10, color='black', linestyle='--', alpha=0.6, label="Benchmark (r=0.10)")
    ax1.set_title("(a) Correlation by Feedback", fontsize=10.5, fontweight='bold')
    ax1.set_xlabel("Generation", fontsize=10)
    ax1.set_ylabel("Correlation (r)", fontsize=10)
    ax1.set_ylim(-0.05, 0.50)
    ax1.legend(frameon=True, loc='upper left', fontsize=8.5)

    ax2.axhline(0.20, color='black', linestyle='--', alpha=0.6, label="Small Effect (d=0.2)")
    ax2.axhline(0.50, color='blue', linestyle=':', alpha=0.6, label="Medium Effect (d=0.5)")
    ax2.set_title("(b) Effect Size (Cohen's d)", fontsize=10.5, fontweight='bold')
    ax2.set_xlabel("Generation", fontsize=10)
    ax2.set_ylabel("Cohen's d (B vs A)", fontsize=10)
    ax2.set_ylim(-0.1, 1.2)
    ax2.legend(frameon=True, loc='upper left', fontsize=8.5)

    plt.tight_layout()
    fig3_path = os.path.join(FIGURES_DIR, "fig3_social_feedback.png")
    plt.savefig(fig3_path, dpi=100)
    plt.close()
    print("Saved clean fig3_social_feedback.png")

    # -------------------------------------------------------------
    # Figure 4: Multi-Panel Model Comparisons & Generational Inertia Dynamics
    # Panel (a): Generation 25 comparisons of 5 unconfounded mechanisms (r_P and r_G)
    # Panel (b): Belief Withdrawal Experiment (Generations 0-25) showing rapid
    #            phenotypic decay vs latent genetic persistence
    # -------------------------------------------------------------
    df_exp4 = pd.read_csv(os.path.join(DATA_DIR, "experiment4_combined.csv"))
    df_exp6 = pd.read_csv(os.path.join(DATA_DIR, "experiment6_belief_withdrawal.csv"))
    
    # Width 7.8 inches x 4.8 inches at 100 DPI = 780 x 480 pixels (Strictly <= 800px)
    fig, (ax_bar, ax_dyn) = plt.subplots(1, 2, figsize=(7.8, 4.6), dpi=100)

    # Subplot (a): Bar comparison of 5 conditions at Gen 25
    cond_order = ['Null_Control', 'Assortative_Only', 'Feedback_Only', 'Coupled_Pure', 'Coupled_Stratified']
    cond_labels = ['Null\nControl', 'Mating\nOnly', 'Feedback\nOnly', 'Coupled\nPure', 'Coupled+\nStrat.']
    
    gen24_4 = df_exp4[df_exp4['gen'] == 24]
    means_P = [gen24_4[gen24_4['condition'] == c]['corr'].mean() for c in cond_order]
    stds_P = [gen24_4[gen24_4['condition'] == c]['corr'].std() for c in cond_order]
    means_G = [gen24_4[gen24_4['condition'] == c]['corr_genetic'].mean() for c in cond_order]
    stds_G = [gen24_4[gen24_4['condition'] == c]['corr_genetic'].std() for c in cond_order]
    
    x = np.arange(len(cond_order))
    width = 0.36
    
    rects1 = ax_bar.bar(x - width/2, means_P, width, yerr=stds_P, capsize=3, label='Phenotypic ($r_P$)',
                        color='#1f77b4', edgecolor='black', alpha=0.85)
    rects2 = ax_bar.bar(x + width/2, means_G, width, yerr=stds_G, capsize=3, label='Genetic ($r_G$)',
                        color='#ff7f0e', edgecolor='black', alpha=0.85)
    
    ax_bar.axhline(0.10, color='red', linestyle='--', linewidth=1.2, label="Benchmark (r=0.10)")
    ax_bar.axhline(0.00, color='gray', linestyle=':', alpha=0.5)
    ax_bar.set_xticks(x)
    ax_bar.set_xticklabels(cond_labels, fontsize=8.5)
    ax_bar.set_ylabel("Correlation (r) at Gen 25", fontsize=9.5, fontweight='bold')
    ax_bar.set_title("(a) Mechanism Deconstruction", fontsize=10, fontweight='bold')
    ax_bar.set_ylim(-0.04, 0.16)
    ax_bar.legend(frameon=True, loc='upper left', fontsize=8.0)

    # Subplot (b): Belief Withdrawal & Generational Inertia Dynamics
    scenarios = ['Sustained', 'Feedback_Cessation', 'Complete_Withdrawal']
    sc_colors = {'Sustained': '#2ca02c', 'Feedback_Cessation': '#9467bd', 'Complete_Withdrawal': '#d62728'}
    sc_labels = {
        'Sustained': 'Sustained (alpha=0.15, beta=0.10)',
        'Feedback_Cessation': 'Feedback Stops at Gen 10 (beta=0)',
        'Complete_Withdrawal': 'Complete Withdrawal at Gen 10'
    }

    grouped6 = df_exp6.groupby(['scenario', 'gen']).agg({'corr': 'mean', 'corr_genetic': 'mean'}).reset_index()

    for sc in scenarios:
        sub = grouped6[grouped6['scenario'] == sc]
        # Phenotypic line (solid)
        ax_dyn.plot(sub['gen'], sub['corr'], color=sc_colors[sc], linewidth=1.8, label=sc_labels[sc])
        # Genetic line (dotted)
        ax_dyn.plot(sub['gen'], sub['corr_genetic'], color=sc_colors[sc], linewidth=1.5, linestyle=':')

    ax_dyn.axvline(10, color='black', linestyle='--', alpha=0.7)
    ax_dyn.text(10.2, 0.135, 'Intervention\n(Gen 10)', fontsize=7.5, color='black', fontweight='bold')
    ax_dyn.axhline(0.10, color='red', linestyle='--', linewidth=1.0, alpha=0.6)
    ax_dyn.axhline(0.00, color='gray', linestyle=':', alpha=0.5)
    
    ax_dyn.set_xlabel("Generation", fontsize=9.5, fontweight='bold')
    ax_dyn.set_ylabel("Correlation (r)", fontsize=9.5, fontweight='bold')
    ax_dyn.set_title("(b) Belief Withdrawal & Inertia", fontsize=10, fontweight='bold')
    ax_dyn.set_ylim(-0.04, 0.16)
    ax_dyn.legend(frameon=True, loc='lower left', fontsize=7.5)

    plt.tight_layout()
    fig4_path = os.path.join(FIGURES_DIR, "fig4_model_comparisons.png")
    plt.savefig(fig4_path, dpi=100)
    plt.close()
    print("Saved clean fig4_model_comparisons.png")

    # -------------------------------------------------------------
    # Package into figures_JASSS.zip for journal upload
    # -------------------------------------------------------------
    zip_path = os.path.join(PAPER_DIR, "figures_JASSS.zip")
    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.write(fig1_path, arcname="fig1_assortative_mating.png")
        zf.write(fig2_path, arcname="fig2_population_stratification.png")
        zf.write(fig3_path, arcname="fig3_social_feedback.png")
        zf.write(fig4_path, arcname="fig4_model_comparisons.png")
    print(f"Packaged figures archive at: {zip_path}")


def main():
    print("=== Starting Statistical Analytics & Publication Figure Suite ===")
    anova_tbl = compute_anova_pipeline()
    sum_df = compute_summary_metrics()
    generate_clean_figures()
    print("\n[OK] All statistical tables and JASSS publication figures generated successfully.")


if __name__ == '__main__':
    main()
