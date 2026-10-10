"""
Blood Type Personality Simulation Engine
Agent-Based Modeling (ABM) for Spurious Correlation in Population Genetics

Roles:
- Statistician: Formalizes polygenic inheritance, mating mechanisms, and feedback loops.
- Simulation Engineer: Vectorized simulation in NumPy for multi-generation tracking.
"""

import numpy as np
import pandas as pd
import os
import json

# Set seed for reproducibility
np.random.seed(42)

# Korean population ABO allele frequencies
# p(A) ~ 0.28, q(B) ~ 0.22, r(O) ~ 0.50
ALLELE_PROBS = {'A': 0.28, 'B': 0.22, 'O': 0.50}
ALLELES = ['A', 'B', 'O']
ALLELE_WEIGHTS = [0.28, 0.22, 0.50]

# Blood type stereotype scores (Conventional cultural belief metric)
# Negative = Introverted/Cautious (Stereotypical A-type)
# Positive = Extraverted/Free-spirited (Stereotypical B-type, O-type)
STEREOTYPE_SCORES = {
    'A': -1.0,
    'B': 1.0,
    'O': 0.5,
    'AB': 0.0
}

def determine_phenotype(allele1, allele2):
    """Determine ABO blood type phenotype from two alleles."""
    pair = {allele1, allele2}
    if 'A' in pair and 'B' in pair:
        return 'AB'
    elif 'A' in pair:
        return 'A'
    elif 'B' in pair:
        return 'B'
    else:
        return 'O'

class Population:
    def __init__(self, size=10000, h2=0.5, subpop_id=0):
        """
        Initialize an agent population.
        size: number of individuals (must be even, 50% male, 50% female)
        h2: heritability of personality trait (0.0 ~ 1.0)
        """
        self.size = size
        self.h2 = h2
        self.subpop_id = subpop_id
        
        # Sex: 0 = Male, 1 = Female
        self.sex = np.random.choice([0, 1], size=size)
        
        # Initial Alleles (Hardy-Weinberg)
        self.allele1 = np.random.choice(ALLELES, size=size, p=ALLELE_WEIGHTS)
        self.allele2 = np.random.choice(ALLELES, size=size, p=ALLELE_WEIGHTS)
        self.phenotype = np.array([determine_phenotype(a1, a2) for a1, a2 in zip(self.allele1, self.allele2)])
        
        # Personality Trait: P = G + E
        # Genetic component G ~ N(0, h2)
        # Environmental component E ~ N(0, 1 - h2)
        self.G = np.random.normal(0, np.sqrt(h2), size=size)
        self.E = np.random.normal(0, np.sqrt(1.0 - h2), size=size)
        self.feedback = np.zeros(size)
        self.P = self.G + self.E + self.feedback

    def update_phenotype(self):
        self.phenotype = np.array([determine_phenotype(a1, a2) for a1, a2 in zip(self.allele1, self.allele2)])
        self.P = self.G + self.E + self.feedback

def run_simulation(
    pop_size=10000,
    generations=30,
    h2=0.5,
    assortative_strength=0.0,
    feedback_strength=0.0,
    stratification=False,
    strat_diff=0.0,
    num_reps=5
):
    """
    Run multi-generation simulation under specified parameters.
    - assortative_strength (alpha): [0.0, 1.0], probability/strength of choosing mate based on blood type belief compatibility.
    - feedback_strength (beta): [0.0, 1.0], magnitude of self-fulfilling socialization feedback.
    - stratification: True/False, presence of two subpopulations with different allele & trait distributions.
    - strat_diff: difference in mean trait and allele frequencies between subpopulations.
    """
    results_by_generation = []

    for rep in range(num_reps):
        # Initialize population
        if not stratification:
            pop = Population(size=pop_size, h2=h2)
        else:
            # 50% Subpop 1 (e.g., higher A, lower trait), 50% Subpop 2 (e.g., higher B, higher trait)
            size_sub = pop_size // 2
            # Subpop 1: A freq = 0.38, B freq = 0.12, O freq = 0.50, Trait shift = -strat_diff
            # Subpop 2: A freq = 0.18, B freq = 0.32, O freq = 0.50, Trait shift = +strat_diff
            pop1 = Population(size=size_sub, h2=h2, subpop_id=1)
            pop1.allele1 = np.random.choice(['A', 'B', 'O'], size=size_sub, p=[0.38, 0.12, 0.50])
            pop1.allele2 = np.random.choice(['A', 'B', 'O'], size=size_sub, p=[0.38, 0.12, 0.50])
            pop1.G += (-strat_diff / 2.0)
            pop1.update_phenotype()

            pop2 = Population(size=size_sub, h2=h2, subpop_id=2)
            pop2.allele1 = np.random.choice(['A', 'B', 'O'], size=size_sub, p=[0.18, 0.32, 0.50])
            pop2.allele2 = np.random.choice(['A', 'B', 'O'], size=size_sub, p=[0.18, 0.32, 0.50])
            pop2.G += (strat_diff / 2.0)
            pop2.update_phenotype()

            # Merge
            pop = Population(size=pop_size, h2=h2)
            pop.sex = np.concatenate([pop1.sex, pop2.sex])
            pop.allele1 = np.concatenate([pop1.allele1, pop2.allele1])
            pop.allele2 = np.concatenate([pop1.allele2, pop2.allele2])
            pop.G = np.concatenate([pop1.G, pop2.G])
            pop.E = np.concatenate([pop1.E, pop2.E])
            pop.subpop_id = np.concatenate([np.ones(size_sub), np.full(size_sub, 2)])
            pop.update_phenotype()

        for gen in range(generations):
            # Calculate current statistics
            stereotype_vals = np.array([STEREOTYPE_SCORES[pt] for pt in pop.phenotype])
            # Pearson correlation between personality trait P and stereotype score
            corr = np.corrcoef(pop.P, stereotype_vals)[0, 1]
            
            # Group means and Cohen's d between A and B
            p_A = pop.P[pop.phenotype == 'A']
            p_B = pop.P[pop.phenotype == 'B']
            mean_A = np.mean(p_A) if len(p_A) > 0 else 0
            mean_B = np.mean(p_B) if len(p_B) > 0 else 0
            pooled_sd = np.sqrt((np.var(p_A) + np.var(p_B)) / 2.0) if (len(p_A) > 0 and len(p_B) > 0) else 1.0
            cohens_d = (mean_B - mean_A) / (pooled_sd + 1e-9)

            results_by_generation.append({
                'rep': rep,
                'gen': gen,
                'corr': corr,
                'cohens_d': cohens_d,
                'mean_A': mean_A,
                'mean_B': mean_B,
                'assortative_strength': assortative_strength,
                'feedback_strength': feedback_strength,
                'stratification': stratification,
                'strat_diff': strat_diff
            })

            # Next generation reproduction (if not final gen)
            if gen < generations - 1:
                males = np.where(pop.sex == 0)[0]
                females = np.where(pop.sex == 1)[0]
                
                num_offspring = pop_size
                half = min(len(males), len(females))
                if half < 100:
                    break

                # Mating selection
                # Random mating baseline vs Assortative mating
                # In assortative mating: males with personality P_m match with females whose blood stereotype aligns with P_m
                if assortative_strength == 0.0:
                    father_idx = np.random.choice(males, size=num_offspring, replace=True)
                    mother_idx = np.random.choice(females, size=num_offspring, replace=True)
                else:
                    # Assortative mating scheme:
                    # A male with high P prefers high stereotype score female (and vice versa) with probability alpha
                    father_idx = np.random.choice(males, size=num_offspring, replace=True)
                    
                    # For each father, candidate mothers
                    # To keep it computationally fast and realistic:
                    # Sample k candidates, pick the one maximizing compatibility with weight alpha
                    k_candidates = 5
                    cand_mothers = np.random.choice(females, size=(num_offspring, k_candidates), replace=True)
                    
                    father_P = pop.P[father_idx] # shape (num_offspring,)
                    # Candidate mother stereotypes
                    cand_stereotypes = np.array([[STEREOTYPE_SCORES[pop.phenotype[m_idx]] for m_idx in row] for row in cand_mothers])
                    
                    # Compatibility score: -abs(father_P[:, None] - cand_stereotypes)
                    compat = -np.abs(father_P[:, None] - cand_stereotypes)
                    
                    # Probability of choosing best candidate based on assortative_strength
                    best_cand_idx = np.argmax(compat, axis=1)
                    random_cand_idx = np.random.randint(0, k_candidates, size=num_offspring)
                    
                    choose_best = np.random.rand(num_offspring) < assortative_strength
                    chosen_col = np.where(choose_best, best_cand_idx, random_cand_idx)
                    mother_idx = cand_mothers[np.arange(num_offspring), chosen_col]

                # Offspring generation
                # Mendel inheritance: 1 allele from father, 1 from mother
                f_a1_choice = np.random.choice([0, 1], size=num_offspring)
                m_a1_choice = np.random.choice([0, 1], size=num_offspring)
                
                child_a1 = np.where(f_a1_choice == 0, pop.allele1[father_idx], pop.allele2[father_idx])
                child_a2 = np.where(m_a1_choice == 0, pop.allele1[mother_idx], pop.allele2[mother_idx])
                
                # Polygenic inheritance of personality:
                # G_child = 0.5 * G_father + 0.5 * G_mother + Segregation Variance
                # Segregation variance = 0.5 * h2
                segregation_noise = np.random.normal(0, np.sqrt(0.5 * h2), size=num_offspring)
                child_G = 0.5 * pop.G[father_idx] + 0.5 * pop.G[mother_idx] + segregation_noise
                
                # Environmental noise
                child_E = np.random.normal(0, np.sqrt(1.0 - h2), size=num_offspring)
                
                # Child phenotype
                child_phenotype = np.array([determine_phenotype(a1, a2) for a1, a2 in zip(child_a1, child_a2)])
                
                # Social feedback / Self-fulfilling prophecy:
                # feedback = beta * stereotype_score
                child_feedback = feedback_strength * np.array([STEREOTYPE_SCORES[pt] for pt in child_phenotype])
                
                # New population
                pop.allele1 = child_a1
                pop.allele2 = child_a2
                pop.phenotype = child_phenotype
                pop.G = child_G
                pop.E = child_E
                pop.feedback = child_feedback
                pop.sex = np.random.choice([0, 1], size=num_offspring)
                pop.P = pop.G + pop.E + pop.feedback

    return pd.DataFrame(results_by_generation)

def main():
    print("=== Starting Comprehensive Blood Type Personality Simulation ===")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    
    # 1. Baseline: Null Model (No assortative mating, no feedback, no stratification)
    print("Running Experiment 0: Null Hypothesis (Control)...")
    df_null = run_simulation(pop_size=5000, generations=25, assortative_strength=0.0, feedback_strength=0.0, num_reps=5)
    df_null['experiment'] = 'Null_Control'
    
    # 2. Experiment 1: Assortative Mating Sweep
    print("Running Experiment 1: Assortative Mating Strength Sweep...")
    exp1_list = [df_null]
    for alpha in [0.2, 0.5, 0.8]:
        df_exp1 = run_simulation(pop_size=5000, generations=25, assortative_strength=alpha, feedback_strength=0.0, num_reps=5)
        df_exp1['experiment'] = f'Assortative_alpha_{alpha}'
        exp1_list.append(df_exp1)
    df_exp1_all = pd.concat(exp1_list, ignore_index=True)
    df_exp1_all.to_csv(os.path.join(data_dir, "experiment1_assortative.csv"), index=False)
    
    # 3. Experiment 2: Population Stratification Sweep
    print("Running Experiment 2: Population Stratification Sweep...")
    exp2_list = []
    for diff in [0.2, 0.5, 1.0]:
        df_exp2 = run_simulation(pop_size=5000, generations=25, stratification=True, strat_diff=diff, assortative_strength=0.0, feedback_strength=0.0, num_reps=5)
        df_exp2['experiment'] = f'Stratification_diff_{diff}'
        exp2_list.append(df_exp2)
    df_exp2_all = pd.concat(exp2_list, ignore_index=True)
    df_exp2_all.to_csv(os.path.join(data_dir, "experiment2_stratification.csv"), index=False)
    
    # 4. Experiment 3: Social Feedback (Self-fulfilling Prophecy) Sweep
    print("Running Experiment 3: Social Feedback Sweep...")
    exp3_list = []
    for beta in [0.1, 0.25, 0.5]:
        df_exp3 = run_simulation(pop_size=5000, generations=25, assortative_strength=0.0, feedback_strength=beta, num_reps=5)
        df_exp3['experiment'] = f'Feedback_beta_{beta}'
        exp3_list.append(df_exp3)
    df_exp3_all = pd.concat(exp3_list, ignore_index=True)
    df_exp3_all.to_csv(os.path.join(data_dir, "experiment3_feedback.csv"), index=False)

    # 5. Experiment 4: Realistic Combined Model
    print("Running Experiment 4: Realistic Synergistic Model...")
    df_real = run_simulation(pop_size=5000, generations=25, assortative_strength=0.15, feedback_strength=0.10, stratification=True, strat_diff=0.2, num_reps=5)
    df_real['experiment'] = 'Realistic_Combined'
    df_real.to_csv(os.path.join(data_dir, "experiment4_combined.csv"), index=False)

    print(f"All simulations completed successfully. Data saved to '{data_dir}' folder.")

if __name__ == '__main__':
    main()

