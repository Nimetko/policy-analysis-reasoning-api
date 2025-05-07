from flask import Flask, request, jsonify
from supabase import create_client
from rdflib import Graph, URIRef, Literal, Namespace
from openai import OpenAI
from dotenv import load_dotenv
import os, json, re
from collections import Counter

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)
sb = create_client(SUPABASE_URL, SUPABASE_KEY)

VALID_POLICY_AREAS = [
    "Defense", "Economy", "Education", "Environment", "Health",
    "Housing", "Justice", "Other", "Social Care", "Transport"
]

app = Flask(__name__)

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
    return g

def prepare_prompt_from_graph(g):
    facts = [f"{s.split('/')[-1]} → {p.split('/')[-1]} → {o.split('/')[-1] if isinstance(o, URIRef) else o}" for s, p, o in g]
    return "\n".join(facts)

def generate_summary(data):
    total = len(data)
    defeated = sum(1 for b in data if b.get("isDefeated"))
    withdrawn = sum(1 for b in data if b.get("billWithdrawn"))
    acts = sum(1 for b in data if b.get("isAct"))
    stage_counts = Counter(b["currentStage_description"] for b in data if b.get("currentStage_description"))
    stage_summary = "\n".join([f"{stage}: {count}" for stage, count in stage_counts.items()])
    return f"Total bills: {total}\nDefeated: {defeated}\nWithdrawn: {withdrawn}\nActs passed: {acts}\n\nStage distribution:\n{stage_summary}"

def ask_gpt(facts, summary, question):
    prompt = f"""
    You are an AI policy analyst. Here is a knowledge graph and summary:

    Summary:
    {summary}

    Graph facts:
    {facts}

    Based on the data, answer:
    {question}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800
    )
    return response.choices[0].message.content.strip()

def infer_policy_and_question(query):
    semantic_prompt = f"""Extract a valid policy_area and question from the query.
    Policy areas: {', '.join(VALID_POLICY_AREAS)}.
    Response as JSON: {{"policy_area": "...", "question": "..."}}

    Query: {query}"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": semantic_prompt}],
        max_tokens=150
    )
    raw_response = response.choices[0].message.content.strip()
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_response, flags=re.MULTILINE).strip()
    parsed = json.loads(cleaned)
    policy_area = parsed.get("policy_area", "Education")
    question = parsed.get("question", query)
    return policy_area, question

@app.route('/analyze', methods=['GET'])
def analyze():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Query parameter is required."}), 400

    policy_area, question = infer_policy_and_question(query)
    data = fetch_bill_data(policy_area)
    graph = build_kg(data)
    facts = prepare_prompt_from_graph(graph)
    summary = generate_summary(data)
    answer = ask_gpt(facts, summary, question)

    return jsonify({"policy_area": policy_area, "question": question, "answer": answer})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
