import subprocess
import sys
import time
import logging
from typing import Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('pipeline.log')
    ]
)
logger = logging.getLogger(__name__)

def run_script(script_path: str) -> Tuple[bool, str]:
    """Run a Python script and return its success status and output."""
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            check=True,
            text=True,
            capture_output=True
        )
        logger.info(f"Script {script_path} executed successfully")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Script {script_path} failed with error: {e.stderr}")
        return False, e.stderr

def check_data_availability() -> bool:
    """Run the data availability check script."""
    logger.info("Checking data availability...")
    success, output = run_script("check_data_availability.py")
    
    if success:
        if "data ready" in output.lower():
            logger.info("Data is available for processing")
            return True
        else:
            logger.info("Data is not yet available")
            return False
    else:
        logger.error("Data availability check failed")
        return False

def fetch_data() -> bool:
    """Run the data fetcher script."""
    logger.info("Fetching data...")
    success, _ = run_script("data_fetcher.py")
    return success

def update_master_sheet() -> bool:
    """Run the master sheet update script."""
    logger.info("Updating master Excel sheet...")
    success, _ = run_script("update_master_sheet.py")
    return success

def main():
    """Main driver function for the data processing pipeline."""
    logger.info("Starting data processing pipeline")
    
    # Step 1: Check data availability with retries
    max_retries = 3
    retry_delay = 60  # seconds
    data_ready = False
    
    for attempt in range(1, max_retries + 1):
        logger.info(f"Data availability check attempt {attempt}/{max_retries}")
        data_ready = check_data_availability()
        
        if data_ready:
            break
        
        if attempt < max_retries:
            logger.info(f"Waiting {retry_delay} seconds before next check...")
            time.sleep(retry_delay)
    
    if not data_ready:
        logger.error("Data not available after maximum retries. Exiting.")
        sys.exit(1)
    
    # Step 2: Fetch data
    if not fetch_data():
        logger.error("Data fetching failed. Exiting.")
        sys.exit(1)
    
    # Step 3: Update master sheet
    if not update_master_sheet():
        logger.error("Master sheet update failed. Exiting.")
        sys.exit(1)
    
    logger.info("Data processing pipeline completed successfully")

if __name__ == "__main__":
    main()