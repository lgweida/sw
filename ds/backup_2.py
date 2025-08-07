import os
import shutil
from datetime import datetime
import subprocess

def backup_metric_data():
    # Define paths
    metric_data_dir = 'metric_data'
    
    # Check if metric_data directory exists
    if not os.path.exists(metric_data_dir):
        print(f"Directory {metric_data_dir} does not exist. Nothing to backup.")
        return
    
    # Get current date in YYYY-MM-DD format
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    # Create backup directory name
    backup_dir_name = f"metric_data_{current_date}"
    
    # Check if backup directory already exists
    counter = 1
    while os.path.exists(backup_dir_name):
        backup_dir_name = f"metric_data_{current_date}_{counter}"
        counter += 1
    
    # Rename (move) the directory
    try:
        shutil.move(metric_data_dir, backup_dir_name)
        print(f"Successfully backed up {metric_data_dir} to {backup_dir_name}")
    except Exception as e:
        print(f"Error backing up {metric_data_dir}: {e}")
        return False
    
    return True

def run_data_fetcher():
    # Assuming data_fetcher is a Python script
    fetcher_script = 'data_fetcher.py'
    
    # Check if script exists
    if not os.path.exists(fetcher_script):
        print(f"Error: {fetcher_script} not found.")
        return False
    
    # Run the script
    try:
        result = subprocess.run(['python', fetcher_script], check=True)
        print(f"Successfully executed {fetcher_script}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing {fetcher_script}: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error running {fetcher_script}: {e}")
        return False

def main():
    print("Starting backup and data fetch process...")
    
    # Step 1: Backup existing metric_data
    if backup_metric_data():
        # Step 2: Run data fetcher only if backup succeeded
        run_data_fetcher()
    
    print("Process completed.")

if __name__ == "__main__":
    main()