import subprocess
import sys
import time
import logging
import os
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
        # Use absolute path for better reliability on Windows
        abs_path = os.path.abspath(script_path)
        
        result = subprocess.run(
            [sys.executable, abs_path],
            check=True,
            text=True,
            capture_output=True,
            shell=True  # Helps with some Windows command processing
        )
        logger.info(f"Script {script_path} executed successfully")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Script {script_path} failed with error: {e.stderr}")
        return False, e.stderr
    except Exception as e:
        logger.error(f"Unexpected error running {script_path}: {str(e)}")
        return False, str(e)

# ... rest of the code remains the same ...