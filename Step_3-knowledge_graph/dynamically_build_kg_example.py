from flask import Flask, request, jsonify
from supabase import create_client, Client
from rdflib import Graph, URIRef, Literal, Namespace
from openai import OpenAI
import os
from dotenv import load_dotenv
from collections import Counter
import json
import re
import sys
from flask_cors import CORS

# --- Load environment variables ---
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- Initialize clients ---
client = OpenAI(api_key=OPENAI_API_KEY)
sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

VALID_POLICY_AREAS = [
    "Defense", "Economy", "Education", "Environment", "Health",
    "Housing", "Justice", "Other", "Social Care", "Transport"
]

def fetch_bill_data(policy_area="Education"):
    response = sb.table("all_bills_uk")\
        .select("*")\
        .eq("policyArea", policy_area)\
        .gte("lastUpdate", "2022-01-01")\
        .execute()
    return response.data

def build_kg(data):
    g = Graph()
    ns = Namespace("http://example.org/legislation/")
    for bill in data:
        bill_uri = URIRef(ns[f"Bill{bill['billId']}"])
        status_uri = URIRef(ns[bill["currentStage_description"].replace(" ", "_")])
        area_uri = URIRef(ns[bill["policyArea"].replace(" ", "_")])
        g.add((bill_uri, ns["hasStatus"], status_uri))
        g.add((bill_uri, ns["belongsTo"], area_uri))
        if bill.get("isAct") is True:
            g.add((bill_uri, ns["isApproved"], Literal(True)))
        elif bill.get("isAct") is False:
            g.add((bill_uri, ns["isRejected"], Literal(True)))
        if bill.get("currentHouse"):
            house_uri = URIRef(ns[bill["currentHouse"].replace(" ", "_")])
            g.add((bill_uri, ns["currentHouse"], house_uri))
        if bill.get("originatingHouse"):
            origin_uri = URIRef(ns[bill["originatingHouse"].replace(" ", "_")])
            g.add((bill_uri, ns["originatingHouse"], origin_uri))
    return g

def prepare_prompt_from_graph(g: Graph):
    facts = [f"{s.split('/')[-1]} → {p.split('/')[-1]} → {o.split('/')[-1] if isinstance(o, URIRef) else o}" for s, p, o in g]
    return "\n".join(facts)

def generate_summary(data):
    total = len(data)
    defeated = sum(1 for b in data if b.get("isDefeated"))
    withdrawn = sum(1 for b in data if b.get("billWithdrawn"))
    acts = sum(1 for b in data if b.get("isAct"))
    stage_counts = Counter(b["currentStage_description"] for b in data if b.get("currentStage_description"))
    stage_summary = "\n".join([f"{stage}: {count}" for stage, count in stage_counts.items()])
    return f"""Total bills: {total}
Defeated: {defeated}
Withdrawn: {withdrawn}
Acts passed: {acts}

Stage distribution:
{stage_summary}"""

def ask_gpt(facts, summary, question):
    prompt = f"""
You are an AI policy analyst. Here is a knowledge graph and a summary:

Summary:
{summary}

Graph facts:
{facts}

Question:
{question}
"""
    response = client.chat.completions.create(
        # model="gpt-4o-mini",
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800
    )
    return response.choices[0].message.content.strip()

def infer_policy_area_and_question(user_input):
    semantic_prompt = f"""
Extract a valid policy area from this list: {", ".join(VALID_POLICY_AREAS)}

Respond in JSON format:
{{
  "policy_area": "...", 
  "question": "..."
}}

User query:
"{user_input}"
"""
    semantic_result = client.chat.completions.create(
        model="gpt-4o",
        # model="gpt-4o-mini",
        messages=[{"role": "user", "content": semantic_prompt}],
        max_tokens=150
    )
    raw_response = semantic_result.choices[0].message.content.strip()
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_response, flags=re.MULTILINE).strip()
    parsed = json.loads(cleaned)
    policy_area = parsed.get("policy_area", "Other").strip()
    question = parsed.get("question", user_input)
    return policy_area, question

app = Flask(__name__)
CORS(app, resources={r"/analyze": {"origins": "*"}})

@app.route('/analyze', methods=['GET'])
def analyze():
    user_input = request.args.get('query')
    if not user_input:
        return jsonify({"error": "query parameter required"}), 400

    policy_area, refined_question = infer_policy_area_and_question(user_input)
    data = fetch_bill_data(policy_area)
    graph = build_kg(data)
    facts_text = prepare_prompt_from_graph(graph)
    summary_text = generate_summary(data)
    answer = ask_gpt(facts_text, summary_text, refined_question)

    return jsonify({"policy_area": policy_area, "question": refined_question, "answer": answer})

if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_input = sys.argv[1]
        print(f"[DEBUG] Received CLI input: {user_input}")

        policy_area, refined_question = infer_policy_area_and_question(user_input)
        print(f"[DEBUG] Policy Area: {policy_area}, Question: {refined_question}")

        data = fetch_bill_data(policy_area)
        print(f"[DEBUG] Data fetched: {len(data)} records")

        graph = build_kg(data)
        print(f"[DEBUG] Knowledge graph built with {len(graph)} triples")

        facts_text = prepare_prompt_from_graph(graph)
        summary_text = generate_summary(data)
        answer = ask_gpt(facts_text, summary_text, refined_question)
        print("\n🤔 GPT Answer:\n", answer)
    else:
        print("[INFO] Starting Flask server...")
        app.run(debug=True, host='0.0.0.0', port=5050)

