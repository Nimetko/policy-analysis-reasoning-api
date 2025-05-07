from supabase import create_client, Client
from rdflib import Graph, URIRef, Literal, Namespace
from openai import OpenAI
import os
from dotenv import load_dotenv
from collections import Counter

# --- Load environment variables ---
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- Initialize clients ---
client = OpenAI(api_key=OPENAI_API_KEY)
sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Step 1: Fetch Data from Supabase ---
def fetch_bill_data(policy_area="Education"):
    print("[INFO] Fetching data from Supabase...")
    response = sb.table("all_bills_uk")\
        .select("*")\
        .eq("policyArea", policy_area)\
        .gte("lastUpdate", "2022-01-01")\
        .execute()
    print(f"[INFO] Retrieved {len(response.data)} records.")
    return response.data

# --- Step 2: Build In-Memory Knowledge Graph ---
def build_kg(data):
    print("[INFO] Building in-memory knowledge graph...")
    g = Graph()
    ns = Namespace("http://example.org/legislation/")

    for bill in data:
        bill_uri = URIRef(ns[f"Bill{bill['billId']}"])

        # Link to shared nodes (not literals)
        status_uri = URIRef(ns[bill["currentStage_description"].replace(" ", "_")])
        area_uri = URIRef(ns[bill["policyArea"].replace(" ", "_")])

        g.add((bill_uri, ns["hasStatus"], status_uri))
        g.add((bill_uri, ns["belongsTo"], area_uri))

        if bill.get("isDefeated"):
            g.add((bill_uri, ns["isDefeated"], Literal(bill["isDefeated"])))
        if bill.get("isAct"):
            g.add((bill_uri, ns["isAct"], Literal(bill["isAct"])))
        if bill.get("billWithdrawn"):
            g.add((bill_uri, ns["billWithdrawn"], Literal(bill["billWithdrawn"])))
        if bill.get("currentHouse"):
            house_uri = URIRef(ns[bill["currentHouse"].replace(" ", "_")])
            g.add((bill_uri, ns["currentHouse"], house_uri))
        if bill.get("originatingHouse"):
            origin_uri = URIRef(ns[bill["originatingHouse"].replace(" ", "_")])
            g.add((bill_uri, ns["originatingHouse"], origin_uri))

    print(f"[INFO] Knowledge graph has {len(g)} triples.")
    return g

# --- Step 3: Prepare Prompt for GPT ---
def prepare_prompt_from_graph(g: Graph):
    print("[INFO] Preparing graph facts for GPT prompt...")
    facts = []
    for s, p, o in g:
        facts.append(f"{s.split('/')[-1]} → {p.split('/')[-1]} → {o.split('/')[-1] if isinstance(o, URIRef) else o}")
    return "\n".join(facts)

# --- Step 3.5: Generate Data Summary ---
def generate_summary(data):
    print("[INFO] Generating summary statistics...")
    total = len(data)
    defeated = sum(1 for b in data if b.get("isDefeated") == True)
    withdrawn = sum(1 for b in data if b.get("billWithdrawn"))
    acts = sum(1 for b in data if b.get("isAct") == True)
    stage_counts = Counter(b["currentStage_description"] for b in data if b.get("currentStage_description"))
    stage_summary = "\n".join([f"{stage}: {count}" for stage, count in stage_counts.items()])
    return f"""Total bills: {total}
Defeated: {defeated}
Withdrawn: {withdrawn}
Acts passed: {acts}

Stage distribution:
{stage_summary}"""

# --- Step 4: Ask GPT for Reasoning ---
def ask_gpt(facts, summary, question):
    print("[INFO] Sending prompt to GPT...")
    prompt = f"""
You are an AI policy analyst. Here is a knowledge graph and a summary of education bills:

Summary:
{summary}

Graph facts:
{facts}

Based on the data, explain the most likely causes of delay or failure for education bills.
"""
    print(f"[DEBUG] GPT prompt length: {len(prompt)} characters")
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800
    )
    return response.choices[0].message.content.strip()

# --- Step 5: Save Graph to File ---
def save_graph(graph: Graph, filepath="knowledge_graph.ttl"):
    print(f"[INFO] Saving knowledge graph to {filepath}...")
    graph.serialize(destination=filepath, format="turtle")
    with open(filepath, 'r') as f:
        content = f.read()
        print(f"[DEBUG] TTL file length: {len(content)} characters")

# --- Run the Flow ---
if __name__ == "__main__":
    question = "Why do education bills often get delayed?"
    raw_data = fetch_bill_data(policy_area="Education")
    graph = build_kg(raw_data)
    facts_text = prepare_prompt_from_graph(graph)
    summary_text = generate_summary(raw_data)
    save_graph(graph, "knowledge_graph.ttl")
    answer = ask_gpt(facts_text, summary_text, question)
    print("\n🤔 GPT Answer:\n", answer)
