from supabase import create_client, Client
from rdflib import Graph, URIRef, Literal, Namespace
from openai import OpenAI
import os
from dotenv import load_dotenv

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
    response = sb.table("all_bills_uk").select("*").eq("policyArea", policy_area).execute()
    return response.data

# --- Step 2: Build In-Memory Knowledge Graph ---
def build_kg(data):
    g = Graph()
    ns = Namespace("http://example.org/legislation/")

    for bill in data:
        bill_id = URIRef(ns[bill["billId"]])
        g.add((bill_id, ns["hasStatus"], Literal(bill["currentStage_description"])))
        g.add((bill_id, ns["belongsTo"], Literal(bill["policyArea"])))
        if bill.get("isDefeated"):
            g.add((bill_id, ns["isDefeated"], Literal(bill["isDefeated"])))
        if bill.get("isAct"):
            g.add((bill_id, ns["isAct"], Literal(bill["isAct"])))
        if bill.get("billWithdrawn"):
            g.add((bill_id, ns["billWithdrawn"], Literal(bill["billWithdrawn"])))
        if bill.get("currentHouse"):
            g.add((bill_id, ns["currentHouse"], Literal(bill["currentHouse"])))
        if bill.get("originatingHouse"):
            g.add((bill_id, ns["originatingHouse"], Literal(bill["originatingHouse"])))
    return g

# --- Step 3: Prepare Prompt for GPT ---
def prepare_prompt_from_graph(g: Graph):
    facts = []
    for s, p, o in g:
        facts.append(f"{s.split('/')[-1]} → {p.split('/')[-1]} → {o}")
    return "\n".join(facts)

# --- Step 3.5: Generate Data Summary ---
def generate_summary(data):
    total = len(data)
    defeated = sum(1 for b in data if b.get("isDefeated") == True)
    withdrawn = sum(1 for b in data if b.get("billWithdrawn"))
    acts = sum(1 for b in data if b.get("isAct") == True)
    return f"Total bills: {total}\nDefeated: {defeated}\nWithdrawn: {withdrawn}\nActs passed: {acts}"

# --- Step 4: Ask GPT for Reasoning ---
def ask_gpt(facts, summary, question):
    prompt = f"""
You are an AI policy analyst. Here is a knowledge graph and a summary of education bills:

Summary:
{summary}

Graph facts:
{facts}

Based on the data, explain the most likely causes of delay or failure for education bills.
"""

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )
    return response.choices[0].message.content.strip()

# --- Run the Flow ---
if __name__ == "__main__":
    question = "Why do education bills often get delayed?"
    raw_data = fetch_bill_data(policy_area="Education")
    graph = build_kg(raw_data)
    facts_text = prepare_prompt_from_graph(graph)
    summary_text = generate_summary(raw_data)
    answer = ask_gpt(facts_text, summary_text, question)
    print("\n🤔 GPT Answer:\n", answer)
