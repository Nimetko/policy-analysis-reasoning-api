from flask import Flask, request, jsonify
from dynamically_build_kg_example import (
    fetch_bill_data,
    build_kg,
    prepare_prompt_from_graph,
    generate_summary,
    save_graph,
    ask_gpt
)

app = Flask(__name__)

@app.route("/analyze", methods=["GET"])
def analyze():
    policy_area = request.args.get("policy", default="Education")
    question = request.args.get("question", default="Why do education bills often get delayed?")

    raw_data = fetch_bill_data(policy_area=policy_area)
    graph = build_kg(raw_data)
    facts_text = prepare_prompt_from_graph(graph)
    summary_text = generate_summary(raw_data)
    save_graph(graph, "knowledge_graph.ttl")
    answer = ask_gpt(facts_text, summary_text, question)

    return jsonify({
        "policyArea": policy_area,
        "question": question,
        "summary": summary_text,
        "answer": answer
    })

if __name__ == "__main__":
    app.run(port=5001, debug=True)

