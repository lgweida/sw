#!/usr/bin/env python3
"""
Main driver program to orchestrate data processing pipeline:
1. Check data availability
2. Fetch data when ready
3. Update master Excel sheet

Compatible with Windows, macOS, and Linux environments.
"""

import subprocess
import sys
import time
import logging
import os
import platform
from datetime import datetime
from enum import Enum
from typing import Dict, Any
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class ScriptStatus(Enum):
    """Status codes for script execution"""
    SUCCESS = 0
    FAILED = 1
    DATA_NOT_READY = 2
    TIMEOUT = 3

class PipelineDriver:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Cross-platform script configuration
        self.scripts = {
            'data_checker': 'check_data_availability.py',
            'data_fetcher': 'data_fetcher.py',
            'excel_updater': 'update_master_excel.py'
        }
        
        # Detect platform for Windows-specific handling
        self.is_windows = platform.system().lower() == 'windows'
        self.logger.info(f"Running on {platform.system()} {platform.release()}")
        
        # Configuration
        self.max_retries = 3
        self.retry_delay = 60  # seconds
        
        # Ensure script paths exist
        self._validate_scripts()
        
    def _validate_scripts(self):
        """Validate that all script files exist"""
        missing_scripts = []
        for name, script_path in self.scripts.items():
            if not Path(script_path).exists():
                missing_scripts.append(f"{name}: {script_path}")
        
        if missing_scripts:
            self.logger.warning("Warning: Some scripts not found:")
            for script in missing_scripts:
                self.logger.warning(f"  - {script}")
            self.logger.warning("Pipeline will fail if these scripts are executed.")
        
    def run_script(self, script_name: str, timeout: int = 300) -> Dict[str, Any]:
        """
        Run a Python script and return execution status
        
        Args:
            script_name: Name of the script to run
            timeout: Maximum execution time in seconds
            
        Returns:
            Dict containing status, return_code, stdout, stderr, and execution_time
        """
        script_path = self.scripts.get(script_name)
        if not script_path:
            return {
                'status': ScriptStatus.FAILED,
                'return_code': -1,
                'stdout': '',
                'stderr': f'Script {script_name} not found in configuration',
                'execution_time': 0
            }
        
        self.logger.info(f"Starting execution of {script_path}")
        start_time = time.time()
        
        try:
            # Windows-compatible command construction
            if self.is_windows:
                # Use python instead of sys.executable for better Windows compatibility
                cmd = ['python', script_path]
                # Alternative: cmd = [sys.executable, script_path]
            else:
                cmd = [sys.executable, script_path]
            
            self.logger.debug(f"Executing command: {' '.join(cmd)}")
            
            # Run the script with timeout
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=False,  # Explicit shell=False for security
                cwd=os.getcwd()  # Explicit working directory
            )
            
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                status = ScriptStatus.SUCCESS
                self.logger.info(f"{script_path} completed successfully in {execution_time:.2f}s")
            elif result.returncode == 2:  # Custom return code for data not ready
                status = ScriptStatus.DATA_NOT_READY
                self.logger.warning(f"{script_path} reports data not ready")
            else:
                status = ScriptStatus.FAILED
                self.logger.error(f"{script_path} failed with return code {result.returncode}")
            
            return {
                'status': status,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'execution_time': execution_time
            }
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            self.logger.error(f"{script_path} timed out after {timeout} seconds")
            return {
                'status': ScriptStatus.TIMEOUT,
                'return_code': -1,
                'stdout': '',
                'stderr': f'Script timed out after {timeout} seconds',
                'execution_time': execution_time
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Error running {script_path}: {str(e)}")
            return {
                'status': ScriptStatus.FAILED,
                'return_code': -1,
                'stdout': '',
                'stderr': str(e),
                'execution_time': execution_time
            }
    
    def wait_for_data_availability(self) -> bool:
        """
        Continuously check for data availability with retries
        
        Returns:
            True if data is available, False if max retries exceeded
        """
        retry_count = 0
        
        while retry_count < self.max_retries:
            self.logger.info(f"Checking data availability (attempt {retry_count + 1}/{self.max_retries})")
            
            result = self.run_script('data_checker')
            
            if result['status'] == ScriptStatus.SUCCESS:
                self.logger.info("Data is available!")
                return True
            elif result['status'] == ScriptStatus.DATA_NOT_READY:
                retry_count += 1
                if retry_count < self.max_retries:
                    self.logger.info(f"Data not ready. Waiting {self.retry_delay} seconds before retry...")
                    time.sleep(self.retry_delay)
            else:
                self.logger.error(f"Data availability check failed: {result['stderr']}")
                return False
        
        self.logger.error(f"Data not available after {self.max_retries} attempts")
        return False
    
    def run_pipeline(self) -> bool:
        """
        Execute the complete data processing pipeline
        
        Returns:
            True if pipeline completed successfully, False otherwise
        """
        pipeline_start = datetime.now()
        self.logger.info("="*50)
        self.logger.info(f"Starting data processing pipeline at {pipeline_start}")
        self.logger.info("="*50)
        
        try:
            # Step 1: Wait for data availability
            self.logger.info("STEP 1: Checking data availability")
            if not self.wait_for_data_availability():
                self.logger.error("Pipeline failed: Data not available")
                return False
            
            # Step 2: Fetch data
            self.logger.info("STEP 2: Fetching data")
            fetch_result = self.run_script('data_fetcher', timeout=600)  # 10 min timeout
            
            if fetch_result['status'] != ScriptStatus.SUCCESS:
                self.logger.error(f"Pipeline failed: Data fetching failed")
                self.logger.error(f"Error: {fetch_result['stderr']}")
                return False
            
            self.logger.info("Data fetching completed successfully")
            
            # Step 3: Update master Excel sheet
            self.logger.info("STEP 3: Updating master Excel sheet")
            excel_result = self.run_script('excel_updater', timeout=300)  # 5 min timeout
            
            if excel_result['status'] != ScriptStatus.SUCCESS:
                self.logger.error(f"Pipeline failed: Excel update failed")
                self.logger.error(f"Error: {excel_result['stderr']}")
                return False
            
            self.logger.info("Excel sheet update completed successfully")
            
            # Pipeline completed successfully
            pipeline_end = datetime.now()
            total_time = (pipeline_end - pipeline_start).total_seconds()
            
            self.logger.info("="*50)
            self.logger.info(f"Pipeline completed successfully!")
            self.logger.info(f"Total execution time: {total_time:.2f} seconds")
            self.logger.info(f"Completed at: {pipeline_end}")
            self.logger.info("="*50)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Pipeline failed with unexpected error: {str(e)}")
            return False
    
    def print_status_report(self):
        """Print a summary of the pipeline configuration"""
        print("\n" + "="*60)
        print("DATA PROCESSING PIPELINE STATUS")
        print("="*60)
        print(f"Platform      : {platform.system()} {platform.release()}")
        print(f"Python version: {sys.version.split()[0]}")
        print(f"Working dir   : {os.getcwd()}")
        print(f"Script configurations:")
        for name, path in self.scripts.items():
            exists = "✓" if Path(path).exists() else "✗"
            print(f"  {name:15}: {path} {exists}")
        print(f"\nRetry settings:")
        print(f"  Max retries   : {self.max_retries}")
        print(f"  Retry delay   : {self.retry_delay} seconds")
        print(f"\nLog file      : pipeline.log")
        print("="*60 + "\n")

def main():
    """Main function to run the pipeline"""
    driver = PipelineDriver()
    
    # Print status report
    driver.print_status_report()
    
    # Run the pipeline
    try:
        success = driver.run_pipeline()
        exit_code = 0 if success else 1
    except KeyboardInterrupt:
        logging.info("Pipeline interrupted by user")
        exit_code = 130
    except Exception as e:
        logging.error(f"Unexpected error in main: {str(e)}")
        exit_code = 1
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()