import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re

# Common Java-related skills and keywords to look for
JAVA_SKILL_KEYWORDS = [
    'Spring Boot', 'Spring', 'Hibernate', 'Microservices', 'REST', 'SQL', 'PostgreSQL', 
    'MySQL', 'Docker', 'Kubernetes', 'AWS', 'GIT', 'Hibernate', 'JPA', 'JUnit', 
    'Kafka', 'Redis', 'Elasticsearch', 'Jenkins', 'CI/CD', 'NoSQL', 'MongoDB', 
    'Agile', 'English', 'JavaScript', 'TypeScript', 'React', 'Angular', 'Vue',
    'Unit Test', 'Design Pattern', 'Clean Code', 'Solid', 'Maven', 'Gradle'
]

def analyze_java_skills(data_path='data/itviec_jobs.csv', output_img='outputs/java_skills_chart.png'):
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found.")
        return

    df = pd.read_csv(data_path)
    
    # Filter for Java jobs if possible, or just analyze all (since itviec query was java)
    skills_text = df['Skills and Experience'].fillna('').str.lower()
    
    skill_counts = {}
    
    for skill in JAVA_SKILL_KEYWORDS:
        # Create a simple regex to match whole words/phrases
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        count = skills_text.apply(lambda x: 1 if re.search(pattern, x) else 0).sum()
        skill_counts[skill] = count
        
    # Convert to DataFrame for plotting
    analysis_df = pd.DataFrame(list(skill_counts.items()), columns=['Skill', 'Count'])
    analysis_df = analysis_df.sort_values(by='Count', ascending=False).head(15) # Top 15

    # Create visualization
    plt.figure(figsize=(12, 8))
    sns.set_theme(style="whitegrid")
    
    bar_plot = sns.barplot(x='Count', y='Skill', data=analysis_df, palette='viridis')
    plt.title('Top 15 Most Required Skills for Java Roles', fontsize=16)
    plt.xlabel('Number of Job Postings', fontsize=12)
    plt.ylabel('Skill / Technology', fontsize=12)
    
    # Ensure outputs directory exists
    os.makedirs(os.path.dirname(output_img), exist_ok=True)
    
    plt.tight_layout()
    plt.savefig(output_img)
    print(f"Analysis complete. Graph saved to {output_img}")
    
    return analysis_df

if __name__ == "__main__":
    # For standalone testing
    analyze_java_skills()
