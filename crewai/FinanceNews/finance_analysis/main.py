import sys
import os
from datetime import datetime
from dotenv import load_dotenv
from finance_analysis.crew import FinancialAnalysisCrew

def run():
    """
    Run the Financial Analysis crew
    """
    # Load environment variables
    load_dotenv()

    # Verify required API keys are available
    if not os.getenv("SERPER_API_KEY"):
        raise ValueError("SERPER_API_KEY environment variable is not set")

    # Define company symbols for yfinance
    company_data = {
        'IBM': 'IBM',
        'Infosys': 'INFY',
        'Accenture': 'ACN'
    }

    inputs = {
        'company_names': list(company_data.keys()),
        'company_symbols': list(company_data.values()),
        'current_year': datetime.now().year,
        'last_year': datetime.now().year - 1
    }

    # Create crew instance
    crew = FinancialAnalysisCrew()

    # Download stock data first
    data_dir = crew.download_all_stock_data(company_data.values())
    print(f"Stock data downloaded to: {data_dir}")

    # Run the analysis
    crew.crew().kickoff(inputs=inputs)

if __name__ == "__main__":
    run()