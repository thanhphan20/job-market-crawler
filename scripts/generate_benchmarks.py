import pandas as pd
import numpy as np
import os

def generate_synthetic_kaggle_data(target_dir="data"):
    """
    Generates synthetic versions of Kaggle datasets based on research statistics.
    Useful for demonstration and benchmarking when raw files are not present.
    """
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # 1. Main AI Market Trend Data (Synthesized from Bisma Sajjad's research)
    print("[*] Generating synthetic 'global_ai_market_2025.csv'...")
    n_rows = 1000
    df_main = pd.DataFrame({
        'job_id': [f'AI{i:05d}' for i in range(n_rows)],
        'job_title': np.random.choice(['Data Scientist', 'ML Engineer', 'AI Researcher', 'Data Analyst', 'Prompt Engineer'], n_rows),
        'salary_usd': np.random.normal(125000, 30000, n_rows).clip(40000, 350000),
        'experience_level': np.random.choice(['EN', 'MI', 'SE', 'EX'], n_rows, p=[0.2, 0.3, 0.4, 0.1]),
        'required_skills': np.random.choice([
            'Python, SQL, PyTorch', 
            'Python, TensorFlow, AWS',
            'SQL, Tableau, Statistics',
            'Python, Natural Language Processing, BERT',
            'Scikit-learn, Pandas, Docker'
        ], n_rows),
        'industry': np.random.choice(['Tech', 'Finance', 'Healthcare', 'Automotive', 'E-commerce'], n_rows)
    })
    df_main.to_csv(os.path.join(target_dir, "global_ai_market_2025.csv"), index=False)

    # 2. AI Impact Data (Synthesized from Sahil Islam's research)
    print("[*] Generating synthetic 'ai_impact_2024_2030.csv'...")
    industries = ['IT', 'Healthcare', 'Manufacturing', 'Finance', 'Education', 'Legal']
    job_statuses = ['Increasing', 'Decreasing']
    
    impact_rows = []
    for ind in industries:
        for status in job_statuses:
            # Synthetic risk: Manufacturing/Decreasing has higher risk than IT/Increasing
            base_risk = 60 if status == 'Decreasing' else 20
            if ind == 'Manufacturing': base_risk += 15
            
            impact_rows.append({
                'Job Title': f'Role in {ind}',
                'Industry': ind,
                'Job Status': status,
                'Automation Risk (%)': np.random.normal(base_risk, 10),
                'AI Impact Level': 'High' if base_risk > 50 else 'Moderate'
            })
    
    df_impact = pd.DataFrame(impact_rows)
    df_impact.to_csv(os.path.join(target_dir, "ai_impact_2024_2030.csv"), index=False)

    # 3. Time Series Data (Synthesized from Mann Raval's research)
    print("[*] Generating synthetic 'ai_data_science_2020_2026.csv'...")
    years = [2020, 2021, 2022, 2023, 2024, 2025, 2026]
    entries = []
    for year in years:
        n = 100
        # Salary grows over years
        base_salary = 80000 + (year - 2020) * 12000
        entries.extend([{
            'work_year': year,
            'salary_in_usd': np.random.normal(base_salary, 15000)
        } for _ in range(n)])
    
    df_time = pd.DataFrame(entries)
    df_time.to_csv(os.path.join(target_dir, "ai_data_science_2020_2026.csv"), index=False)

    print("[+] Synthetic Kaggle benchmarks successfully created in 'data/'.")

if __name__ == "__main__":
    generate_synthetic_kaggle_data()
