import csv
import json
from scraper import scrap_itviec

def main():
    print("Starting crawler...")
    # Scrape first 3 pages for each category, limit 100 total results
    results = scrap_itviec(page_num=3, limit=100)
    
    if not results:
        print("No results found.")
        return

    # Focus on skills_and_experience as requested
    # We will keep Title and Company so the user knows which job it belongs to
    output_data = []
    for entry in results:
        output_data.append({
            'Title': entry.get('title'),
            'Company': entry.get('company'),
            'Skills and Experience': entry.get('skills_and_experience')
        })

    # Export to JSON
    json_file = 'itviec_jobs.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(f"Exported to {json_file}")

    # Export to CSV
    csv_file = 'itviec_jobs.csv'
    keys = output_data[0].keys()
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(output_data)
    print(f"Exported to {csv_file}")

if __name__ == "__main__":
    main()
