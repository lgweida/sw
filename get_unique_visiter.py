import requests

url = "https://api.similarweb.com/v1/website/openai.com/unique-visitors/desktop_unique_visitors?api_key=8e1c8a24317d47a0a1eac314ab7aea88&start_date=2023-06&end_date=2025-06&country=world&granularity=monthly&main_domain_only=false&format=json&show_verified=false&mtd=false"

headers = {"accept": "application/json"}

response = requests.get(url, headers=headers)

print(response.text)
