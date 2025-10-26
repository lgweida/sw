# Tidal Automation Guide

## Table of Contents
1. [Introduction to Tidal Automation](#introduction-to-tidal-automation)
2. [Python REST API Scripts](#python-rest-api-scripts)
3. [Job Export/Import Operations](#job-exportimport-operations)
4. [Job Definition Samples](#job-definition-samples)
5. [Web Client Version Comparison](#web-client-version-comparison)

## Introduction to Tidal Automation

Tidal Automation is an enterprise job scheduling and workload automation platform, now owned by Redwood Software after being acquired from Cisco in 2023.

### Key Capabilities
- Cross-platform scheduling (Windows, Linux, Unix, SAP, Databases, Cloud)
- Workflow orchestration
- Centralized management and monitoring
- Calendar-based scheduling
- Robust error handling and alerting

## Python REST API Scripts

### Listing Jobs Created by Current User

```python
import requests
import json
from typing import List, Dict, Optional

class TidalAutomationClient:
    def __init__(self, base_url: str, username: str, password: str, verify_ssl: bool = True):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.verify_ssl = verify_ssl
    
    def get_my_jobs(self, created_by: str = None) -> List[Dict]:
        if created_by is None:
            created_by = self.username
        
        jobs_url = f"{self.base_url}/api/jobs"
        params = {'createdBy': created_by}
        
        try:
            response = self.session.get(jobs_url, params=params, verify=self.verify_ssl)
            response.raise_for_status()
            jobs_data = response.json()
            
            # Handle different response formats
            if isinstance(jobs_data, dict) and 'jobs' in jobs_data:
                return jobs_data['jobs']
            elif isinstance(jobs_data, dict) and 'items' in jobs_data:
                return jobs_data['items']
            elif isinstance(jobs_data, list):
                return jobs_data
            else:
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch jobs: {e}")
            return []
```

### Usage Examples
```bash
# Basic usage
python tidal_jobs.py --base-url "https://tidal.company.com" --username "yourname" --password "yourpass"

# With SSL disabled and JSON output
python tidal_jobs.py --base-url "https://tidal.company.com" --username "yourname" --password "yourpass" --no-ssl-verify --format json

# Limited results
python tidal_jobs.py --base-url "https://tidal.company.com" --username "yourname" --password "yourpass" --max-results 50
```

## Job Export/Import Operations

### Complete Job Management Script

```python
class TidalJobManager:
    def export_job(self, job_id: str, export_format: str = 'json') -> Optional[Dict]:
        """Export a job definition"""
        try:
            job_url = f"{self.base_url}/api/jobs/{job_id}"
            response = self.session.get(job_url, verify=self.verify_ssl)
            response.raise_for_status()
            job_definition = response.json()
            return self._clean_job_definition(job_definition)
        except requests.exceptions.RequestException as e:
            print(f"Failed to export job {job_id}: {e}")
            return None
    
    def import_job(self, job_definition: Dict, new_job_name: str = None) -> Optional[Dict]:
        """Import a job definition to create a new job"""
        try:
            import_definition = self._prepare_for_import(job_definition, new_job_name)
            create_url = f"{self.base_url}/api/jobs"
            response = self.session.post(create_url, json=import_definition, verify=self.verify_ssl)
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                print(f"Failed to create job: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Failed to import job: {e}")
            return None
```

### Export/Import Commands

```bash
# Export all jobs to JSON
python tidal_job_manager.py --base-url "https://tidal.company.com" --username "yourname" --password "yourpass" export --output-dir "./my_jobs" --format json

# Export specific job
python tidal_job_manager.py --base-url "https://tidal.company.com" --username "yourname" --password "yourpass" export --job-id "JOB_12345" --output-dir "./single_job"

# Import single job
python tidal_job_manager.py --base-url "https://tidal.company.com" --username "yourname" --password "yourpass" import --file "./my_jobs/daily_report_JOB_12345.json"

# Import all jobs from directory
python tidal_job_manager.py --base-url "https://tidal.company.com" --username "yourname" --password "yourpass" import --directory "./my_jobs"
```

## Job Definition Samples

### Basic Job Definition

```json
{
  "name": "Daily_Sales_Report_ETL",
  "description": "Extract, transform and load daily sales data from source systems to data warehouse",
  "jobType": "COMMAND",
  "command": {
    "type": "WINDOWS_BATCH",
    "commandLine": "C:\\Scripts\\daily_sales_etl.bat",
    "workingDirectory": "C:\\Scripts\\",
    "parameters": [
      {
        "name": "DATE",
        "value": "$(currentDate-1)"
      }
    ]
  },
  "schedule": {
    "type": "CALENDAR",
    "calendar": "BUSINESS_DAYS",
    "startTime": "02:00",
    "timezone": "America/New_York"
  },
  "notifications": {
    "onSuccess": [
      {
        "type": "EMAIL",
        "recipients": ["etl-team@company.com"],
        "subject": "SUCCESS: Daily Sales ETL completed"
      }
    ],
    "onFailure": [
      {
        "type": "EMAIL", 
        "recipients": ["etl-team@company.com", "on-call-admin@company.com"],
        "subject": "FAILED: Daily Sales ETL job"
      }
    ]
  },
  "properties": {
    "priority": "MEDIUM",
    "maxRunTime": 3600,
    "retryOnFailure": {
      "enabled": true,
      "maxRetries": 3,
      "retryInterval": 300
    }
  }
}
```

### SQL Server Job Example

```json
{
  "name": "Monthly_Financial_Close",
  "description": "Execute monthly financial closing procedures in SQL Server",
  "jobType": "DATABASE",
  "database": {
    "type": "SQL_SERVER",
    "server": "FINANCE-SQL-01",
    "databaseName": "FinancialDB",
    "commandType": "STORED_PROCEDURE",
    "command": "usp_MonthlyFinancialClose",
    "parameters": [
      {
        "name": "@AccountingMonth",
        "value": "$(currentMonth-1)"
      }
    ]
  },
  "schedule": {
    "type": "CALENDAR",
    "calendar": "MONTH_END",
    "startTime": "20:00"
  }
}
```

### File Transfer Job

```json
{
  "name": "FTP_Sales_Data_Transfer",
  "description": "Transfer daily sales data files to partner FTP server",
  "jobType": "FILE_TRANSFER",
  "fileTransfer": {
    "type": "FTP",
    "source": {
      "server": "internal-sftp.company.com",
      "path": "/outbound/sales/",
      "filePattern": "sales_$(currentDate-1)*.csv"
    },
    "destination": {
      "server": "partner-ftp.example.com",
      "path": "/incoming/sales/"
    }
  },
  "schedule": {
    "type": "CALENDAR", 
    "calendar": "BUSINESS_DAYS",
    "startTime": "03:30"
  }
}
```

## Web Client Version Comparison

### Method 1: Job History/Version Comparison

1. **Navigate to the Job**
   - Go to **Jobs** tab
   - Click on the job name to open details

2. **Access Version History**
   - Look for **"History"**, **"Versions"**, or **"Audit"** tab
   - Right-click job → **"View History"** or **"Version History"**

3. **Compare Versions**
   - Select two versions with checkboxes
   - Click **"Compare"** or **"Diff"** button

4. **Review Differences**
   - Added lines (green)
   - Modified lines (yellow) 
   - Deleted lines (red)

### Method 2: Search and Compare Feature

1. Use global search to find jobs
2. Select multiple jobs
3. Use **"Compare Jobs"** from context menu

### Method 3: Export and Compare Manually

```python
# API-based comparison
def compare_job_versions(job_id, version1, version2):
    v1 = tidal_client.get_job_version(job_id, version1)
    v2 = tidal_client.get_job_version(job_id, version2)
    
    import difflib
    diff = difflib.unified_diff(
        json.dumps(v1, indent=2).splitlines(),
        json.dumps(v2, indent=2).splitlines(),
        fromfile=f"Version {version1}",
        tofile=f"Version {version2}"
    )
    
    print('\n'.join(diff))
```

### Comparison Points
- **Job Definitions**: Command lines, scripts, parameters
- **Schedules**: Timing, calendars, dependencies  
- **Resources**: Servers, queues, file paths
- **Notifications**: Alert rules, recipients
- **Properties**: Timeouts, retry settings, priorities

## Important Notes

- **API Endpoints**: May vary by Tidal/Redwood version
- **Authentication**: Adjust for token-based auth if needed
- **Field Mapping**: Some fields may be read-only
- **Testing**: Always test in non-production first
- **Security**: Use environment variables for credentials in production

This guide provides comprehensive coverage of Tidal Automation operations including API scripting, job management, and web client features for effective workload automation management.