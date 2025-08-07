import subprocess
import sys
import time
from datetime import datetime

def run_script(script_name, max_retries=3, retry_delay=5):
    """
    Run a Python script and return its status.
    
    Args:
        script_name (str): Name of the script to run
        max_retries (int): Maximum number of retries if script fails
        retry_delay (int): Seconds to wait between retries
        
    Returns:
        tuple: (success: bool, output: str, error: str)
    """
    retries = 0
    
    while retries < max_retries:
        try:
            print(f"\n{'='*50}")
            print(f"Running {script_name} - Attempt {retries + 1}/{max_retries}")
            print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*50}\n")
            
            # Run the script and capture output
            result = subprocess.run(
                [sys.executable, script_name],
                capture_output=True,
                text=True,
                check=True
            )
            
            print(f"\n{script_name} completed successfully")
            return (True, result.stdout, result.stderr)
            
        except subprocess.CalledProcessError as e:
            retries += 1
            print(f"\n{script_name} failed with error: {e.stderr}")
            
            if retries < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"Maximum retries ({max_retries}) reached for {script_name}")
                return (False, e.stdout, e.stderr)
                
        except Exception as e:
            print(f"\nUnexpected error running {script_name}: {str(e)}")
            return (False, "", str(e))

def main():
    # Configuration


    SCRIPTS = [
    r"C:\path\to\check_data_availability.py",
    r"C:\path\to\data_fetcher.py",
    r"C:\path\to\update_master_excel.py"
    ]

    SCRIPTS = [
        "check_data_availability.py",
        "data_fetcher.py",
        "update_master_excel.py"
    ]
    
    # Track overall status
    overall_success = True
    status_report = []
    
    print("Starting data processing workflow...")
    start_time = datetime.now()
    
    for i, script in enumerate(SCRIPTS, 1):
        # For the first script, just run it
        if i == 1:
            success, output, error = run_script(script)
        else:
            # For subsequent scripts, only run if previous succeeded
            if not overall_success:
                print(f"\nSkipping {script} because previous step failed")
                success = False
            else:
                success, output, error = run_script(script)
        
        # Update status
        overall_success = overall_success and success
        
        # Record status for report
        status_report.append({
            "script": script,
            "success": success,
            "start_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "end_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        # If any step fails, we can choose to stop the workflow
        if not success:
            print(f"\nWorkflow stopped at {script}")
            break
    
    # Generate final report
    print("\n" + "="*80)
    print("WORKFLOW COMPLETION REPORT")
    print(f"Total time: {datetime.now() - start_time}")
    print("="*80)
    
    for report in status_report:
        status = "SUCCESS" if report["success"] else "FAILED"
        print(f"{report['script']:<30} {status:<10} {report['start_time']}")
    
    print("="*80 + "\n")
    
    # Return appropriate exit code
    sys.exit(0 if overall_success else 1)

if __name__ == "__main__":
    main()
