#!/usr/bin/env python3
"""
Master Reproduction Script for:
'Can Cultural Beliefs Generate Spurious Blood-Type–Personality Associations?
 An Agent-Based Simulation and Causal Modeling of the Blood-Type Personality Myth'

Journal of Artificial Societies and Social Simulation (JASSS)
Author: Suhyun Kim (Korea University College of Medicine)

This script automates the complete replication pipeline:
1. Multi-generational agent-based simulation across all experimental conditions
   (Null, Assortative Mating, Stratification, Social Feedback, Pure Coupled, Coupled+Stratified,
    Factorial Grid, Belief Withdrawal, and Robustness Checks)
2. Statistical analysis, 2-Way Factorial ANOVA, and Cohen's d evaluations
3. Generation of publication-quality Figures 1 to 4 (strict JASSS graphics compliance, <=800px width)
4. Rigorous numerical verification of all Table 1 empirical metrics and ANOVA tables
"""

import os
import sys
import subprocess
import pandas as pd
import numpy as np

def run_step(step_name, module_path):
    print(f"\n==========================================")
    print(f"[*] Running: {step_name}")
    print(f"[*] Executing: {module_path}")
    print(f"==========================================")
    res = subprocess.run([sys.executable, module_path], capture_output=True, text=True)
    if res.stdout:
        print(res.stdout)
    if res.stderr:
        # Filter benign matplotlib font cache warnings
        filtered_err = "\n".join([line for line in res.stderr.splitlines() if "matplotlib" not in line.lower() and "failed to find real location" not in line.lower()])
        if filtered_err.strip():
            print(filtered_err, file=sys.stderr)
    if res.returncode != 0:
        print(f"[!] Error executing {module_path}. Return code: {res.returncode}")
        sys.exit(res.returncode)
    print(f"[OK] {step_name} completed successfully.")

def verify_results(base_dir):
    print(f"\n==========================================")
    print(f"[*] Verifying Simulation Datasets, Figures, and Statistical Metrics")
    print(f"==========================================")
    
    data_dir = os.path.join(base_dir, "data")
    fig_dir = os.path.join(base_dir, "figures")
    paper_dir = os.path.join(base_dir, "paper")
    
    # 1. Verify existence and integrity of all simulation datasets
    expected_data = [
        ("experiment1_assortative.csv", 500),
        ("experiment2_stratification.csv", 375),
        ("experiment3_feedback.csv", 375),
        ("experiment4_combined.csv", 625),
        ("experiment5_factorial_grid.csv", 1500),
        ("experiment6_belief_withdrawal.csv", 390),
        ("experiment7_sensitivity_robustness.csv", 250),
        ("anova_results.csv", 4),
        ("summary_metrics.csv", 8)
    ]
    for fname, min_rows in expected_data:
        p = os.path.join(data_dir, fname)
        assert os.path.exists(p), f"Missing required data file: {p}"
        df = pd.read_csv(p)
        assert len(df) >= min_rows, f"Insufficient records in {fname}: expected >= {min_rows}, got {len(df)}"
        print(f"[OK] {fname}: {len(df)} records verified.")

    # 2. Verify existence and size of clean figures
    expected_figs = [
        "fig1_assortative_mating.png",
        "fig2_population_stratification.png",
        "fig3_social_feedback.png",
        "fig4_model_comparisons.png"
    ]
    for fname in expected_figs:
        p = os.path.join(fig_dir, fname)
        assert os.path.exists(p), f"Missing figure file: {p}"
        size_kb = os.path.getsize(p) / 1024
        assert size_kb > 20, f"Figure file suspiciously small ({size_kb} KB): {fname}"
        print(f"[OK] {fname} ({size_kb:.1f} KB): verified.")

    # Check zip archive
    zip_path = os.path.join(paper_dir, "figures_JASSS.zip")
    assert os.path.exists(zip_path), f"Missing figure zip: {zip_path}"
    print(f"[OK] figures_JASSS.zip ({os.path.getsize(zip_path)/1024:.1f} KB): verified.")

    # 3. Rigorous numerical assertions on key empirical metrics
    df_sum = pd.read_csv(os.path.join(data_dir, "summary_metrics.csv")).set_index('Model')
    
    # 3a. Coupled Pure Model
    cp = df_sum.loc['Coupled Pure Model (alpha = 0.15, beta = 0.10)']
    np.testing.assert_allclose(cp['r_mean'], 0.102, atol=0.015,
                               err_msg="Coupled Pure Model mean r deviated beyond tolerance!")
    print(f"\n[Verification] Coupled Pure Model (alpha=0.15, beta=0.10):")
    print(f"  Observed: r = {cp['r_mean']:.3f} +/- {cp['r_std']:.3f} (Table 1: 0.102)")
    print(f"  R^2 = {cp['r2_pct']:.2f}% | Cohen's d = {cp['cohens_d']:.3f}")

    # 3b. Social Feedback Moderate (beta = 0.25)
    fbm = df_sum.loc['Social Feedback Moderate (beta = 0.25)']
    np.testing.assert_allclose(fbm['r_mean'], 0.199, atol=0.015,
                               err_msg="Social Feedback (beta=0.25) mean r deviated beyond tolerance!")
    np.testing.assert_allclose(fbm['cohens_d'], 0.494, atol=0.040,
                               err_msg="Social Feedback Cohen's d deviated beyond tolerance!")
    print(f"\n[Verification] Social Feedback (beta=0.25):")
    print(f"  Observed: r = {fbm['r_mean']:.3f} | Cohen's d = {fbm['cohens_d']:.3f} (Theoretical benchmark: d ~ 0.50)")

    # 3c. Factorial ANOVA verification
    df_anova = pd.read_csv(os.path.join(data_dir, "anova_results.csv"), index_col=0)
    
    f_alpha = df_anova.loc['C(alpha)', 'F']
    f_beta = df_anova.loc['C(beta)', 'F']
    f_inter = df_anova.loc['C(alpha):C(beta)', 'F']
    p_inter = df_anova.loc['C(alpha):C(beta)', 'PR(>F)']
    
    assert f_alpha > 100.0, f"ANOVA alpha main effect F too low: {f_alpha}"
    assert f_beta > 500.0, f"ANOVA beta main effect F too low: {f_beta}"
    assert p_inter > 0.05, f"ANOVA interaction unexpectedly significant (p={p_inter})"
    print(f"\n[Verification] Two-Way Factorial ANOVA on 4x3 Grid (N = 60):")
    print(f"  Main effect alpha: F(3, 48) = {f_alpha:.2f}, p < 0.001, eta_p^2 = {df_anova.loc['C(alpha)', 'eta_p2']:.3f}")
    print(f"  Main effect beta:  F(2, 48) = {f_beta:.2f}, p < 0.001, eta_p^2 = {df_anova.loc['C(beta)', 'eta_p2']:.3f}")
    print(f"  Interaction:       F(6, 48) = {f_inter:.2f}, p = {p_inter:.3f} (non-significant), eta_p^2 = {df_anova.loc['C(alpha):C(beta)', 'eta_p2']:.3f}")

    # 3d. Belief Withdrawal dynamics check
    df_bw = pd.read_csv(os.path.join(data_dir, "experiment6_belief_withdrawal.csv"))
    r_sust_g24 = df_bw[(df_bw['scenario'] == 'Sustained') & (df_bw['gen'] == 24)]['corr'].mean()
    r_stop_g24 = df_bw[(df_bw['scenario'] == 'Complete_Withdrawal') & (df_bw['gen'] == 24)]['corr'].mean()
    assert r_sust_g24 > 0.08, f"Sustained belief failed to maintain correlation at Gen 24: {r_sust_g24}"
    assert abs(r_stop_g24) < 0.02, f"Complete withdrawal failed to dissipate correlation at Gen 24: {r_stop_g24}"
    print(f"\n[Verification] Belief Withdrawal & Generational Inertia Dynamic:")
    print(f"  Sustained at Gen 24: r = {r_sust_g24:.3f}")
    print(f"  Complete Withdrawal at Gen 24: r = {r_stop_g24:.3f} (diluted to zero)")

    print("\n==========================================")
    print("[OK] ALL SIMULATION AND STATISTICAL METRICS REPRODUCED FLAWLESSLY!")
    print("==========================================")

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sim_script = os.path.join(base_dir, "src", "simulation.py")
    analytics_script = os.path.join(base_dir, "src", "analytics.py")

    # Step 1: Simulation
    run_step("Multi-Generational ABM Simulation Suite", sim_script)
    # Step 2: Analytics, ANOVA, and Figures
    run_step("Statistical Analytics, ANOVA & Figure Generation", analytics_script)
    # Step 3: Verification
    verify_results(base_dir)
