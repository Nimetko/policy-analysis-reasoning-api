import pandas as pd

# Load dataset
df = pd.read_csv("bills_with_policy_area_full.csv")

# Drop rows without a policyArea (if any)
df = df.dropna(subset=["policyArea"])

# Count total and rejected bills per policy area
summary = (
    df.groupby("policyArea")
    .agg(total_bills=("billId", "count"),
         rejected_bills=("isAct", lambda x: (~x).sum()))
    .reset_index()
)

# Calculate rejection rate
summary["rejection_rate_percent"] = (summary["rejected_bills"] / summary["total_bills"] * 100).round(2)

# Sort by rejection rate
summary = summary.sort_values(by="rejection_rate_percent", ascending=False)

# Display result
print(summary.to_string(index=False))

