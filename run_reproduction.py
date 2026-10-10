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
        ("experiment6_belief_withdrawal.csv", 1500),
        ("experiment7_sensitivity_robustness.csv", 250),
        ("anova_results.csv", 4),
        ("summary_metrics.csv", 8)
    ]
    for fname, min_rows in expected_data:
        p = os.path.join(data_dir, fname)
        assert os.path.exists(p), f"Missing required data file: {p}"
        df = pd.read_csv(p)
        assert len(df) >= min_rows, f"Insufficient records in {fname}: expected >= {min_rows}, got {len(df)}"
        # Verify unique seed generation and spawn_key traceability
        if 'seed' in df.columns:
            assert df['seed'].nunique() > 1, f"Seed values in {fname} are not distinct!"
            assert 'spawn_key' in df.columns, f"spawn_key missing in {fname}!"
        print(f"[OK] {fname}: {len(df)} records verified (distinct seeds and spawn_key confirmed).")

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

    # Check zip archive (in figures/ for standalone reproducibility, and paper/ if present)
    zip_path_fig = os.path.join(fig_dir, "figures_JASSS.zip")
    assert os.path.exists(zip_path_fig), f"Missing figure zip: {zip_path_fig}"
    print(f"[OK] figures/figures_JASSS.zip ({os.path.getsize(zip_path_fig)/1024:.1f} KB): verified.")
    if os.path.exists(paper_dir):
        zip_path_paper = os.path.join(paper_dir, "figures_JASSS.zip")
        if os.path.exists(zip_path_paper):
            print(f"[OK] paper/figures_JASSS.zip ({os.path.getsize(zip_path_paper)/1024:.1f} KB): verified.")

    # 3. Rigorous numerical assertions on key empirical metrics (Table 1)
    df_sum = pd.read_csv(os.path.join(data_dir, "summary_metrics.csv")).set_index('Model')
    
    # 3a. Table 1: All eight condition benchmarks
    t1_expected = {
        'Null Control (Pure Random Mating)': (-0.010, 0.008, -0.017),
        'Weak Assortative (alpha = 0.2)': (0.025, 0.018, 0.050),
        'Strong Assortative (alpha = 0.8)': (0.139, 0.025, 0.343),
        'Stratification (Delta = 0.5 SD)': (-0.000, 0.013, 0.007),
        'Social Feedback Mild (beta = 0.10)': (0.079, 0.017, 0.195),
        'Social Feedback Moderate (beta = 0.25)': (0.199, 0.017, 0.494),
        'Coupled Pure Model (alpha = 0.15, beta = 0.10)': (0.102, 0.014, 0.247),
        'Coupled + Stratified (alpha = 0.15, beta = 0.10, Delta = 0.2)': (0.104, 0.022, 0.255)
    }

    print("\n[Verification] Validating Table 1 Empirical Benchmarks (N=5 MC runs per condition):")
    for cond_name, (exp_r, exp_std, exp_d) in t1_expected.items():
        row = df_sum.loc[cond_name]
        np.testing.assert_allclose(row['r_mean'], exp_r, atol=0.015,
                                  err_msg=f"{cond_name} mean r deviated beyond tolerance!")
        np.testing.assert_allclose(row['r_std'], exp_std, atol=0.015,
                                  err_msg=f"{cond_name} std r deviated beyond tolerance!")
        np.testing.assert_allclose(row['cohens_d'], exp_d, atol=0.040,
                                  err_msg=f"{cond_name} Cohen's d deviated beyond tolerance!")
        print(f"  [OK] {cond_name}: r = {row['r_mean']:.3f} +/- {row['r_std']:.3f} | Cohen's d = {row['cohens_d']:.3f}")

    # 3b. Factorial ANOVA verification (4x3 Grid, N = 60)
    df_anova = pd.read_csv(os.path.join(data_dir, "anova_results.csv"), index_col=0)
    
    f_alpha = df_anova.loc['C(alpha)', 'F']
    f_beta = df_anova.loc['C(beta)', 'F']
    f_inter = df_anova.loc['C(alpha):C(beta)', 'F']
    p_inter = df_anova.loc['C(alpha):C(beta)', 'PR(>F)']
    
    np.testing.assert_allclose(f_alpha, 282.23, rtol=0.05, err_msg="ANOVA alpha F deviated!")
    np.testing.assert_allclose(f_beta, 1016.64, rtol=0.05, err_msg="ANOVA beta F deviated!")
    assert p_inter > 0.05, f"ANOVA interaction unexpectedly significant (p={p_inter})"
    print(f"\n[Verification] Two-Way Factorial ANOVA on 4x3 Grid (N = 60):")
    print(f"  Main effect alpha: F(3, 48) = {f_alpha:.2f}, p < 0.001, eta_p^2 = {df_anova.loc['C(alpha)', 'eta_p2']:.3f}")
    print(f"  Main effect beta:  F(2, 48) = {f_beta:.2f}, p < 0.001, eta_p^2 = {df_anova.loc['C(beta)', 'eta_p2']:.3f}")
    print(f"  Interaction:       F(6, 48) = {f_inter:.2f}, p = {p_inter:.3f} (non-significant), eta_p^2 = {df_anova.loc['C(alpha):C(beta)', 'eta_p2']:.3f}")

    # 3c. Belief Withdrawal dynamics check (N = 20 MC runs)
    df_bw = pd.read_csv(os.path.join(data_dir, "experiment6_belief_withdrawal.csv"))
    
    # Gen 24/25 checks
    g25_sust = df_bw[(df_bw['scenario'] == 'Sustained') & (df_bw['gen'] == 25)]
    g25_fc = df_bw[(df_bw['scenario'] == 'Feedback_Cessation') & (df_bw['gen'] == 25)]
    g25_cw = df_bw[(df_bw['scenario'] == 'Complete_Withdrawal') & (df_bw['gen'] == 25)]
    
    # 95% CIs
    fc_rg_mean = g25_fc['corr_genetic'].mean()
    fc_rg_ci = 1.96 * (g25_fc['corr_genetic'].std() / np.sqrt(len(g25_fc)))
    cw_rg_mean = g25_cw['corr_genetic'].mean()
    cw_rg_ci = 1.96 * (g25_cw['corr_genetic'].std() / np.sqrt(len(g25_cw)))

    # Feedback Cessation maintains latent genetic association significantly above zero
    assert (fc_rg_mean - fc_rg_ci) > 0.020, f"Feedback Cessation 95% CI lower bound not strictly positive: {fc_rg_mean - fc_rg_ci}"
    # Complete Withdrawal genetic association collapses to zero (CI spans 0)
    assert abs(cw_rg_mean) < 0.015, f"Complete Withdrawal failed to dissipate: {cw_rg_mean}"
    assert (cw_rg_mean - cw_rg_ci) <= 0.0 <= (cw_rg_mean + cw_rg_ci), "Complete Withdrawal CI does not span zero!"

    print(f"\n[Verification] Belief Withdrawal & Generational Inertia Dynamic (N = 20 MC runs):")
    print(f"  Sustained at Gen 25: r_P = {g25_sust['corr'].mean():.3f} | r_G = {g25_sust['corr_genetic'].mean():.3f}")
    print(f"  Feedback Cessation Gen 25: r_P = {g25_fc['corr'].mean():.3f} | r_G = {fc_rg_mean:.3f} +/- {fc_rg_ci:.3f} (95% CI: [{fc_rg_mean-fc_rg_ci:.3f}, {fc_rg_mean+fc_rg_ci:.3f}])")
    print(f"  Complete Withdrawal Gen 25: r_P = {g25_cw['corr'].mean():.3f} | r_G = {cw_rg_mean:.3f} +/- {cw_rg_ci:.3f} (95% CI: [{cw_rg_mean-cw_rg_ci:.3f}, {cw_rg_mean+cw_rg_ci:.3f}])")

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
