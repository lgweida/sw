import requests
from typing import Dict, Any, Optional

# SimilarWeb API configuration dictionary
SIMILARWEB_API_CONFIG = {
    "base_url": "https://api.similarweb.com/v1/website",
    "endpoints": {
        "visits": {
            "path": "/total-traffic-and-engagement/visits",
            "method": "GET",
            "headers": {
                "accept": "application/json"
            },
            "path_params": {
                "domain_name": {
                    "type": "string",
                    "required": True,
                    "default": "amazon.com",
                    "description": "Enter website of interest, without 'www.' or brackets {}"
                }
            },
            "query_params": {
                "api_key": {
                    "type": "string",
                    "required": True,
                    "default": "Add_Your_API_KEY",
                    "description": "Your Similarweb API key."
                },
                "start_date": {
                    "type": "string",
                    "required": False,
                    "default": "2023-01",
                    "description": "Start month (format: YYYY-MM)"
                },
                "end_date": {
                    "type": "string",
                    "required": False,
                    "default": "2023-03",
                    "description": "End month (format: YYYY-MM)"
                },
                "country": {
                    "type": "string",
                    "required": True,
                    "default": "us",
                    "description": "Country filter, as a 2-letter ISO country code, or 'world' for worldwide"
                },
                "granularity": {
                    "type": "string",
                    "required": True,
                    "default": "monthly",
                    "description": "Set the granularity for the returned values. Can be 'daily', 'weekly' or 'monthly'"
                },
                "main_domain_only": {
                    "type": "string",
                    "required": False,
                    "default": "false",
                    "description": "Return values for the main domain only ('true'), or include also the subdomains ('false')"
                },
                "format": {
                    "type": "string",
                    "required": False,
                    "default": "json",
                    "description": "Format in which the reply should be returned. Possible values: 'json' (default) or 'xml'"
                },
                "show_verified": {
                    "type": "string",
                    "required": False,
                    "default": "false",
                    "description": "Show shared Google Analytics data when available"
                },
                "mtd": {
                    "type": "string",
                    "required": False,
                    "default": "false",
                    "description": "When 'true', end_date is set to the latest available days' data (month-to-date)"
                },
                "engaged_only": {
                    "type": "string",
                    "required": False,
                    "default": "false",
                    "description": "When 'true', the data is filtered by 'engaged visits' only"
                }
            }
        },
        "pages_per_visit": {
            "path": "/total-traffic-and-engagement/pages-per-visit",
            "method": "GET",
            "headers": {
                "accept": "application/json"
            },
            "path_params": {
                "domain_name": {
                    "type": "string",
                    "required": True,
                    "default": "amazon.com",
                    "description": "Enter website of interest, without 'www.' or brackets {}"
                }
            },
            "query_params": {
                "api_key": {
                    "type": "string",
                    "required": True,
                    "default": "Add_Your_API_KEY",
                    "description": "Your Similarweb API key."
                },
                "start_date": {
                    "type": "string",
                    "required": False,
                    "default": "2023-01",
                    "description": "Start month (format: YYYY-MM)"
                },
                "end_date": {
                    "type": "string",
                    "required": False,
                    "default": "2023-03",
                    "description": "End month (format: YYYY-MM)"
                },
                "country": {
                    "type": "string",
                    "required": True,
                    "default": "us",
                    "description": "Country filter, as a 2-letter ISO country code, or 'world' for worldwide"
                },
                "granularity": {
                    "type": "string",
                    "required": True,
                    "default": "monthly",
                    "description": "Set the granularity for the returned values. Can be 'daily', 'weekly' or 'monthly'"
                },
                "main_domain_only": {
                    "type": "string",
                    "required": False,
                    "default": "false",
                    "description": "Return values for the main domain only ('true'), or include also the subdomains ('false')"
                },
                "format": {
                    "type": "string",
                    "required": False,
                    "default": "json",
                    "description": "Format in which the reply should be returned. Possible values: 'json' (default) or 'xml'"
                },
                "show_verified": {
                    "type": "string",
                    "required": False,
                    "default": "false",
                    "description": "Show shared Google Analytics data when available"
                },
                "mtd": {
                    "type": "string",
                    "required": False,
                    "default": "false",
                    "description": "When 'true', end_date is set to the latest available days' data (month-to-date)"
                },
                "engaged_only": {
                    "type": "string",
                    "required": False,
                    "default": "false",
                    "description": "When 'true', the data is filtered by 'engaged visits' only"
                }
            }
        }
    }
}


class SimilarWebAPIClient:
    """
    A client class for making dynamic requests to SimilarWeb API endpoints
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.config = SIMILARWEB_API_CONFIG
    
    def build_url(self, endpoint_name: str, domain_name: str) -> str:
        """Build the complete URL for an endpoint"""
        endpoint_config = self.config["endpoints"][endpoint_name]
        return f"{self.config['base_url']}/{domain_name}{endpoint_config['path']}"
    
    def build_params(self, endpoint_name: str, **kwargs) -> Dict[str, str]:
        """Build query parameters for an endpoint with defaults and overrides"""
        endpoint_config = self.config["endpoints"][endpoint_name]
        params = {}
        
        # Set API key
        params["api_key"] = self.api_key
        
        # Add default values for query parameters
        for param_name, param_config in endpoint_config["query_params"].items():
            if param_name != "api_key":  # Skip api_key as it's already set
                if param_name in kwargs:
                    params[param_name] = str(kwargs[param_name])
                else:
                    params[param_name] = param_config["default"]
        
        return params
    
    def make_request(self, endpoint_name: str, domain_name: str, **kwargs) -> requests.Response:
        """Make a request to the specified endpoint with parameters"""
        endpoint_config = self.config["endpoints"][endpoint_name]
        
        url = self.build_url(endpoint_name, domain_name)
        params = self.build_params(endpoint_name, **kwargs)
        headers = endpoint_config["headers"]
        
        response = requests.get(url, params=params, headers=headers)
        return response
    
    def get_visits(self, domain_name: str = "amazon.com", **kwargs) -> requests.Response:
        """Get visits data for a domain"""
        return self.make_request("visits", domain_name, **kwargs)
    
    def get_pages_per_visit(self, domain_name: str = "amazon.com", **kwargs) -> requests.Response:
        """Get pages per visit data for a domain"""
        return self.make_request("pages_per_visit", domain_name, **kwargs)


# Example usage:
if __name__ == "__main__":
    # Initialize the client with your API key
    client = SimilarWebAPIClient("YOUR_API_KEY_HERE")
    
    # Example 1: Get visits data with default parameters
    response = client.get_visits("amazon.com")
    
    # Example 2: Get visits data with custom parameters
    response = client.get_visits(
        domain_name="amazon.com",
        start_date="2024-01",
        end_date="2024-06",
        country="world",
        granularity="monthly"
    )
    
    # Example 3: Get pages per visit data
    response = client.get_pages_per_visit(
        domain_name="google.com",
        start_date="2024-01",
        end_date="2024-03",
        country="us"
    )
    
    # Check response
    if response.status_code == 200:
        data = response.json()
        print(data)
    else:
        print(f"Error: {response.status_code} - {response.text}")
    
    # Example 4: Direct URL and params building (if you prefer manual control)
    url = client.build_url("visits", "amazon.com")
    params = client.build_params("visits", start_date="2024-01", country="world")
    print(f"URL: {url}")
    print(f"Params: {params}")
