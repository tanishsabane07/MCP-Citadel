from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
from retriever.search import search
from services.gemini_service import analyze_example_with_gemini

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

DB_PATH = "./data/query_logs.db"

def log_query_to_db(data):
    """Insert analysis into the existing table columns."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO query_logs (query, example_id, classification, severity, explanation, remediation, final_severity)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("query"),
        data.get("example_id", ""),  # example identifier
        data.get("classification", ""),
        data.get("severity", 0),
        data.get("explanation", ""),
        data.get("remediation", ""),
        data.get("final_severity", 0.0)
    ))
    conn.commit()
    conn.close()

@app.route("/api/query", methods=["POST"])
def query():
    data = request.json or {}
    user_query = data.get("query", "")
    top_k = int(data.get("top_k", 5))
    results = search(user_query, top_k=top_k)
    return jsonify(results)

@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.json or {}
    user_query = data.get("query", "")
    top_k = int(data.get("top_k", 3))

    if not user_query:
        return jsonify({"error": "query missing"}), 400

    selected = search(user_query, top_k=top_k)
    enriched = []

    for ex in selected:
        llm_res = analyze_example_with_gemini(user_query, ex)

        # Ensure llm_res is a dict
        if not isinstance(llm_res, dict):
            try:
                llm_res = json.loads(llm_res)
            except Exception:
                llm_res = {
                    "summary": "",
                    "classification": "",
                    "severity": 0,
                    "explanation": "",
                    "remediation": ["No structured remediation returned"]
                }

        # Convert remediation list to newline string for frontend
        remediation_points = llm_res.get("remediation", [])
        if isinstance(remediation_points, list):
            llm_res["remediation"] = "\n".join(remediation_points)
        elif isinstance(remediation_points, dict):
            llm_res["remediation"] = "\n".join([f"{k}: {v}" for k, v in remediation_points.items()])
        else:
            llm_res["remediation"] = str(remediation_points)

        # Log to DB
        log_query_to_db({
            "query": user_query,
            "example_id": ex.get("id", ""),  # dataset/example id
            "classification": llm_res.get("classification", ""),
            "severity": llm_res.get("severity", 0),
            "explanation": llm_res.get("explanation", ""),
            "remediation": llm_res.get("remediation", ""),
            "final_severity": llm_res.get("severity", 0)
        })

        enriched.append({
            "dataset": ex,
            "gemini": llm_res
        })

    return jsonify({"enriched": enriched})

@app.route("/api/history", methods=["GET"])
def get_history():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM query_logs ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    history = [dict(row) for row in rows]
    return jsonify({"history": history})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
