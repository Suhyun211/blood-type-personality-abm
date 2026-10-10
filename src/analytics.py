"""
Statistical Analytics and Figure Generation Suite (Strict JASSS Compliance)
Adheres to JASSS Graphic Guidelines:
- DO NOT INCLUDE FIGURE CAPTIONS IN THE IMAGES
- Graphics scaled to <= 800 pixels in width (typical 750x500px, 100-120 DPI)
- PNG format preferred
- Separate archive zip creation for submission
"""

import os
import zipfile
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
mpl.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
mpl.rcParams['axes.edgecolor'] = '#333333'
mpl.rcParams['axes.linewidth'] = 0.8
mpl.rcParams['font.size'] = 11

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGURES_DIR = os.path.join(BASE_DIR, "figures")
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(FIGURES_DIR, exist_ok=True)

def generate_clean_figures():
    print("=== Generating JASSS-Compliant Clean Figures (No In-Image Captions, <=800px width) ===")

    # -------------------------------------------------------------
    # Figure 1: Assortative Mating Dynamics across Generations
    # -------------------------------------------------------------
    df_exp1 = pd.read_csv(os.path.join(DATA_DIR, "experiment1_assortative.csv"))
    
    # Target 750x480 pixels: figsize=(7.5, 4.8), dpi=100
    fig, ax = plt.subplots(figsize=(7.5, 4.8), dpi=100)
    grouped = df_exp1.groupby(['assortative_strength', 'gen'])['corr'].agg(['mean', 'std']).reset_index()
    
    colors = {0.0: '#7f7f7f', 0.2: '#2ca02c', 0.5: '#1f77b4', 0.8: '#d62728'}
    labels = {
        0.0: 'Control (alpha=0.0, Random Mating)',
        0.2: 'Weak Belief (alpha=0.2)',
        0.5: 'Moderate Belief (alpha=0.5)',
        0.8: 'Extreme Belief (alpha=0.8)'
    }

    for alpha in [0.0, 0.2, 0.5, 0.8]:
        sub = grouped[grouped['assortative_strength'] == alpha]
        ax.plot(sub['gen'], sub['mean'], label=labels[alpha], color=colors[alpha], linewidth=2.2)
        ax.fill_between(sub['gen'], sub['mean'] - sub['std'], sub['mean'] + sub['std'], color=colors[alpha], alpha=0.15)

    ax.axhline(0.10, color='black', linestyle='--', alpha=0.6, label="Cohen's Benchmark (r = 0.10)")
    ax.axhline(0.00, color='gray', linestyle=':', alpha=0.5)

    # NO FIGURE CAPTION IN THE IMAGE (JASSS rule)
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

    # NO FIGURE CAPTION IN THE IMAGE
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

    # NO SUPTITLE / IN-IMAGE CAPTION
    plt.tight_layout()
    fig3_path = os.path.join(FIGURES_DIR, "fig3_social_feedback.png")
    plt.savefig(fig3_path, dpi=100)
    plt.close()
    print("Saved clean fig3_social_feedback.png")

    # -------------------------------------------------------------
    # Figure 4: Realistic Scenario Comparison
    # -------------------------------------------------------------
    df_real = pd.read_csv(os.path.join(DATA_DIR, "experiment4_combined.csv"))
    
    summary_data = []
    null_final = df_exp1[df_exp1['assortative_strength'] == 0.0].query('gen == 24')['corr']
    summary_data.append({'Model': 'Null Control\n(Random)', 'corr': null_final.mean(), 'std': null_final.std()})
    
    a_weak = df_exp1[df_exp1['assortative_strength'] == 0.2].query('gen == 24')['corr']
    summary_data.append({'Model': 'Weak Assort.\n(alpha=0.2)', 'corr': a_weak.mean(), 'std': a_weak.std()})
    
    a_strong = df_exp1[df_exp1['assortative_strength'] == 0.8].query('gen == 24')['corr']
    summary_data.append({'Model': 'Strong Assort.\n(alpha=0.8)', 'corr': a_strong.mean(), 'std': a_strong.std()})

    strat_mod = df_exp2[df_exp2['strat_diff'] == 0.5].query('gen == 24')['corr']
    summary_data.append({'Model': 'Stratification\n(Delta=0.5)', 'corr': strat_mod.mean(), 'std': strat_mod.std()})

    fb_mod = df_exp3[df_exp3['feedback_strength'] == 0.25].query('gen == 24')['corr']
    summary_data.append({'Model': 'Social Feedback\n(beta=0.25)', 'corr': fb_mod.mean(), 'std': fb_mod.std()})

    real_final = df_real.query('gen == 24')['corr']
    summary_data.append({'Model': 'Coupled\nIllustrative', 'corr': real_final.mean(), 'std': real_final.std()})

    df_summary = pd.DataFrame(summary_data)
    
    fig, ax = plt.subplots(figsize=(7.6, 4.8), dpi=100)
    bars = ax.bar(df_summary['Model'], df_summary['corr'], yerr=df_summary['std'], capsize=4, 
                   color=['#7f7f7f', '#2ca02c', '#d62728', '#ff7f0e', '#e377c2', '#1f77b4'],
                   edgecolor='black', alpha=0.85, width=0.55)
    
    ax.axhline(0.10, color='red', linestyle='--', linewidth=1.5, label="Cohen's Benchmark (r = 0.10)")
    ax.set_ylabel("Mean Correlation (r) at Gen 25", fontsize=11, fontweight='bold')
    ax.set_ylim(-0.02, 0.40)
    
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.012, f"r={yval:.3f}", ha='center', va='bottom', fontsize=9.5, fontweight='bold')

    ax.legend(frameon=True, loc='upper left', fontsize=9.5)
    plt.tight_layout()
    fig4_path = os.path.join(FIGURES_DIR, "fig4_model_comparisons.png")
    plt.savefig(fig4_path, dpi=100)
    plt.close()
    print("Saved clean fig4_model_comparisons.png")

    # -------------------------------------------------------------
    # Package into figures.zip for easy submission upload
    # -------------------------------------------------------------
    zip_path = os.path.join(BASE_DIR, "paper", "figures_JASSS.zip")
    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.write(fig1_path, arcname="fig1_assortative_mating.png")
        zf.write(fig2_path, arcname="fig2_population_stratification.png")
        zf.write(fig3_path, arcname="fig3_social_feedback.png")
        zf.write(fig4_path, arcname="fig4_model_comparisons.png")
    print(f"Packaged figures archive at: {zip_path}")

if __name__ == '__main__':
    generate_clean_figures()
