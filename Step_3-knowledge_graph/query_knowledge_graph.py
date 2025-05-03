import networkx as nx
import json
import argparse
from collections import Counter

# Load the graph
with open("bills_knowledge_graph.json") as f:
    data = json.load(f)
    G = nx.node_link_graph(data, edges="links")  # Explicitly define 'links' to suppress warning

def summarize_policy_areas():
    bill_nodes = [(node, attrs) for node, attrs in G.nodes(data=True) if attrs.get("label") == "Bill"]
    print(f"\n📦 Found {len(bill_nodes)} bill nodes")

    if not bill_nodes:
        print("⚠️ No bill nodes found. Check if 'label' attribute is present.")
        print("🔍 First few nodes in graph for inspection:")
        for i, (node, attrs) in enumerate(G.nodes(data=True)):
            print(f"{node}: {attrs}")
            if i >= 5:
                break
        return

    counter = Counter()
    for _, attrs in bill_nodes:
        for nbr in G.neighbors(_):
            nbr_attrs = G.nodes[nbr]
            if nbr_attrs.get("label") == "PolicyArea":
                counter[nbr_attrs.get("name", "<Unknown>")] += 1

    print("\n📊 Bills per Policy Area:\n")
    for area, count in counter.most_common():
        print(f"{area:<20} {count}")

def rejected_bills_by_policy():
    rejected = {}
    for node, attrs in G.nodes(data=True):
        if attrs.get("label") == "Bill":
            for nbr in G.neighbors(node):
                nbr_attrs = G.nodes[nbr]
                if nbr_attrs.get("label") == "Outcome" and nbr_attrs.get("status") in ["Rejected", "Withdrawn"]:
                    title = attrs.get("title", node)
                    policy_area = "<Unknown>"
                    for second_nbr in G.neighbors(node):
                        second_attrs = G.nodes[second_nbr]
                        if second_attrs.get("label") == "PolicyArea":
                            policy_area = second_attrs.get("name", policy_area)
                            break
                    rejected.setdefault(policy_area, []).append(title)
                    break

    print("\n❌ Rejected Bills per Policy Area:")
    for area, bills in sorted(rejected.items(), key=lambda x: -len(x[1])):
        print(f"\n{area} ({len(bills)} rejected):")
        for title in bills[:5]:  # print only top 5 per area
            print(f"  - {title}")
        if len(bills) > 5:
            print("  ...")

def trace_bill(bill_id):
    if not G.has_node(bill_id):
        print(f"❌ Bill ID {bill_id} not found in graph")
        return
    attrs = G.nodes[bill_id]
    print(f"\n🔎 Bill {bill_id} - {attrs.get('title', 'No title')}")

    for nbr in G.neighbors(bill_id):
        nbr_attrs = G.nodes[nbr]
        if nbr_attrs.get("label") == "PolicyArea":
            print(f"  Policy Area: {nbr_attrs.get('name')}")
        elif nbr_attrs.get("label") == "Outcome":
            print(f"  Outcome: {nbr_attrs.get('status')}")
        elif nbr_attrs.get("label") == "Stage":
            print(f"  Last Stage: {nbr_attrs.get('name')}")

    print("\n🔗 Connections:")
    for neighbor in G.neighbors(bill_id):
        edge_data = G.get_edge_data(bill_id, neighbor)
        neighbor_data = G.nodes[neighbor]
        label = neighbor_data.get("label", "?")
        print(f"  - {label}: {neighbor}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", action="store_true", help="Show summary of bills per policy area")
    parser.add_argument("--rejected", action="store_true", help="Show rejected bills per policy area")
    parser.add_argument("--trace", type=str, help="Trace connections of a specific bill by ID")

    args = parser.parse_args()

    if args.summary:
        summarize_policy_areas()
    if args.rejected:
        rejected_bills_by_policy()
    if args.trace:
        trace_bill(args.trace)

    if not any([args.summary, args.rejected, args.trace]):
        parser.print_help()
