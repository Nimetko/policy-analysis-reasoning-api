import requests
import json
import math

BASE_URL = "https://bills-api.parliament.uk/api/v1/Bills"

all_bills = []

# Step 1: First request to get totalResults
params = {
    "PageSize": 20,  # Doesn't matter, API limits to 20
    "Skip": 0
}

print(f"Fetching first page to find total results...")

response = requests.get(BASE_URL, params=params)
if response.status_code != 200:
    print(f"Failed to fetch data: {response.status_code}")
    exit()

data = response.json()
total_results = data.get("totalResults", 0)
print(f"Total bills found: {total_results}")

# Save first 20 bills
bills = data.get("items", [])
all_bills.extend(bills)

# Step 2: Calculate how many pages
pages_needed = math.ceil(total_results / 20)
print(f"Total pages needed: {pages_needed}")

# Step 3: Fetch all other pages
for page in range(1, pages_needed):
    skip = page * 20
    print(f"Fetching bills with skip={skip}...")
    params = {
        "PageSize": 20,  # Always 20
        "Skip": skip
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code != 200:
        print(f"Failed to fetch data at skip={skip}: {response.status_code}")
        break

    data = response.json()
    bills = data.get("items", [])
    all_bills.extend(bills)

print(f"✅ Successfully fetched {len(all_bills)} bills total!")

# Step 4: Save to JSON
with open("bills_data.json", "w", encoding="utf-8") as f:
    json.dump(all_bills, f, ensure_ascii=False, indent=2)

print("✅ Bills data saved to bills_full_dataset.json!")
