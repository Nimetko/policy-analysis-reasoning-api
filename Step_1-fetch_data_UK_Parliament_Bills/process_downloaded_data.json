import json
import pandas as pd

# Load the JSON file
with open("bills_data.json", "r", encoding="utf-8") as f:
    bills = json.load(f)

# Prepare a list of simplified bill dicts
flat_bills = []
for bill in bills:
    flat_bills.append({
        "billId": bill.get("billId"),
        "shortTitle": bill.get("shortTitle"),
        "currentHouse": bill.get("currentHouse"),
        "originatingHouse": bill.get("originatingHouse"),
        "lastUpdate": bill.get("lastUpdate"),
        "billWithdrawn": bill.get("billWithdrawn"),
        "isDefeated": bill.get("isDefeated"),
        "isAct": bill.get("isAct"),
        "currentStage_description": bill.get("currentStage", {}).get("description"),
        "currentStage_house": bill.get("currentStage", {}).get("house"),
        "currentStage_abbreviation": bill.get("currentStage", {}).get("abbreviation")
    })

# Convert to pandas DataFrame
df = pd.DataFrame(flat_bills)

# Save to CSV (optional, good for SQL import)
df.to_csv("flat_bills.csv", index=False)

print("Flattened bills saved to flat_bills.csv!")

