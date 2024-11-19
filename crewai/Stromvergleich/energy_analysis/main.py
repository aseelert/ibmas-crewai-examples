import sys
import os
from datetime import datetime
from dotenv import load_dotenv
from energy_analysis.crew import EnergyAnalysisCrew

def run():
    """
    Run the Energy Analysis crew
    """
    # Load environment variables
    load_dotenv()

    # Verify Serper API key is available
    if not os.getenv("SERPER_API_KEY"):
        raise ValueError("SERPER_API_KEY environment variable is not set")

    inputs = {
        'current_year': datetime.now().year,
        'zip_code': '09113'
    }
    EnergyAnalysisCrew().crew().kickoff(inputs=inputs)

if __name__ == "__main__":
    run()