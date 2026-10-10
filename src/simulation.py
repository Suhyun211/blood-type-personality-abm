"""
Blood Type Personality Simulation Engine
Agent-Based Modeling (ABM) for Spurious Correlation in Population Genetics

Rigorous Implementation adhering to Review Round 5 Guidelines:
- Independent Random Number Generation via np.random.SeedSequence
- Separation of Pure Coupled Model from Population Stratification
- Full 4 x 3 Factorial Grid for ANOVA Pipeline
- Multi-Generational Belief Withdrawal and Genetic/Phenotypic Inertia Tracking
- Dual Tracking of Phenotypic Correlation Corr(S(X), P) and Genetic Correlation Corr(S(X), G)
- Robustness Checks on Stereotype Scoring Scales and Mating Selection Direction
"""

import os
import json
import numpy as np
import pandas as pd

# Master Seed for Global SeedSequence
MASTER_SEED = 20261010

# Korean population ABO allele frequencies (Census baseline)
# p(A) ~ 0.28, q(B) ~ 0.22, r(O) ~ 0.50
ALLELES = ['A', 'B', 'O']
ALLELE_WEIGHTS = [0.28, 0.22, 0.50]

# Standard Blood type stereotype scores (Conventional cultural belief metric)
# Negative = Introverted/Cautious (Stereotypical A-type)
# Positive = Extraverted/Free-spirited (Stereotypical B-type, O-type)
STEREOTYPE_SCORES = {
    'A': -1.0,
    'B': 1.0,
    'O': 0.5,
    'AB': 0.0
}

# Phenotype mapping dictionary for speed and determinism
PHENO_MAP = {
    ('A', 'A'): 'A', ('A', 'B'): 'AB', ('A', 'O'): 'A',
    ('B', 'A'): 'AB', ('B', 'B'): 'B', ('B', 'O'): 'B',
    ('O', 'A'): 'A', ('O', 'B'): 'B', ('O', 'O'): 'O'
}

def determine_phenotype_vec(allele1, allele2):
    """Fast vectorized determination of ABO phenotypes."""
    return np.array([PHENO_MAP[(a1, a2)] for a1, a2 in zip(allele1, allele2)])


class Population:
    """Agent Population container maintaining genetics, phenotype, and environmental states."""
    def __init__(self, size=5000, h2=0.5, subpop_id=0, rng=None, stereotype_map=None):
        self.size = size
        self.h2 = h2
        self.subpop_id = subpop_id
        self.rng = rng if rng is not None else np.random.default_rng(MASTER_SEED)
        self.stereotype_map = stereotype_map if stereotype_map is not None else STEREOTYPE_SCORES
        
        # Sex: 0 = Male, 1 = Female (equal 1:1 ratio)
        self.sex = self.rng.choice([0, 1], size=size)
        
        # Initial Alleles under Hardy-Weinberg equilibrium
        self.allele1 = self.rng.choice(ALLELES, size=size, p=ALLELE_WEIGHTS)
        self.allele2 = self.rng.choice(ALLELES, size=size, p=ALLELE_WEIGHTS)
        self.phenotype = determine_phenotype_vec(self.allele1, self.allele2)
        
        # Polygenic personality components: P = G + E + feedback
        # Additive genetic component G ~ N(0, h^2)
        # Non-shared environmental noise E ~ N(0, 1 - h^2)
        self.G = self.rng.normal(0, np.sqrt(h2), size=size)
        self.E = self.rng.normal(0, np.sqrt(1.0 - h2), size=size)
        self.feedback = np.zeros(size)
        self.P = self.G + self.E + self.feedback

    def update_phenotype(self):
        """Update blood phenotypes and expressed trait."""
        self.phenotype = determine_phenotype_vec(self.allele1, self.allele2)
        self.P = self.G + self.E + self.feedback

    def clone(self, new_rng=None):
        """Deep copy for counterfactual branching experiments."""
        p = Population(
            size=self.size,
            h2=self.h2,
            subpop_id=self.subpop_id,
            rng=new_rng if new_rng is not None else self.rng,
            stereotype_map=self.stereotype_map
        )
        p.sex = self.sex.copy()
        p.allele1 = self.allele1.copy()
        p.allele2 = self.allele2.copy()
        p.phenotype = self.phenotype.copy()
        p.G = self.G.copy()
        p.E = self.E.copy()
        p.feedback = self.feedback.copy()
        p.P = self.P.copy()
        return p


def reproduce_generation(
    pop,
    assortative_strength=0.0,
    feedback_strength=0.0,
    k_candidates=5,
    bidirectional=False
):
    """
    Execute one generation of mate selection, Mendelian allele transmission,
    polygenic inheritance, and social feedback.
    """
    rng = pop.rng
    males = np.where(pop.sex == 0)[0]
    females = np.where(pop.sex == 1)[0]
    num_offspring = pop.size
    
    # 1. Mate Selection
    father_idx = rng.choice(males, size=num_offspring, replace=True)
    
    if assortative_strength == 0.0:
        mother_idx = rng.choice(females, size=num_offspring, replace=True)
    else:
        # Sample k candidates from female pool
        cand_mothers = rng.choice(females, size=(num_offspring, k_candidates), replace=True)
        father_P = pop.P[father_idx]
        
        # Stereotype values of candidate females
        pop_stereotypes = np.array([pop.stereotype_map[pt] for pt in pop.phenotype])
        cand_stereotypes = pop_stereotypes[cand_mothers]  # Shape: (num_offspring, k_candidates)
        
        # Compatibility metric: -|P_male - S(X_female)|
        compat = -np.abs(father_P[:, None] - cand_stereotypes)
        
        if bidirectional:
            # Bidirectional selection: candidate females also evaluate father's stereotype score vs their P
            cand_P = pop.P[cand_mothers]
            father_stereotypes = pop_stereotypes[father_idx]
            compat_female = -np.abs(cand_P - father_stereotypes[:, None])
            compat = 0.5 * compat + 0.5 * compat_female
            
        best_cand_idx = np.argmax(compat, axis=1)
        random_cand_idx = rng.integers(0, k_candidates, size=num_offspring)
        
        choose_best = rng.random(num_offspring) < assortative_strength
        chosen_col = np.where(choose_best, best_cand_idx, random_cand_idx)
        mother_idx = cand_mothers[np.arange(num_offspring), chosen_col]

    # 2. Mendelian Inheritance of ABO alleles
    f_a1_choice = rng.choice([0, 1], size=num_offspring)
    m_a1_choice = rng.choice([0, 1], size=num_offspring)
    
    child_a1 = np.where(f_a1_choice == 0, pop.allele1[father_idx], pop.allele2[father_idx])
    child_a2 = np.where(m_a1_choice == 0, pop.allele1[mother_idx], pop.allele2[mother_idx])
    child_phenotype = determine_phenotype_vec(child_a1, child_a2)

    # 3. Polygenic Inheritance of Personality (Infinitesimal Model)
    # Segregation variance = 0.5 * h^2
    segregation_noise = rng.normal(0, np.sqrt(0.5 * pop.h2), size=num_offspring)
    child_G = 0.5 * pop.G[father_idx] + 0.5 * pop.G[mother_idx] + segregation_noise
    
    # 4. Independent Environmental Noise
    child_E = rng.normal(0, np.sqrt(1.0 - pop.h2), size=num_offspring)

    # 5. Social Feedback / Labeling
    child_stereotypes = np.array([pop.stereotype_map[pt] for pt in child_phenotype])
    child_feedback = feedback_strength * child_stereotypes

    # 6. Update population
    pop.allele1 = child_a1
    pop.allele2 = child_a2
    pop.phenotype = child_phenotype
    pop.G = child_G
    pop.E = child_E
    pop.feedback = child_feedback
    pop.sex = rng.choice([0, 1], size=num_offspring)
    pop.P = pop.G + pop.E + pop.feedback


def run_simulation(
    pop_size=5000,
    generations=25,
    h2=0.5,
    assortative_strength=0.0,
    feedback_strength=0.0,
    stratification=False,
    strat_diff=0.0,
    num_reps=5,
    child_seeds=None,
    experiment_label="Simulation",
    stereotype_map=None,
    bidirectional=False
):
    """
    Execute multi-generational simulation with independent explicit seed streams.
    Tracks both phenotypic correlation r_P and latent genetic correlation r_G.
    """
    if child_seeds is None:
        seed_seq = np.random.SeedSequence(MASTER_SEED)
        child_seeds = seed_seq.spawn(num_reps)

    results = []

    for rep, c_seed in enumerate(child_seeds):
        rng = np.random.default_rng(c_seed)
        seed_id = int(c_seed.entropy) if hasattr(c_seed, 'entropy') else rep

        # Initialize Population
        if not stratification:
            pop = Population(size=pop_size, h2=h2, rng=rng, stereotype_map=stereotype_map)
        else:
            size_sub = pop_size // 2
            pop1 = Population(size=size_sub, h2=h2, subpop_id=1, rng=rng, stereotype_map=stereotype_map)
            pop1.allele1 = rng.choice(['A', 'B', 'O'], size=size_sub, p=[0.38, 0.12, 0.50])
            pop1.allele2 = rng.choice(['A', 'B', 'O'], size=size_sub, p=[0.38, 0.12, 0.50])
            pop1.G += (-strat_diff / 2.0)
            pop1.update_phenotype()

            pop2 = Population(size=size_sub, h2=h2, subpop_id=2, rng=rng, stereotype_map=stereotype_map)
            pop2.allele1 = rng.choice(['A', 'B', 'O'], size=size_sub, p=[0.18, 0.32, 0.50])
            pop2.allele2 = rng.choice(['A', 'B', 'O'], size=size_sub, p=[0.18, 0.32, 0.50])
            pop2.G += (strat_diff / 2.0)
            pop2.update_phenotype()

            pop = Population(size=pop_size, h2=h2, rng=rng, stereotype_map=stereotype_map)
            pop.sex = np.concatenate([pop1.sex, pop2.sex])
            pop.allele1 = np.concatenate([pop1.allele1, pop2.allele1])
            pop.allele2 = np.concatenate([pop1.allele2, pop2.allele2])
            pop.G = np.concatenate([pop1.G, pop2.G])
            pop.E = np.concatenate([pop1.E, pop2.E])
            pop.subpop_id = np.concatenate([np.ones(size_sub), np.full(size_sub, 2)])
            pop.update_phenotype()

        for gen in range(generations):
            st_map = pop.stereotype_map
            st_scores = np.array([st_map[pt] for pt in pop.phenotype])
            
            # Phenotypic and Genetic correlations
            r_P = float(np.corrcoef(pop.P, st_scores)[0, 1])
            r_G = float(np.corrcoef(pop.G, st_scores)[0, 1])
            
            # Subgroup means
            p_A = pop.P[pop.phenotype == 'A']
            p_B = pop.P[pop.phenotype == 'B']
            p_O = pop.P[pop.phenotype == 'O']
            p_AB = pop.P[pop.phenotype == 'AB']
            
            mean_A = float(np.mean(p_A)) if len(p_A) > 0 else 0.0
            mean_B = float(np.mean(p_B)) if len(p_B) > 0 else 0.0
            mean_O = float(np.mean(p_O)) if len(p_O) > 0 else 0.0
            mean_AB = float(np.mean(p_AB)) if len(p_AB) > 0 else 0.0
            
            # Genetic means
            g_A = pop.G[pop.phenotype == 'A']
            g_B = pop.G[pop.phenotype == 'B']
            mean_G_A = float(np.mean(g_A)) if len(g_A) > 0 else 0.0
            mean_G_B = float(np.mean(g_B)) if len(g_B) > 0 else 0.0

            # Cohen's d (Type B vs Type A)
            pooled_sd_P = float(np.sqrt((np.var(p_A) + np.var(p_B)) / 2.0)) if (len(p_A) > 0 and len(p_B) > 0) else 1.0
            cohens_d_P = (mean_B - mean_A) / (pooled_sd_P + 1e-9)
            
            pooled_sd_G = float(np.sqrt((np.var(g_A) + np.var(g_B)) / 2.0)) if (len(g_A) > 0 and len(g_B) > 0) else 1.0
            cohens_d_G = (mean_G_B - mean_G_A) / (pooled_sd_G + 1e-9)

            results.append({
                'rep': rep,
                'seed': seed_id,
                'gen': gen,
                'experiment': experiment_label,
                'corr': r_P,
                'corr_genetic': r_G,
                'cohens_d': cohens_d_P,
                'cohens_d_genetic': cohens_d_G,
                'mean_A': mean_A,
                'mean_B': mean_B,
                'mean_O': mean_O,
                'mean_AB': mean_AB,
                'assortative_strength': assortative_strength,
                'feedback_strength': feedback_strength,
                'stratification': stratification,
                'strat_diff': strat_diff
            })

            # Next generation step
            if gen < generations - 1:
                reproduce_generation(
                    pop,
                    assortative_strength=assortative_strength,
                    feedback_strength=feedback_strength,
                    bidirectional=bidirectional
                )

    return pd.DataFrame(results)


def run_belief_withdrawal_experiment(num_reps=5, child_seeds=None):
    """
    Experiment 6: Cultural Belief Withdrawal & Generational Inertia Dynamic.
    - Gen 0 to 10: Baseline coupled cultural model (alpha = 0.15, beta = 0.10).
    - At Gen 10: Branches into 3 scenarios:
      1) Sustained: Maintain alpha = 0.15, beta = 0.10
      2) Feedback Cessation: beta = 0.0, alpha = 0.15 (mating bias continues)
      3) Complete Withdrawal: alpha = 0.0, beta = 0.0 (full random mating, no feedback)
    """
    if child_seeds is None:
        seed_seq = np.random.SeedSequence(MASTER_SEED)
        child_seeds = seed_seq.spawn(num_reps)

    records = []

    for rep, cs in enumerate(child_seeds):
        # We spawn separate generators for the branches to ensure fair comparison
        sub_seeds = cs.spawn(4)
        rng_early = np.random.default_rng(sub_seeds[0])
        seed_id = int(cs.entropy) if hasattr(cs, 'entropy') else rep
        
        pop = Population(size=5000, h2=0.5, rng=rng_early)
        
        # Gen 0..10 run under baseline
        early_records = []
        for g in range(11):
            st = np.array([STEREOTYPE_SCORES[pt] for pt in pop.phenotype])
            r_P = float(np.corrcoef(pop.P, st)[0, 1])
            r_G = float(np.corrcoef(pop.G, st)[0, 1])
            
            p_A = pop.P[pop.phenotype == 'A']
            p_B = pop.P[pop.phenotype == 'B']
            d_P = (np.mean(p_B) - np.mean(p_A)) / (np.sqrt((np.var(p_A) + np.var(p_B)) / 2.0) + 1e-9)
            
            early_records.append({
                'rep': rep,
                'seed': seed_id,
                'gen': g,
                'corr': r_P,
                'corr_genetic': r_G,
                'cohens_d': d_P
            })
            if g < 10:
                reproduce_generation(pop, assortative_strength=0.15, feedback_strength=0.10)

        # Clone population at Gen 10 for branches
        pop_sust = pop.clone(new_rng=np.random.default_rng(sub_seeds[1]))
        pop_fb_stop = pop.clone(new_rng=np.random.default_rng(sub_seeds[2]))
        pop_comp_stop = pop.clone(new_rng=np.random.default_rng(sub_seeds[3]))

        scenarios = [
            ('Sustained', pop_sust, 0.15, 0.10),
            ('Feedback_Cessation', pop_fb_stop, 0.15, 0.0),
            ('Complete_Withdrawal', pop_comp_stop, 0.0, 0.0)
        ]

        for sc_name, sc_pop, sc_alpha, sc_beta in scenarios:
            # Append early history
            for er in early_records:
                records.append({**er, 'scenario': sc_name})
            
            cur_pop = sc_pop.clone()
            for g in range(11, 26):
                reproduce_generation(cur_pop, assortative_strength=sc_alpha, feedback_strength=sc_beta)
                st = np.array([STEREOTYPE_SCORES[pt] for pt in cur_pop.phenotype])
                r_P = float(np.corrcoef(cur_pop.P, st)[0, 1])
                r_G = float(np.corrcoef(cur_pop.G, st)[0, 1])
                
                p_A = cur_pop.P[cur_pop.phenotype == 'A']
                p_B = cur_pop.P[cur_pop.phenotype == 'B']
                d_P = (np.mean(p_B) - np.mean(p_A)) / (np.sqrt((np.var(p_A) + np.var(p_B)) / 2.0) + 1e-9)
                
                records.append({
                    'rep': rep,
                    'seed': seed_id,
                    'gen': g,
                    'scenario': sc_name,
                    'corr': r_P,
                    'corr_genetic': r_G,
                    'cohens_d': d_P
                })

    return pd.DataFrame(records)


def main():
    print("=====================================================================")
    print("  ABM Simulation Suite for Blood Type Personality Association")
    print("  Adhering to JASSS Standards & Review Round 5 Guidelines")
    print("=====================================================================")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    master_seq = np.random.SeedSequence(MASTER_SEED)
    
    # Spawn child seed streams for each experimental module
    num_reps = 5
    exp_seeds = master_seq.spawn(7) # 7 distinct experiment modules

    # -------------------------------------------------------------
    # 1. Experiment 1: Assortative Mating Sweep (alpha in {0.0, 0.2, 0.5, 0.8})
    # -------------------------------------------------------------
    print("\n[*] Executing Experiment 1: Assortative Mating Sweep...")
    exp1_seeds = exp_seeds[0].spawn(num_reps)
    exp1_frames = []
    for alpha in [0.0, 0.2, 0.5, 0.8]:
        df_a = run_simulation(
            pop_size=5000,
            generations=25,
            assortative_strength=alpha,
            feedback_strength=0.0,
            num_reps=num_reps,
            child_seeds=exp1_seeds,
            experiment_label=f'Assortative_alpha_{alpha}'
        )
        exp1_frames.append(df_a)
    df_exp1 = pd.concat(exp1_frames, ignore_index=True)
    exp1_path = os.path.join(data_dir, "experiment1_assortative.csv")
    df_exp1.to_csv(exp1_path, index=False)
    print(f"  -> Saved {len(df_exp1)} records to: {exp1_path}")

    # -------------------------------------------------------------
    # 2. Experiment 2: Population Stratification Sweep (Delta in {0.2, 0.5, 1.0})
    # -------------------------------------------------------------
    print("\n[*] Executing Experiment 2: Population Stratification Sweep...")
    exp2_seeds = exp_seeds[1].spawn(num_reps)
    exp2_frames = []
    for diff in [0.2, 0.5, 1.0]:
        df_s = run_simulation(
            pop_size=5000,
            generations=25,
            stratification=True,
            strat_diff=diff,
            assortative_strength=0.0,
            feedback_strength=0.0,
            num_reps=num_reps,
            child_seeds=exp2_seeds,
            experiment_label=f'Stratification_diff_{diff}'
        )
        exp2_frames.append(df_s)
    df_exp2 = pd.concat(exp2_frames, ignore_index=True)
    exp2_path = os.path.join(data_dir, "experiment2_stratification.csv")
    df_exp2.to_csv(exp2_path, index=False)
    print(f"  -> Saved {len(df_exp2)} records to: {exp2_path}")

    # -------------------------------------------------------------
    # 3. Experiment 3: Social Feedback Sweep (beta in {0.10, 0.25, 0.50})
    # -------------------------------------------------------------
    print("\n[*] Executing Experiment 3: Social Feedback Sweep...")
    exp3_seeds = exp_seeds[2].spawn(num_reps)
    exp3_frames = []
    for beta in [0.10, 0.25, 0.50]:
        df_f = run_simulation(
            pop_size=5000,
            generations=25,
            assortative_strength=0.0,
            feedback_strength=beta,
            num_reps=num_reps,
            child_seeds=exp3_seeds,
            experiment_label=f'Feedback_beta_{beta}'
        )
        exp3_frames.append(df_f)
    df_exp3 = pd.concat(exp3_frames, ignore_index=True)
    exp3_path = os.path.join(data_dir, "experiment3_feedback.csv")
    df_exp3.to_csv(exp3_path, index=False)
    print(f"  -> Saved {len(df_exp3)} records to: {exp3_path}")

    # -------------------------------------------------------------
    # 4. Experiment 4: Separation of Synergistic & Stratified Mechanisms
    # Resolving Reviewer Confound:
    # Condition 1: Null Control (alpha=0, beta=0, strat=False)
    # Condition 2: Assortative Only (alpha=0.15, beta=0, strat=False)
    # Condition 3: Feedback Only (alpha=0, beta=0.10, strat=False)
    # Condition 4: Coupled Pure (alpha=0.15, beta=0.10, strat=False) [Pure 2-factor cultural model]
    # Condition 5: Coupled + Stratification (alpha=0.15, beta=0.10, strat=True, diff=0.2)
    # -------------------------------------------------------------
    print("\n[*] Executing Experiment 4: Unconfounded Mechanism Separation...")
    exp4_seeds = exp_seeds[3].spawn(num_reps)
    exp4_frames = []
    conditions_exp4 = [
        ('Null_Control', 0.0, 0.0, False, 0.0),
        ('Assortative_Only', 0.15, 0.0, False, 0.0),
        ('Feedback_Only', 0.0, 0.10, False, 0.0),
        ('Coupled_Pure', 0.15, 0.10, False, 0.0),
        ('Coupled_Stratified', 0.15, 0.10, True, 0.2)
    ]
    for label, alpha, beta, strat, diff in conditions_exp4:
        df_c = run_simulation(
            pop_size=5000,
            generations=25,
            assortative_strength=alpha,
            feedback_strength=beta,
            stratification=strat,
            strat_diff=diff,
            num_reps=num_reps,
            child_seeds=exp4_seeds,
            experiment_label=label
        )
        df_c['condition'] = label
        exp4_frames.append(df_c)
    df_exp4 = pd.concat(exp4_frames, ignore_index=True)
    exp4_path = os.path.join(data_dir, "experiment4_combined.csv")
    df_exp4.to_csv(exp4_path, index=False)
    print(f"  -> Saved {len(df_exp4)} records to: {exp4_path}")

    # -------------------------------------------------------------
    # 5. Experiment 5: Complete 4 x 3 Factorial Grid for ANOVA
    # alpha in {0.0, 0.2, 0.5, 0.8} x beta in {0.0, 0.10, 0.25} x 5 reps = 60 cells
    # -------------------------------------------------------------
    print("\n[*] Executing Experiment 5: Complete 4 x 3 Factorial Grid for ANOVA...")
    exp5_seeds = exp_seeds[4].spawn(num_reps)
    exp5_frames = []
    alphas = [0.0, 0.2, 0.5, 0.8]
    betas = [0.0, 0.10, 0.25]
    
    for alpha in alphas:
        for beta in betas:
            df_g = run_simulation(
                pop_size=5000,
                generations=25,
                assortative_strength=alpha,
                feedback_strength=beta,
                stratification=False,
                num_reps=num_reps,
                child_seeds=exp5_seeds,
                experiment_label=f'Factorial_a{alpha}_b{beta}'
            )
            df_g['alpha'] = alpha
            df_g['beta'] = beta
            exp5_frames.append(df_g)
    df_exp5 = pd.concat(exp5_frames, ignore_index=True)
    exp5_path = os.path.join(data_dir, "experiment5_factorial_grid.csv")
    df_exp5.to_csv(exp5_path, index=False)
    print(f"  -> Saved {len(df_exp5)} records to: {exp5_path}")

    # -------------------------------------------------------------
    # 6. Experiment 6: Belief Withdrawal and Generational Inertia
    # -------------------------------------------------------------
    print("\n[*] Executing Experiment 6: Belief Withdrawal & Generational Inertia...")
    exp6_seeds = exp_seeds[5].spawn(num_reps)
    df_exp6 = run_belief_withdrawal_experiment(num_reps=num_reps, child_seeds=exp6_seeds)
    exp6_path = os.path.join(data_dir, "experiment6_belief_withdrawal.csv")
    df_exp6.to_csv(exp6_path, index=False)
    print(f"  -> Saved {len(df_exp6)} records to: {exp6_path}")

    # -------------------------------------------------------------
    # 7. Experiment 7: Robustness Checks (Stereotype Schemes & Direction)
    # -------------------------------------------------------------
    print("\n[*] Executing Experiment 7: Sensitivity & Robustness Checks...")
    exp7_seeds = exp_seeds[6].spawn(num_reps)
    exp7_frames = []
    
    # 7a. Symmetric Scoring Scale: A=-1, B=1, O=0, AB=0
    sym_scores = {'A': -1.0, 'B': 1.0, 'O': 0.0, 'AB': 0.0}
    df_sym = run_simulation(
        pop_size=5000, generations=25, assortative_strength=0.15, feedback_strength=0.10,
        num_reps=num_reps, child_seeds=exp7_seeds, experiment_label='Robustness_Symmetric_Scale',
        stereotype_map=sym_scores
    )
    df_sym['robustness_test'] = 'Symmetric_Scores'
    exp7_frames.append(df_sym)
    
    # 7b. Bidirectional Mate Choice
    df_bi = run_simulation(
        pop_size=5000, generations=25, assortative_strength=0.15, feedback_strength=0.10,
        num_reps=num_reps, child_seeds=exp7_seeds, experiment_label='Robustness_Bidirectional_Choice',
        bidirectional=True
    )
    df_bi['robustness_test'] = 'Bidirectional_Choice'
    exp7_frames.append(df_bi)

    df_exp7 = pd.concat(exp7_frames, ignore_index=True)
    exp7_path = os.path.join(data_dir, "experiment7_sensitivity_robustness.csv")
    df_exp7.to_csv(exp7_path, index=False)
    print(f"  -> Saved {len(df_exp7)} records to: {exp7_path}")

    print("\n[OK] All simulations completed flawlessly. All datasets saved in /data.")

if __name__ == '__main__':
    main()
