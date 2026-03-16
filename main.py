import csv
import json
import os
from crawlers.itviec import scrap_itviec
from analytics.skill_analyzer import analyze_market_trends

def main():
    # 1. Scraping
    print("--- Phase 1: Scraping ITViec (Building Large Dataset) ---")
    # Target 500 jobs, checking up to 15 pages
    results = scrap_itviec(limit=500, start_page=1, end_page=15)
    
    if not results:
        print("No results found. Please check your session ID in crawlers/itviec.py")
        return

    print(f"Successfully collected {len(results)} job postings.")

    # Focus on specific fields for analysis
    output_data = []
    for entry in results:
        output_data.append({
            'Title': entry.get('title'),
            'Company': entry.get('company'),
            'Skills and Experience': entry.get('skills_and_experience')
        })

    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)

    # Export to JSON
    json_path = 'data/itviec_jobs.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(f"Exported listings to {json_path}")

    # Export to CSV (Primary for pandas analysis)
    csv_path = 'data/itviec_jobs.csv'
    if output_data:
        keys = output_data[0].keys()
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(output_data)
        print(f"Exported listings to {csv_path}")

    # 2. Analytics
    print("\n--- Phase 2: Advanced Market Analytics (NLP & Graphs) ---")
    group_counts = analyze_market_trends(csv_path)
    
    if group_counts:
        print("\nMarket Demand Summary:")
        for group, count in sorted(group_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"- {group}: {count} jobs")
        
        print("\n✅ All artifacts generated in 'outputs/' folder:")
        print("- market_groups.png (Bar chart)")
        print("- skill_network.png (Co-occurrence Graph)")
        print("- java_roadmap.md (Data-driven learning guide)")

if __name__ == "__main__":
    main()
