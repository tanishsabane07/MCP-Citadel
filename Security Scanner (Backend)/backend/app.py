# # backend/app.py
# import os
# import sqlite3
# import json
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from retriever.search import search
# from services.gemini_service import analyze_example_with_gemini

# app = Flask(__name__)
# CORS(app, resources={r"/api/*": {"origins": "*"}})

# DB_PATH = os.path.join(os.path.dirname(__file__), "data/query_logs.db")

# def init_db():
#     os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS query_logs (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             query TEXT NOT NULL,
#             example_id TEXT,
#             dataset_name TEXT,
#             classification TEXT,
#             severity INTEGER,
#             explanation TEXT,
#             remediation TEXT,
#             final_severity REAL,
#             timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
#         )
#     """)
#     conn.commit()
#     conn.close()

# def log_query_to_db(data):
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
#     cursor.execute("""
#         INSERT INTO query_logs (
#             query, example_id, dataset_name, classification, severity,
#             explanation, remediation, final_severity
#         ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
#     """, (
#         data.get("query"),
#         data.get("example_id"),
#         data.get("dataset_name"),
#         data.get("classification"),
#         data.get("severity"),
#         json.dumps(data.get("explanation")),  # store as string
#         json.dumps(data.get("remediation")),
#         data.get("final_severity")
#     ))
#     conn.commit()
#     conn.close()

# @app.route("/api/analyze", methods=["POST"])
# def analyze():
#     data = request.json or {}
#     user_query = data.get("query", "")
#     top_k = int(data.get("top_k", 3))

#     if not user_query:
#         return jsonify({"error": "query missing"}), 400

#     selected = search(user_query, top_k=top_k)
#     enriched = []

#     for ex in selected:
#         llm_res = analyze_example_with_gemini(user_query, ex)

#         # Debug Gemini output
#         print("DEBUG: Gemini raw output:", llm_res)

#         # Ensure remediation is a list
#         remediation = llm_res.get("remediation")
#         if isinstance(remediation, str):
#             remediation = [line.strip() for line in remediation.split("\n") if line.strip()]
#         elif not isinstance(remediation, list):
#             remediation = ["Investigate and remediate."]
#         llm_res["remediation"] = remediation

#         # Debug dataset fields
#         print("DEBUG: Dataset fields:", ex)

#         # Fix explanation: fallback if Gemini output is empty
#         explanation = llm_res.get("explanation")
#         if not explanation:
#             explanation = ex.get("description") or ex.get("details") or "No explanation available."
#         elif isinstance(explanation, list):
#             explanation = " ".join(str(item) for item in explanation)
#         explanation = explanation.strip()
#         llm_res["explanation"] = explanation

#         dataset_name = ex.get("name") or ex.get("id", "N/A")
#         dataset_description = ex.get("description") or ex.get("details") or "No description available."

#         # Debug final explanation and description
#         print("DEBUG: Final explanation:", explanation)
#         print("DEBUG: Dataset description:", dataset_description)

#         log_query_to_db({
#             "query": user_query,
#             "example_id": ex.get("id", ""),
#             "dataset_name": dataset_name,
#             "classification": llm_res.get("classification", ex.get("tag", "unknown")),
#             "severity": llm_res.get("severity", 0),
#             "explanation": explanation,
#             "remediation": llm_res.get("remediation", []),
#             "final_severity": llm_res.get("severity", 0)
#         })

#         enriched.append({
#             "dataset": {
#                 "name": dataset_name,
#                 "description": dataset_description
#             },
#             "gemini": llm_res
#         })

#     return jsonify({"enriched": enriched})


# @app.route("/api/history", methods=["GET"])
# def get_history():
#     conn = sqlite3.connect(DB_PATH)
#     conn.row_factory = sqlite3.Row
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM query_logs ORDER BY timestamp DESC")
#     rows = cursor.fetchall()
#     conn.close()

#     history = []
#     for row in rows:
#         item = dict(row)
#         # Ensure remediation is parsed as list
#         if isinstance(item.get("remediation"), str):
#             try:
#                 item["remediation"] = json.loads(item["remediation"])
#             except:
#                 item["remediation"] = [item.get("remediation")]
#         history.append(item)

#     return jsonify({"history": history})

# if __name__ == "__main__":
#     init_db()
#     app.run(debug=True, port=5000)

# backend/app.py
# import os
# import sqlite3
# import json
# import logging
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from retriever.search import search  # your existing search function
# from services.gemini_service import analyze_example_with_gemini  # your Gemini function

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# app = Flask(__name__)
# CORS(app, resources={r"/api/*": {"origins": "*"}})

# # Database path inside data folder
# DB_PATH = os.path.join(os.path.dirname(__file__), "data/query_logs.db")

# # Initialize DB if not exists
# def init_db():
#     os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS query_logs (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             query TEXT NOT NULL,
#             example_id TEXT,
#             dataset_name TEXT,
#             classification TEXT,
#             severity INTEGER,
#             explanation TEXT,
#             remediation TEXT,
#             final_severity REAL,
#             timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
#         )
#     """)
#     conn.commit()
#     conn.close()

# # Log query to DB
# def log_query_to_db(data):
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
#     cursor.execute("""
#         INSERT INTO query_logs (
#             query, example_id, dataset_name, classification, severity,
#             explanation, remediation, final_severity
#         ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
#     """, (
#         data.get("query"),
#         data.get("example_id"),
#         data.get("dataset_name"),
#         data.get("classification"),
#         data.get("severity"),
#         data.get("explanation"),
#         json.dumps(data.get("remediation")),
#         data.get("final_severity")
#     ))
#     conn.commit()
#     conn.close()

# @app.route("/api/query", methods=["POST"])
# def query():
#     data = request.json or {}
#     user_query = data.get("query", "")
#     top_k = int(data.get("top_k", 5))
#     results = search(user_query, top_k=top_k)
#     return jsonify(results)

# @app.route("/api/analyze", methods=["POST"])
# def analyze():
#     data = request.json or {}
#     user_query = data.get("query", "")
#     top_k = int(data.get("top_k", 3))

#     if not user_query:
#         return jsonify({"error": "query missing"}), 400

#     selected = search(user_query, top_k=top_k)
#     enriched = []

#     for ex in selected:
#         # Gemini analysis
#         llm_res = analyze_example_with_gemini(user_query, ex)

#         # Ensure dict
#         if not isinstance(llm_res, dict):
#             try:
#                 llm_res = json.loads(llm_res)
#             except Exception:
#                 llm_res = {"explanation": "No explanation", "remediation": ["No remediation"], "classification": ex.get("tag", "N/A"), "severity": 5}

#         # Ensure remediation is a list
#         if isinstance(llm_res.get("remediation"), str):
#             llm_res["remediation"] = [llm_res["remediation"]]

#         # Ensure explanation is string
#         explanation = llm_res.get("explanation")
#         if isinstance(explanation, list):
#             explanation = "\n".join(explanation)
#         elif not explanation:
#             explanation = "No explanation provided"

#         # Ensure dataset description is present
#         description = ex.get("description", "No description provided")

#         # Debug logs
#         logger.info("Dataset: %s, Description: %s, Explanation: %s", ex.get("name", "N/A"), description, explanation)

#         # Log to DB
#         log_query_to_db({
#             "query": user_query,
#             "example_id": ex.get("id", ""),
#             "dataset_name": ex.get("name", ex.get("id", "N/A")),
#             "classification": llm_res.get("classification", ex.get("tag", "N/A")),
#             "severity": llm_res.get("severity", 0),
#             "explanation": explanation,
#             "remediation": llm_res.get("remediation", []),
#             "final_severity": llm_res.get("severity", 0)
#         })

#         enriched.append({
#             "dataset": {
#                 "name": ex.get("name", ex.get("id", "N/A")),
#                 "description": description
#             },
#             "gemini": {
#                 "classification": llm_res.get("classification", "N/A"),
#                 "severity": llm_res.get("severity", 0),
#                 "explanation": explanation,
#                 "remediation": llm_res.get("remediation", [])
#             }
#         })

#     return jsonify({"enriched": enriched})

# @app.route("/api/history", methods=["GET"])
# def get_history():
#     conn = sqlite3.connect(DB_PATH)
#     conn.row_factory = sqlite3.Row
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM query_logs ORDER BY timestamp DESC")
#     rows = cursor.fetchall()
#     conn.close()

#     history = []
#     for row in rows:
#         item = dict(row)
#         # Ensure remediation is list
#         if isinstance(item.get("remediation"), str):
#             try:
#                 item["remediation"] = json.loads(item["remediation"])
#             except:
#                 item["remediation"] = [item.get("remediation")]
#         history.append(item)

#     return jsonify({"history": history})

# if __name__ == "__main__":
#     init_db()
#     app.run(debug=True, port=5000)


# # backend/app.py
# import os
# import sqlite3
# import json
# import logging
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from retriever.search import search
# from services.scoring import analyze_query_with_cvss

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# app = Flask(__name__)
# CORS(app, resources={r"/api/*": {"origins": "*"}})

# DB_PATH = os.path.join(os.path.dirname(__file__), "data/query_logs.db")

# def init_db():
#     os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS query_logs (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             query TEXT NOT NULL,
#             example_id TEXT,
#             dataset_name TEXT,
#             classification TEXT,
#             cvss_score REAL,
#             explanation TEXT,
#             remediation TEXT,
#             timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
#         )
#     """)
#     conn.commit()
#     conn.close()

# def log_query_to_db(data):
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
#     cursor.execute("""
#         INSERT INTO query_logs (
#             query, example_id, dataset_name, classification, cvss_score, explanation, remediation
#         ) VALUES (?, ?, ?, ?, ?, ?, ?)
#     """, (
#         data.get("query"),
#         data.get("example_id"),
#         data.get("dataset_name"),
#         data.get("classification"),
#         float(data.get("cvss_score", 5.0)),
#         data.get("explanation"),
#         json.dumps(data.get("remediation", []))
#     ))
#     conn.commit()
#     conn.close()

# @app.route("/api/query", methods=["POST"])
# def query_api():
#     data = request.json or {}
#     user_query = data.get("query", "")
#     top_k = int(data.get("top_k", 5))
#     results = search(user_query, top_k=top_k)
#     return jsonify(results)

# @app.route("/api/analyze", methods=["POST"])
# def analyze_api():
#     data = request.json or {}
#     user_query = data.get("query", "")
#     top_k = int(data.get("top_k", 3))

#     if not user_query:
#         return jsonify({"error": "query missing"}), 400

#     selected = search(user_query, top_k=top_k)
#     enriched = []

#     for ex in selected:
#         analysis = analyze_query_with_cvss(user_query, ex)

#         # Log to DB
#         # log_query_to_db({
#         #     "query": user_query,
#         #     "example_id": ex.get("id", ""),
#         #     "dataset_name": ex.get("title", ex.get("id", "N/A")),
#         #     "classification": analysis.get("classification"),
#         #     "cvss_score": analysis.get("cvss_score"),
#         #     "explanation": analysis.get("explanation"),
#         #     "remediation": analysis.get("remediation")
#         # })

#         enriched.append({
#             "dataset": {
#                 "name": ex.get("title", ex.get("id", "N/A")),
#                 "description": ex.get("details", "No description provided")
#             },
#             "analysis": analysis
#         })

#     return jsonify({"enriched": enriched})

# @app.route("/api/history", methods=["GET"])
# def get_history():
#     conn = sqlite3.connect(DB_PATH)
#     conn.row_factory = sqlite3.Row
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM query_logs ORDER BY timestamp DESC")
#     rows = cursor.fetchall()
#     conn.close()

#     history = []
#     for row in rows:
#         item = dict(row)
#         if isinstance(item.get("remediation"), str):
#             try:
#                 item["remediation"] = json.loads(item["remediation"])
#             except:
#                 item["remediation"] = [item.get("remediation")]
#         history.append(item)
#     return jsonify({"history": history})

# if __name__ == "__main__":
#     init_db()
#     app.run(debug=True, port=5000)


# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import logging
# from services import gemini_service, scoring
# from services.history_db import init_db
# from services.history_db import log_query
# import sqlite3
# import json
# import os

# DB_PATH = os.path.join(os.path.dirname(__file__), "data/query_logs.db")


# app = Flask(__name__)
# CORS(app)
# logging.basicConfig(level=logging.INFO)

# # @app.route("/analyze", methods=["POST"])
# # def analyze_query():
# #     data = request.get_json()
# #     query = data.get("query", "").strip()
# #     example = data.get("example", {})

# #     if not query:
# #         return jsonify({"error": "Empty query"}), 400

# #     # Step 1: Compute severity via scoring.py
# #     cvss_result = scoring.analyze_query_with_cvss(query, example)
# #     severity_score = cvss_result["cvss_score"]

# #     # Step 2: Get classification/explanation/remediation via Gemini
# #     gemini_result = gemini_service.analyze_example_with_gemini(query, example)

# #     # Step 3: Merge both results
# #     final_output = {
# #         "classification": gemini_result.get("classification", cvss_result["classification"]),
# #         "severity": severity_score,
# #         "explanation": gemini_result.get("explanation", ""),
# #         "remediation": gemini_result.get("remediation", cvss_result["remediation"]),
# #         "debug": cvss_result["debug_details"]
# #     }

    

# #     return jsonify(final_output)

# @app.route("/analyze", methods=["POST"])
# def analyze_query():
#     data = request.get_json()
#     query = data.get("query", "").strip()
#     example = data.get("example", {})

#     if not query:
#         return jsonify({"error": "Empty query"}), 400

#     # Step 1: Compute severity via scoring.py
#     cvss_result = scoring.analyze_query_with_cvss(query, example)
#     severity_score = cvss_result["cvss_score"]

#     # Step 2: Get classification/explanation/remediation via Gemini
#     gemini_result = gemini_service.analyze_example_with_gemini(query, example)

#     # Step 3: Merge both results
#     final_output = {
#         "classification": gemini_result.get("classification", cvss_result["classification"]),
#         "severity": severity_score,
#         "explanation": gemini_result.get("explanation", ""),
#         "remediation": gemini_result.get("remediation", cvss_result.get("remediation", [])),
#         "debug": cvss_result.get("debug_details", {})
#     }

#     # Step 4: Log query 
#     log_query({
#         "query": query,
#         "classification": final_output["classification"],
#         "cvss_score": final_output["severity"],
#         "matched_keywords": cvss_result.get("matched_keywords", []),
#         "top_match": cvss_result.get("top_match", {}),
#         "dataset_name": example.get("title", example.get("id", "")),
#         "explanation": final_output["explanation"],
#         "remediation": final_output["remediation"],
#     })

#     return jsonify(final_output)


# from services.history_db import fetch_history

# @app.route("/history", methods=["GET"])
# def get_history():
#     rows = fetch_history(limit=50)
#     history = []
#     for row in rows:
#         history.append({
#             "id": row[0],
#             "timestamp": row[1],
#             "query": row[2],
#             "classification": row[3],
#             "cvss_score": row[4],
#             "matched_keywords": row[5].split(",") if row[5] else [],
#             "top_match_id": row[6],
#             "top_match_title": row[7],
#             "dataset_name": row[8],
#             "explanation": row[9],
#             "remediation": row[10].split("\n") if row[10] else []
#         })
#     return jsonify({"history": history})



    

# if __name__ == "__main__":
#     init_db()
#     app.run(debug=True, port=5000)
     


from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from services import gemini_service, scoring
from services.history_db import init_db, log_query, fetch_history
import os
import json
from flask import send_file
import csv
import io


app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

DB_PATH = os.path.join(os.path.dirname(__file__), "data/query_logs.db")


# @app.route("/analyze", methods=["POST"])
# def analyze_query():
#     data = request.get_json()
#     query = data.get("query", "").strip()
#     example = data.get("example", {})

#     if not query:
#         return jsonify({"error": "Empty query"}), 400

#     # Step 1: Compute severity via scoring.py
#     cvss_result = scoring.analyze_query_with_cvss(query, example)
#     severity_score = cvss_result["cvss_score"]

#     # Step 2: Get classification/explanation/remediation via Gemini
#     gemini_result = gemini_service.analyze_example_with_gemini(query, example)

#     # Step 3: Merge both results
#     final_output = {
#         "classification": gemini_result.get("classification", cvss_result["classification"]),
#         "severity": severity_score,
#         "explanation": gemini_result.get("explanation", ""),
#         "remediation": gemini_result.get("remediation", cvss_result.get("remediation", [])),
#         "debug": cvss_result.get("debug_details", {})
#     }

#     # Step 4: Log query safely
#     remediation_value = final_output["remediation"]
#     if isinstance(remediation_value, (list, dict)):
#         remediation_value = json.dumps(remediation_value)

#     log_query({
#         "query": query,
#         "classification": final_output["classification"],
#         "cvss_score": final_output["severity"],
#         "explanation": final_output["explanation"],
#         "remediation": remediation_value,
#     })

#     return jsonify(final_output)

@app.route("/analyze", methods=["POST"])
def analyze_query():
    data = request.get_json()
    query = data.get("query", "").strip()
    example = data.get("example", {})

    if not query:
        return jsonify({"error": "Empty query"}), 400

    # Step 1: Compute severity and top matches via CVSS scoring
    cvss_result = scoring.analyze_query_with_cvss(query, example)
    severity_score = cvss_result.get("cvss_score", 0)

    # Step 2: Get Gemini results (classification, explanation, remediation)
    gemini_result = gemini_service.analyze_example_with_gemini(query, example)

    # Step 3: Prepare final output
    final_output = {
        "classification": gemini_result.get("classification", cvss_result.get("classification")),
        "severity": severity_score,
        "explanation": gemini_result.get("explanation", ""),
        "remediation": gemini_result.get("remediation", cvss_result.get("remediation", [])),
        "debug": cvss_result.get("debug_details", {}),
        "datasets": []  # will be filled below
    }

    # Step 4: Add top 3–5 datasets from CVSS debug_details
    top_matches = cvss_result.get("debug_details", {}).get("top_matches", [])
    for match in top_matches[:5]:
        final_output["datasets"].append({
            "id": match.get("id"),
            "title": match.get("title"),
            "description": match.get("description") or match.get("details", "")[:200]
        })

    # Step 5: Log query safely
    remediation_value = final_output["remediation"]
    if isinstance(remediation_value, (list, dict)):
        remediation_value = json.dumps(remediation_value)

    log_query({
        "query": query,
        "classification": final_output["classification"],
        "cvss_score": final_output["severity"],
        "explanation": final_output["explanation"],
        "remediation": remediation_value,
    })

    return jsonify(final_output)



@app.route("/history", methods=["GET"])
def get_history():
    rows = fetch_history(limit=50)
    history = []
    for row in rows:
        try:
            remediation_value = json.loads(row[5]) if row[5] else []
        except json.JSONDecodeError:
            remediation_value = row[5].split("|") if row[5] else []

        history.append({
            "id": row[0],
            "timestamp": row[1],
            "query": row[2],
            "classification": row[3],
            "cvss_score": row[4],
            "explanation": row[5],
            "remediation": remediation_value,
        })

    return jsonify({"history": history})

@app.route("/export_history", methods=["GET"])
def export_history():
    """Export all history as CSV."""
    rows = fetch_history(limit=1000)  # or remove limit if you want all
    output = io.StringIO()
    writer = csv.writer(output)

    # CSV header
    writer.writerow([
        "ID", "Timestamp", "Query", "Classification", "CVSS Score",
        "Explanation", "Remediation"
    ])

    # Data rows
    for row in rows:
        writer.writerow(row)

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode("utf-8")),
        mimetype="text/csv",
        as_attachment=True,
        download_name="query_history.csv"
    )



if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
