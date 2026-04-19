import os
import argparse
import csv
from datetime import datetime
from crawlers.itviec import scrap_itviec
from analytics.intelligence_engine import IntelligenceEngine
from analytics.kaggle_analyzer import KaggleMarketAnalyzer

def main():
    parser = argparse.ArgumentParser(description="Job Market Intelligence Engine v4.0")
    parser.add_argument("--crawl", action="store_true", help="Run the scrapper")
    parser.add_argument("--fetch", action="store_true", help="Fetch SO benchmarks")
    parser.add_argument("--kaggle", action="store_true", help="Run Kaggle global analysis")
    parser.add_argument("--benchmark", action="store_true", help="Generate synthetic Kaggle benchmarks for demo")
    parser.add_argument("--analyze", action="store_true", help="Run Intelligence Engine (SO/Local)")
    
    args = parser.parse_args()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 0. Generate Benchmarks (Internal Utility)
    if args.benchmark:
        from scripts.generate_benchmarks import generate_synthetic_kaggle_data
        generate_synthetic_kaggle_data()

    # 1. Crawl (if requested)
    if args.crawl:
        print("\n--- Scraping Market Data ---")
        results = scrap_itviec(limit=500)
        # ... (rest of crawl logic)

    # 2. Intelligence Engine Analysis (SO + ITviec)
    if args.analyze:
        print("\n--- Running Intelligence Engine (SO + ITviec Correlation) ---")
        engine = IntelligenceEngine()
        engine.load_all_sources(data_dir="data")
        report_path = engine.run_agentic_analysis()
        if report_path:
            print(f"\n[DONE] Strategic Market Intelligence Report: {report_path}")

    # 3. Kaggle Specialized Analysis (Global Trends)
    if args.kaggle:
        print("\n--- Running Global AI Market Analysis (Kaggle Insights) ---")
        analyzer = KaggleMarketAnalyzer()
        analyzer.run_all()

if __name__ == "__main__":
    main()
