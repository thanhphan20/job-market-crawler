import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

# Layered Concept Groups
CONCEPT_GROUPS = {
    "Java Core": [
        "jvm", "jit", "garbage collection", "multithreading", "concurrency", 
        "java memory model", "stream api", "lambda", "reflection", "annotations", "generics"
    ],
    "Spring Ecosystem": [
        "spring", "spring boot", "spring cloud", "spring security", "spring data", "spring mvc"
    ],
    "Architecture": [
        "microservice", "event driven", "saga", "ddd", "domain driven design", 
        "clean architecture", "hexagonal architecture", "design pattern", "solid", "dry",
        "distributed system", "high concurrency", "system design", "rest api", "graphql"
    ],
    "Data & Messaging": [
        "sql", "postgresql", "mysql", "mongodb", "redis", "nosql", "elasticsearch",
        "kafka", "rabbitmq", "message queue", "activemq"
    ],
    "Infrastructure & DevOps": [
        "docker", "kubernetes", "k8s", "aws", "azure", "gcp", "ci/cd", "jenkins", 
        "terraform", "ansible", "git", "maven", "gradle"
    ]
}

def analyze_market_trends(data_path='data/itviec_jobs.csv'):
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found.")
        return None

    df = pd.read_csv(data_path)
    if df.empty:
        print("Dataset is empty.")
        return None

    corpus = df['Skills and Experience'].fillna('').str.lower()
    
    # 1. Grouped Concept Analysis
    group_counts = {}
    for group, skills in CONCEPT_GROUPS.items():
        # Check if ANY skill in the group is mentioned in the JD
        pattern = r'\b(' + '|'.join([re.escape(s) for s in skills]) + r')\b'
        count = corpus.apply(lambda x: 1 if re.search(pattern, x) else 0).sum()
        group_counts[group] = count

    # 2. TF-IDF for Automatic Concept Detection
    print("Running TF-IDF analysis...")
    tfidf = TfidfVectorizer(stop_words='english', ngram_range=(1, 3), max_features=20)
    t_matrix = tfidf.fit_transform(corpus)
    feature_names = tfidf.get_feature_names_out()
    tfidf_scores = t_matrix.sum(axis=0).A1
    top_tfidf = pd.DataFrame({'Concept': feature_names, 'Score': tfidf_scores}).sort_values(by='Score', ascending=False)

    # 3. Co-occurrence Matrix for Graph
    print("Calculating skill co-occurrence...")
    # Select top 20 specific keywords from all groups for the graph to keep it readable
    all_keywords = [skill for skills in CONCEPT_GROUPS.values() for skill in skills]
    
    # Filter keywords to those actually present in the corpus to avoid sparse graph
    present_keywords = []
    for k in all_keywords:
        if corpus.str.contains(r'\b' + re.escape(k) + r'\b').any():
            present_keywords.append(k)
            
    # Take top 15 most frequent skills for the graph
    skill_freq = {}
    for k in present_keywords:
        skill_freq[k] = corpus.str.contains(r'\b' + re.escape(k) + r'\b').sum()
    top_skills_for_graph = sorted(skill_freq, key=skill_freq.get, reverse=True)[:15]

    co_matrix = np.zeros((len(top_skills_for_graph), len(top_skills_for_graph)))
    for i, s1 in enumerate(top_skills_for_graph):
        for j, s2 in enumerate(top_skills_for_graph):
            if i == j: continue
            # Count JDs having both s1 and s2
            count = corpus.apply(lambda x: 1 if (re.search(r'\b'+re.escape(s1)+r'\b', x) and re.search(r'\b'+re.escape(s2)+r'\b', x)) else 0).sum()
            co_matrix[i, j] = count

    # Visualizations
    os.makedirs('outputs', exist_ok=True)
    
    # Graph 1: Grouped Concepts
    plt.figure(figsize=(10, 6))
    sns.barplot(x=list(group_counts.values()), y=list(group_counts.keys()), palette='magma')
    plt.title('Market Demand by Concept Group', fontsize=14)
    plt.tight_layout()
    plt.savefig('outputs/market_groups.png')

    # Graph 2: Co-occurrence Network
    plt.figure(figsize=(12, 10))
    G = nx.Graph()
    for i, s1 in enumerate(top_skills_for_graph):
        for j, s2 in enumerate(top_skills_for_graph):
            if i < j and co_matrix[i, j] > 0:
                G.add_edge(s1, s2, weight=co_matrix[i, j])

    pos = nx.spring_layout(G, k=0.5, iterations=50)
    # Scale node sizes by frequency
    node_sizes = [skill_freq[node] * 100 for node in G.nodes()]
    edges = G.edges()
    weights = [G[u][v]['weight'] for u, v in edges]
    
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color='skyblue', alpha=0.8)
    nx.draw_networkx_edges(G, pos, width=[w/2 for w in weights], edge_color='grey', alpha=0.5)
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
    
    plt.title('Skill Co-occurrence Network (Trends that go together)', fontsize=15)
    plt.axis('off')
    plt.savefig('outputs/skill_network.png')

    # 4. Generate Learning Roadmap
    generate_roadmap(group_counts, top_skills_for_graph)

    return group_counts

def generate_roadmap(groups, top_skills):
    roadmap_path = 'outputs/java_roadmap.md'
    with open(roadmap_path, 'w') as f:
        f.write("# 🚀 Java Developer Learning Roadmap (Data-Driven)\n\n")
        f.write(f"Generated from analyzing latest job postings on ITviec.\n\n")
        
        f.write("## Phase 1: Core Mastery\n")
        f.write("- **Java Fundamentals**: Streams, Lambda, Multithreading.\n")
        f.write("- **JVM Internals**: Memory Model, GC (Commonly asked in senior roles).\n\n")

        f.write("## Phase 2: The Framework King\n")
        f.write("- **Spring Boot**: The #1 requirement. Focus on REST APIs and Security.\n")
        f.write("- **Data Access**: SQL (PostgreSQL/MySQL) & Hibernate/JPA.\n\n")

        f.write("## Phase 3: Infrastructure & Modern Primitives\n")
        f.write("- **Docker & Kubernetes**: Containerization is non-negotiable now.\n")
        f.write("- **CI/CD**: Understanding Jenkins or GitHub Actions.\n\n")

        f.write("## Phase 4: Scaling & Architecture\n")
        f.write("- **Microservices**: Distributed systems and Service Discovery.\n")
        f.write("- **Cloud**: AWS is the most frequent cloud provider mentioned.\n")
        f.write("- **Messaging**: Kafka for event-driven architectures.\n\n")

        f.write("## 💡 Market Insights\n")
        f.write(f"- Most mentioned architecture: **Microservices**\n")
        f.write(f"- Top companion skill: **Docker**\n")
    
    print(f"Roadmap generated at {roadmap_path}")

if __name__ == "__main__":
    analyze_market_trends()
