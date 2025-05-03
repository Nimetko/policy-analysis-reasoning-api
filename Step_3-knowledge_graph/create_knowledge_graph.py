import pandas as pd
import networkx as nx

# Load your dataset
csv_path = "bills_with_policy_area_full.csv"
df = pd.read_csv(csv_path)

# Create a directed graph
G = nx.DiGraph()

# Iterate through each row and create nodes and edges
for _, row in df.iterrows():
    bill_id = str(row['billId'])
    bill_title = row.get('shortTitle', f"Bill {bill_id}")
    policy = row.get('policyArea', 'Unknown')
    outcome = (
        'Rejected' if not row.get('isAct', True) else 'Passed'
    )
    stage = row.get('currentStage_description', 'Unknown')
    sponsor = row.get('sponsor', 'Unknown')
    withdrawn = row.get('billWithdrawn', False)
    defeated = row.get('isDefeated', False)

    # Add nodes
    G.add_node(f"bill_{bill_id}", label="Bill", title=bill_title)
    G.add_node(f"policy_{policy}", label="PolicyArea", name=policy)
    G.add_node(f"outcome_{outcome}", label="Outcome", status=outcome)
    G.add_node(f"stage_{stage}", label="Stage", name=stage)
    G.add_node(f"sponsor_{sponsor}", label="Sponsor", name=sponsor)

    # Add edges
    G.add_edge(f"bill_{bill_id}", f"policy_{policy}", relation="HAS_POLICY")
    G.add_edge(f"bill_{bill_id}", f"outcome_{outcome}", relation="HAS_OUTCOME")
    G.add_edge(f"bill_{bill_id}", f"stage_{stage}", relation="WENT_THROUGH_STAGE")
    G.add_edge(f"bill_{bill_id}", f"sponsor_{sponsor}", relation="SPONSORED_BY")

    # Optional: tag as withdrawn/defeated
    if withdrawn:
        G.add_node(f"outcome_Withdrawn", label="Outcome", status="Withdrawn")
        G.add_edge(f"bill_{bill_id}", f"outcome_Withdrawn", relation="HAS_OUTCOME")
    if defeated:
        G.add_node(f"outcome_Defeated", label="Outcome", status="Defeated")
        G.add_edge(f"bill_{bill_id}", f"outcome_Defeated", relation="HAS_OUTCOME")

# Save graph in multiple formats
nx.write_graphml(G, "bills_knowledge_graph.graphml")
nx.readwrite.json_graph.node_link_data(G)
with open("bills_knowledge_graph.json", "w") as f:
    import json
    json.dump(nx.readwrite.json_graph.node_link_data(G), f, indent=2)

print(f"✅ Graph saved with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
