# Tidal Automation API - Python Script Documentation

## Conversation Summary

### Initial Question
**User:** Do you know tidal automation software?

### Response
Yes, Tidal Automation (now known as Tidal Software) is an enterprise workload automation and job scheduling platform used to orchestrate and manage complex batch processes, data workflows, and IT operations across different systems and platforms.

#### Key Features

- **Job scheduling** - Automating the execution of jobs across multiple systems (mainframes, Unix/Linux, Windows, cloud platforms)
- **Workflow orchestration** - Managing dependencies between jobs and creating complex workflows
- **Monitoring and alerts** - Real-time visibility into job status and automated notifications
- **Cross-platform support** - Integrating diverse IT environments
- **Compliance and auditing** - Tracking job execution for regulatory requirements

#### Common Use Cases
Tidal is commonly used in large enterprises for tasks like:
- ETL processes
- File transfers
- Database backups
- Report generation
- Coordinating complex business processes that run on schedules

---

## Python Script Request

**User:** Write a python script to list all jobs created by me through REST API

### Solution Overview
A Python script was created to interact with the Tidal Automation REST API to retrieve and display all jobs created by a specific user.

---

## Python Script Code

```python
import requests
import json
from requests.auth import HTTPBasicAuth

# Tidal Configuration
TIDAL_BASE_URL = "https://your-tidal-server:port/api"  # Update with your Tidal server URL
USERNAME = "your_username"  # Update with your username
PASSWORD = "your_password"  # Update with your password

# Optional: If using token-based authentication instead
# API_TOKEN = "your_api_token"

def get_jobs_by_user(username):
    """
    Retrieve all jobs created by a specific user from Tidal Automation
    """
    
    # API endpoint for jobs
    endpoint = f"{TIDAL_BASE_URL}/jobs"
    
    # Headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        # Make the API request with basic authentication
        response = requests.get(
            endpoint,
            auth=HTTPBasicAuth(USERNAME, PASSWORD),
            headers=headers,
            verify=False,  # Set to True in production with proper SSL certificates
            params={"createdBy": username}  # Filter by creator
        )
        
        # Alternative: If using token authentication, uncomment below
        # headers["Authorization"] = f"Bearer {API_TOKEN}"
        # response = requests.get(endpoint, headers=headers, verify=False)
        
        # Check if request was successful
        response.raise_for_status()
        
        # Parse the JSON response
        jobs = response.json()
        
        return jobs
        
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Tidal API: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        return None

def display_jobs(jobs):
    """
    Display job information in a readable format
    """
    if not jobs:
        print("No jobs found or unable to retrieve jobs.")
        return
    
    # Handle different response formats
    job_list = jobs if isinstance(jobs, list) else jobs.get('jobs', [])
    
    if not job_list:
        print("No jobs found for this user.")
        return
    
    print(f"\nFound {len(job_list)} job(s):\n")
    print("-" * 80)
    
    for idx, job in enumerate(job_list, 1):
        print(f"\nJob #{idx}")
        print(f"  Job Name: {job.get('name', 'N/A')}")
        print(f"  Job ID: {job.get('id', 'N/A')}")
        print(f"  Description: {job.get('description', 'N/A')}")
        print(f"  Status: {job.get('status', 'N/A')}")
        print(f"  Created By: {job.get('createdBy', 'N/A')}")
        print(f"  Created Date: {job.get('createdDate', 'N/A')}")
        print(f"  Job Type: {job.get('jobType', 'N/A')}")
        print("-" * 80)

def save_to_file(jobs, filename="my_tidal_jobs.json"):
    """
    Save job data to a JSON file
    """
    try:
        with open(filename, 'w') as f:
            json.dump(jobs, f, indent=2)
        print(f"\nJob data saved to {filename}")
    except Exception as e:
        print(f"Error saving to file: {e}")

if __name__ == "__main__":
    print("Fetching jobs from Tidal Automation...")
    print(f"User: {USERNAME}\n")
    
    # Get jobs created by the user
    jobs = get_jobs_by_user(USERNAME)
    
    # Display the jobs
    display_jobs(jobs)
    
    # Optional: Save to file
    if jobs:
        save_to_file(jobs)
```

---

## Setup Instructions

### Prerequisites
1. Install the `requests` library:
   ```bash
   pip install requests
   ```

### Configuration
Update the following variables in the script:

| Variable | Description | Example |
|----------|-------------|---------|
| `TIDAL_BASE_URL` | Your Tidal server URL and port | `https://tidal.company.com:8443/api` |
| `USERNAME` | Your Tidal username | `john.doe` |
| `PASSWORD` | Your Tidal password | `your_secure_password` |

### Alternative Authentication
If your Tidal instance uses token-based authentication, uncomment and use the token authentication section in the code.

---

## Script Features

### 1. Get Jobs by User
- Fetches all jobs created by the specified user
- Uses REST API with proper authentication
- Includes error handling for connection issues

### 2. Display Jobs
- Shows job details in a readable format
- Displays the following information:
  - Job Name
  - Job ID
  - Description
  - Status
  - Created By
  - Created Date
  - Job Type

### 3. Save to File
- Optionally saves job data to a JSON file (`my_tidal_jobs.json`)
- Formatted with proper indentation for readability

---

## Important Notes

### API Endpoint Variations
The exact API endpoint and response format may vary depending on your Tidal version. You might need to adjust:

- **Endpoint URL**: `/jobs` vs `/job-definitions` vs `/job-instances`
- **Filter Parameter**: `createdBy` vs `owner` vs other field names
- **Response Structure**: Based on your Tidal API documentation

### Security Considerations
1. **SSL Verification**: The script currently has `verify=False` for SSL. In production, set this to `True` and ensure proper SSL certificates are configured.
2. **Credentials**: Never hardcode credentials in production. Consider using:
   - Environment variables
   - Configuration files (not committed to version control)
   - Secret management systems

### Best Practices
1. Consult your Tidal API documentation for exact endpoints
2. Test the script in a development environment first
3. Implement proper credential management
4. Add logging for production use
5. Handle pagination if you have many jobs

---

## Example Output

```
Fetching jobs from Tidal Automation...
User: john.doe

Found 3 job(s):

--------------------------------------------------------------------------------

Job #1
  Job Name: Daily Data ETL
  Job ID: 12345
  Description: Daily ETL process for customer data
  Status: Active
  Created By: john.doe
  Created Date: 2024-10-15T10:30:00Z
  Job Type: Script
--------------------------------------------------------------------------------

Job #2
  Job Name: Weekly Report Generation
  Job ID: 12346
  Description: Generate weekly sales reports
  Status: Active
  Created By: john.doe
  Created Date: 2024-10-20T14:00:00Z
  Job Type: Report
--------------------------------------------------------------------------------

Job data saved to my_tidal_jobs.json
```

---

## Troubleshooting

### Common Issues

1. **Connection Error**: Check that the `TIDAL_BASE_URL` is correct and accessible
2. **Authentication Failed**: Verify username and password are correct
3. **Empty Results**: Check the filter parameter name (`createdBy`) matches your API version
4. **JSON Parse Error**: The API response format might be different; check the raw response

### Next Steps

For specific API documentation, consult your Tidal Automation administrator or refer to your version's API documentation.

---

*Document created: October 26, 2025*