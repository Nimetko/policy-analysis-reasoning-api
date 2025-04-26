import requests
import json

# Base URL
BASE_URL = "https://bills-api.parliament.uk/api/v1/Bills"  # <- Important: Corrected endpoint

# Set page size and start page
params = {
    "PageSize": 100,  # Note: P should be capital
    "Page": 1
}

all_bills = []  # List to store bills

# Loop to fetch 500 bills
while len(all_bills) < 500:
    print(f"Fetching page {params['Page']}...")
    response = requests.get(BASE_URL, params=params)

    if response.status_code != 200:
        print(f"Failed to fetch page {params['Page']}: {response.status_code}")
        break

    data = response.json()
    bills = data.get("items", [])
    
    if not bills:
        print("No more bills found.")
        break

    all_bills.extend(bills)
    params["Page"] += 1

# Limit to exactly 500 if needed
all_bills = all_bills[:500]

# Save to JSON file
with open("bills_data.json", "w", encoding="utf-8") as f:
    json.dump(all_bills, f, ensure_ascii=False, indent=2)

print(f"Successfully fetched {len(all_bills)} bills!")
