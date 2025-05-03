import os
import json
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import networkx as nx

# Load environment variables
load_dotenv()

# Connect to Supabase
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_API_KEY")
supabase = create_client(url, key)

# Retrieve all data with pagination
table_name = "all_bills_uk"
batch_size = 1000
offset = 0
all_rows = []

while True:
    response = supabase.table(table_name).select("*").range(offset, offset + batch_size - 1).execute()
    if not response.data:
        break
    all_rows.extend(response.data)
    offset += batch_size

df_bills = pd.DataFrame(all_rows)
print(f"✅ Loaded {len(df_bills)} bills")

# Basic analysis: Policy Area Rejection Rates
# NOTE: This assumes you have a 'policyArea' and 'outcome' field in your Supabase table
if 'policyArea' in df_bills.columns and 'outcome' in df_bills.columns:
    df_policy = df_bills[['policyArea', 'outcome']].dropna()
    df_policy['is_rejected'] = df_policy['outcome'].str.lower().str.contains('reject')

    summary = (
        df_policy.groupby('policyArea')['is_rejected']
        .agg(['count', 'sum'])
        .rename(columns={'count': 'total_bills', 'sum': 'rejected_bills'})
    )
    summary['rejection_rate'] = summary['rejected_bills'] / summary['total_bills']
    summary = summary.sort_values(by='rejection_rate', ascending=False)

    print("\n📊 Policy Area Rejection Rates:")
    print(summary.head(10))
else:
    print("⚠️ 'policyArea' and/or 'outcome' column missing from dataset")

# Build Knowledge Graph
G = nx.DiGraph()

# Sample subset for clarity
df_sample = df_bills.sample(n=300, random_state=42)
for _, row in df_sample.iterrows():
    bill_node = f"Bill {row['billId']}"
    department_node = row['originatingHouse']
    status_node = row['currentStage_description']

    if pd.isna(department_node) or pd.isna(status_node):
        continue  # skip incomplete rows

    # Add Nodes
    G.add_node(bill_node, type='Bill')
    G.add_node(department_node, type='Department')
    G.add_node(status_node, type='Status')

    # Add Edges
    G.add_edge(bill_node, department_node, relation='handled_by')
    G.add_edge(bill_node, status_node, relation='current_status')

# Export for interactive viewer
def export_graph_to_json(G, path="bills_knowledge_graph.json"):
    data = {
        "nodes": [
            {
                "id": n,
                "label": n,
                "type": G.nodes[n].get("type", ""),
                "color": (
                    "#4F9DFF" if G.nodes[n]["type"] == "Bill"
                    else "#47D16C" if G.nodes[n]["type"] == "Department"
                    else "#FFA500"
                )
            }
            for n in G.nodes
        ],
        "edges": [
            {
                "from": u,
                "to": v,
                "label": G.edges[u, v].get("relation", "")
            }
            for u, v in G.edges
        ]
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Exported styled graph to {path}")

export_graph_to_json(G)

# Optional: also export to GraphML
nx.write_graphml(G, "bills_knowledge_graph.graphml")
print("✅ Graph exported to 'bills_knowledge_graph.graphml'")
