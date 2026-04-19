import argparse
from analytics.intelligence_engine import IntelligenceEngine
from config.settings import RAW_DATA_DIR


def run_main():
    parser = argparse.ArgumentParser(
        description="Market Intelligence Engine v6.1 - CLI Control"
    )

    # Core Actions
    parser.add_argument(
        "--flow",
        action="store_true",
        help="Run the full end-to-end Intelligence Flow (8-Vector Analysis)",
    )
    parser.add_argument(
        "--extract",
        action="store_true",
        help="Run the raw dataset extraction utility from data/ folder",
    )
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Generate synthetic benchmark data (for testing purposes)",
    )

    # Options
    parser.add_argument('--dir', type=str, default=str(RAW_DATA_DIR), help="Override the raw data directory")
    parser.add_argument('--limit', type=int, default=20, help="Limit for crawler or analysis results")

    args = parser.parse_args()

    # Logo / Header
    print("\n" + "="*50)
    print(" MARKET INTELLIGENCE ENGINE v6.1")
    print("="*50 + "\n")

    if args.itviec:
        from crawlers.itviec import run_itviec_crawler
        run_itviec_crawler(limit=args.limit)
        return

    if args.extract:
        # Import internally to avoid circular dependencies
        from scripts.extract_datasets import extract_all

        extract_all()
        return

    if args.benchmark:
        from scripts.generate_benchmarks import generate_synthetic_kaggle_data

        generate_synthetic_kaggle_data()
        return

    if args.flow:
        engine = IntelligenceEngine(raw_dir=args.dir)
        engine.load_all_sources()
        report = engine.run_agentic_analysis()
        if report:
            print(f"\n[SUCCESS] Analysis Complete: {report}")
        return

    # Default action if no args
    parser.print_help()


if __name__ == "__main__":
    run_main()
