# # # # services/scoring.py
# # # import logging
# # # from services.gemini_service import analyze_example_with_gemini
# # # from services.cvss_calculator import calculate_cvss

# # # logger = logging.getLogger(__name__)

# # # def analyze_query_with_cvss(user_query: str, example: dict) -> dict:
# # #     """
# # #     Analyze user query dynamically using Gemini, then calculate CVSS.
# # #     Returns dict: {classification, cvss_score, explanation, remediation}
# # #     """
# # #     llm_res = analyze_example_with_gemini(user_query, example)

# # #     # Map LLM severity 0-10 to CVSS metrics dynamically
# # #     # Scale: 0 => low impact, 10 => high impact
# # #     sev = float(llm_res.get("severity", 5))

# # #     # Dynamic CVSS base metrics from severity
# # #     # AV=N (network) for high severity, AC=L for easy attacks
# # #     metrics = {
# # #         "AV": "N" if sev >= 7 else "A",
# # #         "AC": "L" if sev >= 7 else "H",
# # #         "PR": "N" if sev >= 7 else "L",
# # #         "UI": "N" if sev >= 7 else "R",
# # #         "S": "U",
# # #         "C": "H" if sev >= 7 else "L",
# # #         "I": "H" if sev >= 7 else "L",
# # #         "A": "H" if sev >= 7 else "L"
# # #     }

# # #     cvss = calculate_cvss(metrics)

# # #     return {
# # #         "classification": llm_res.get("classification", example.get("tag", "unknown")),
# # #         "cvss_score": cvss["base_score"],
# # #         "explanation": llm_res.get("explanation", ""),
# # #         "remediation": llm_res.get("remediation", [])
# # #     }


# # # backend/services/scoring.py
# # """
# # Dynamic severity / CVSS-like scoring for user queries.

# # This module implements:
# # - calculate_severity(query): computes a 0-10 severity score from the free-text query.
# # - analyze_query_with_cvss(user_query, example): (keeps existing name/signature)
# #     used by backend.app.analyze_api — returns a dict with:
# #     - classification
# #     - cvss_score (0-10 float)
# #     - explanation (string / multi-point)
# #     - remediation (list of actionable steps)

# # Design choices:
# # - Keeps the function name analyze_query_with_cvss(...) intact so it plugs into your app.py.
# # - Uses a hybrid approach:
# #     * fast heuristic / keyword scoring (explainable)
# #     * lightweight TF-IDF similarity against the attackbench dataset (captures semantically
# #       risky queries that lack explicit keywords)
# # - Loads the dataset directly from ../data/attackbench.json to avoid circular imports.
# # - Caches vectorizer and TF-IDF matrix at module level for performance.
# # """

# # import os
# # import json
# # import math
# # from typing import List, Dict, Tuple

# # from sklearn.feature_extraction.text import TfidfVectorizer
# # from sklearn.metrics.pairwise import cosine_similarity

# # # Module-level cache
# # _DATASET_PATH = os.path.join(os.path.dirname(__file__), "../data/attackbench.json")
# # _dataset = None
# # _vectorizer = None
# # _tfidf_matrix = None
# # _texts = None


# # # -------------------------
# # # Helpers: load dataset + TF-IDF
# # # -------------------------
# # def _load_dataset():
# #     global _dataset, _texts
# #     if _dataset is None:
# #         with open(_DATASET_PATH, "r", encoding="utf-8") as f:
# #             _dataset = json.load(f)
# #         # ensure text field
# #         for item in _dataset:
# #             title = item.get("title", "")
# #             details = item.get("details", "")
# #             item["_combined_text"] = f"{title} {details}"
# #         _texts = [item["_combined_text"] for item in _dataset]
# #     return _dataset


# # def _ensure_vectorizer():
# #     """
# #     Build and cache a TF-IDF vectorizer and matrix on the attackbench dataset.
# #     This is intentionally lightweight and only used as an enhancement (not the single source
# #     of truth) so the system still behaves even if TF-IDF is noisy.
# #     """
# #     global _vectorizer, _tfidf_matrix, _texts
# #     if _vectorizer is None or _tfidf_matrix is None:
# #         _load_dataset()
# #         _vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
# #         _tfidf_matrix = _vectorizer.fit_transform(_texts)
# #     return _vectorizer, _tfidf_matrix


# # # -------------------------
# # # Heuristics configuration
# # # -------------------------
# # # Keywords mapped to severity contribution (0-10 scale before normalization)
# # _CRITICAL_ACTIONS = {
# #     # action : weight
# #     "delete": 3.0,
# #     "drop": 3.0,
# #     "execute": 3.0,
# #     "rce": 4.0,
# #     "remote code execution": 4.0,
# #     "bypass": 3.5,
# #     "exploit": 3.5,
# #     "upload": 2.5,
# #     "overwrite": 2.5,
# #     "privilege escalation": 4.0,
# #     "escalate": 3.0,
# #     "bypass authentication": 4.0,
# #     "gain access": 3.5
# # }

# # _SENSITIVE_TARGETS = {
# #     "admin": 3.0,
# #     "root": 4.0,
# #     "database": 3.5,
# #     "db": 3.0,
# #     "server": 3.0,
# #     "config": 2.5,
# #     "credentials": 3.5,
# #     "api key": 3.5,
# #     "secret": 3.5,
# #     "token": 3.0,
# #     "ssh": 3.5,
# # }

# # _EXPOSURE_TERMS = {
# #     "public": 1.5,
# #     "internet": 1.5,
# #     "remote": 1.5,
# #     "exposed": 1.5,
# #     "open": 1.0,
# #     "unauthenticated": 2.0,
# #     "anonymous": 1.5,
# # }

# # # fallback base score when some security intent is detected but weak:
# # _BASE_INTENT_SCORE = 1.5

# # # similarity mapping: similarity (0..1) -> score contribution (0..4)
# # _SIMILARITY_MAX = 4.0


# # # -------------------------
# # # Core: calculate_severity
# # # -------------------------
# # def calculate_severity(query: str, use_similarity: bool = True) -> Tuple[float, Dict]:
# #     """
# #     Calculate a CVSS-like 0-10 severity score from a free-text query.

# #     Returns:
# #       (score, details) where details is a dict describing factor contributions:
# #         {
# #           "heuristic_score": float,
# #           "similarity_score": float,
# #           "final_score": float,
# #           "matched_keywords": [...],
# #           "top_similarity_matches": [ (id, title, sim_score), ... ]
# #         }

# #     Behavior:
# #       - If the query contains no security intent (no keywords AND low similarity),
# #         returns a very low score (~0.0).
# #       - Otherwise, combines heuristic score (keyword + target + exposure) with an
# #         embedding/similarity-derived score to capture semantic matches.
# #     """
# #     if not query or not query.strip():
# #         return 0.0, {"reason": "empty query"}

# #     q = query.lower()

# #     # Quick intent check: look for any security-ish words (broad set)
# #     security_vocab = set(list(_CRITICAL_ACTIONS.keys()) + list(_SENSITIVE_TARGETS.keys()) + list(_EXPOSURE_TERMS.keys()) +
# #                          ["sql", "xss", "ssrf", "csrf", "vulnerab", "exploit", "attack", "bypass", "shell", "exec", "payload"])
# #     found_vocab = [w for w in security_vocab if w in q]

# #     # Build heuristic score from keywords
# #     matched_keywords = []
# #     heuristic_score = 0.0

# #     # actions
# #     for kw, w in _CRITICAL_ACTIONS.items():
# #         if kw in q:
# #             heuristic_score += w
# #             matched_keywords.append(kw)

# #     # targets
# #     for kw, w in _SENSITIVE_TARGETS.items():
# #         if kw in q:
# #             heuristic_score += w
# #             matched_keywords.append(kw)

# #     # exposure
# #     for kw, w in _EXPOSURE_TERMS.items():
# #         if kw in q:
# #             heuristic_score += w
# #             matched_keywords.append(kw)

# #     # small heuristics: presence of pattern words (e.g., "how to", "tutorial", "exploit code")
# #     if "how to" in q or "tutorial" in q or "exploit code" in q or "proof of concept" in q:
# #         heuristic_score += 1.0
# #         matched_keywords.append("how-to/tutorial")

# #     # If nothing matched at all, check similarity to known vulnerabilities as fallback
# #     similarity_score = 0.0
# #     top_matches = []

# #     if use_similarity:
# #         try:
# #             vectorizer, tfidf_matrix = _ensure_vectorizer()
# #             q_vec = vectorizer.transform([query])
# #             sims = cosine_similarity(q_vec, tfidf_matrix).flatten()
# #             # get best similarity
# #             best_idx = int(sims.argmax())
# #             best_sim = float(sims[best_idx])
# #             # map similarity (0..1) to a contribution (0.._SIMILARITY_MAX)
# #             similarity_score = min(_SIMILARITY_MAX, best_sim * _SIMILARITY_MAX * 1.2)  # scale up a bit
# #             # top 3 matches for explainability
# #             _load_dataset()
# #             top_n = sims.argsort()[::-1][:3]
# #             # safe guard - ensure dataset loaded
# #             for idx in top_n:
# #                 top_matches.append((_dataset[idx].get("id"), _dataset[idx].get("title"), float(sims[idx])))
# #         except Exception:
# #             # If TF-IDF fails for any reason, keep similarity_score = 0
# #             similarity_score = 0.0
# #             top_matches = []

# #     # If neither heuristic nor similarity found anything, return very low score
# #     if heuristic_score <= 0 and (similarity_score <= 0 or not found_vocab):
# #         return 0.0, {
# #             "heuristic_score": 0.0,
# #             "similarity_score": similarity_score,
# #             "final_score": 0.0,
# #             "matched_keywords": matched_keywords,
# #             "top_similarity_matches": top_matches,
# #             "reason": "No security intent detected"
# #         }

# #     # Normalize heuristic: heur_score might be in a wide range; scale to 0..(10 - _SIMILARITY_MAX)
# #     # We'll allocate up to (10 - _SIMILARITY_MAX) e.g., 6.0 points for heuristics and up to _SIMILARITY_MAX for similarity.
# #     HEURISTIC_MAX_ALLOCATION = 10.0 - _SIMILARITY_MAX  # e.g., 6.0

# #     # Estimate a possible maximum raw heuristic value to normalize. We choose a conservative cap:
# #     RAW_HEURISTIC_CAP = 12.0  # if sum of weights exceeds this, we clamp before scaling
# #     heur_clamped = min(heuristic_score, RAW_HEURISTIC_CAP)
# #     heur_norm = (heur_clamped / RAW_HEURISTIC_CAP) * HEURISTIC_MAX_ALLOCATION

# #     final_score = heur_norm + similarity_score
# #     # small floor due to base intent
# #     final_score = max(final_score, _BASE_INTENT_SCORE if matched_keywords or found_vocab else 0.0)

# #     # clamp to 0..10
# #     final_score = max(0.0, min(10.0, final_score))

# #     details = {
# #         "heuristic_score_raw": heuristic_score,
# #         "heuristic_score_normalized": round(heur_norm, 3),
# #         "similarity_score": round(similarity_score, 3),
# #         "final_score": round(final_score, 3),
# #         "matched_keywords": matched_keywords,
# #         "top_similarity_matches": top_matches
# #     }
# #     return final_score, details


# # # -------------------------
# # # Remediation templates
# # # -------------------------
# # _REMEDIATION_TEMPLATES = {
# #     "sql-injection": [
# #         "Use parameterized queries / prepared statements for all database access.",
# #         "Validate and sanitize all user inputs before including them in queries.",
# #         "Apply least privilege to DB accounts used by the application.",
# #         "Enable query logging and monitor for anomalous queries."
# #     ],
# #     "xss": [
# #         "Escape and encode all user-supplied content before rendering in HTML.",
# #         "Apply a strict Content-Security-Policy (CSP) restricting scripts and sources.",
# #         "Use secure templating engines that auto-escape output.",
# #         "Validate and sanitize any HTML or markdown inputs."
# #     ],
# #     "command-injection": [
# #         "Avoid shelling out with user-controlled input. Use safe libraries/APIs.",
# #         "If shelling out is required, use argument arrays and proper escaping.",
# #         "Run processing in a sandbox or isolated process with minimal privileges.",
# #         "Validate filenames and restrict upload directories."
# #     ],
# #     "insecure-deserialization": [
# #         "Avoid deserializing untrusted data. Use safe formats (JSON) with strict schema validation.",
# #         "Implement integrity checks and signatures for serialized payloads.",
# #         "Run deserialization in a restricted context or sandbox.",
# #         "Monitor and restrict inputs to deserialization endpoints."
# #     ],
# #     "ssrf": [
# #         "Whitelist remote hosts / domains for server-side fetches.",
# #         "Block metadata and internal IP ranges (169.254.169.254, 127.0.0.1, 10/8, 192.168/16).",
# #         "Validate and sanitize URLs before fetching.",
# #         "Apply network egress controls and timeouts."
# #     ],
# #     "default-creds": [
# #         "Enforce unique, strong passwords for all default accounts and rotate them.",
# #         "Disable unused default accounts and restrict admin access to a limited IP range.",
# #         "Use secrets management for credentials and never store plaintext in code.",
# #         "Audit and remove any hard-coded or default credentials in builds or images."
# #     ],
# #     "secrets-in-repo": [
# #         "Rotate any secrets found in repositories and revoke leaked credentials immediately.",
# #         "Use secret scanning in CI to block commits with sensitive data.",
# #         "Adopt a secrets manager and inject secrets at runtime instead of storing them.",
# #         "Scan historical commits and remove secrets from the repo (use tools like BFG)."
# #     ],
# #     "default": [
# #         "Follow the principle of least privilege and secure default configurations.",
# #         "Validate and sanitize inputs; enforce strong authentication.",
# #         "Monitor logs and set up alerting for suspicious activity.",
# #         "Apply timely updates and patching for all dependencies."
# #     ]
# # }


# # def _get_remediation_for_tag(tag: str) -> List[str]:
# #     if not tag:
# #         return _REMEDIATION_TEMPLATES["default"]
# #     return _REMEDIATION_TEMPLATES.get(tag.lower(), _REMEDIATION_TEMPLATES["default"])


# # # -------------------------
# # # Public API for app.py compatibility
# # # -------------------------
# # def analyze_query_with_cvss(user_query: str, example: dict) -> Dict:
# #     """
# #     Keeps the same signature used by backend/app.py:
# #       analyze_query_with_cvss(user_query, ex)

# #     Returns a dict containing:
# #       - classification (string)
# #       - cvss_score (float 0..10)
# #       - explanation (string with ~4 short points)
# #       - remediation (list of strings)
# #     """
# #     # classification defaults to dataset tag
# #     classification = example.get("tag", "unknown")

# #     score, details = calculate_severity(user_query, use_similarity=True)

# #     # Build explanation: include the top contributing factors plus dataset context
# #     points = []
# #     # 1. Mention computed score
# #     points.append(f"Computed severity score: {round(score, 2)} / 10.")

# #     # 2. Heuristic factors
# #     heur_raw = details.get("heuristic_score_raw", 0.0)
# #     if heur_raw > 0:
# #         # mention matched keywords
# #         matched = details.get("matched_keywords", [])
# #         if matched:
# #             points.append(f"Matched keywords/phrases: {', '.join(matched)}.")
# #         else:
# #             points.append("Heuristic indicators detected in the query content.")

# #     # 3. Similarity-based evidence
# #     top_sim = details.get("top_similarity_matches", [])
# #     if top_sim:
# #         # show top 1-2 matches
# #         matches_text = "; ".join([f"{m[0]} - {m[1]} (sim={round(m[2],3)})" for m in top_sim[:2]])
# #         points.append(f"Query is semantically similar to known examples: {matches_text}.")

# #     # 4. Context from dataset example (brief)
# #     ex_title = example.get("title") or example.get("id", "N/A")
# #     ex_details = (example.get("details") or "")[:220]  # short snippet
# #     points.append(f"Reference example used: {ex_title}. Context: {ex_details}")

# #     # Ensure we have 4-5 points; if fewer, add generic guidance points
# #     if len(points) < 4:
# #         points.append("Apply least privilege and validate all user inputs.")
# #     if len(points) > 5:
# #         points = points[:5]

# #     # Build remediation from template (based on tag) — ensures list
# #     remediation = _get_remediation_for_tag(classification)
# #     if not isinstance(remediation, list):
# #         remediation = list(remediation)

# #     return {
# #         "classification": classification,
# #         "cvss_score": float(round(score, 3)),
# #         "explanation": " ".join(points),
# #         "remediation": remediation
# #     }

# # backend/services/scoring.py

# # import os
# # import json
# # from typing import List, Dict, Tuple
# # import numpy as np
# # from sentence_transformers import SentenceTransformer, util

# # # -------------------------
# # # Paths & dataset loading
# # # -------------------------
# # _DATASET_PATH = os.path.join(os.path.dirname(__file__), "../data/attackbench.json")
# # _dataset = None

# # def _load_dataset():
# #     global _dataset
# #     if _dataset is None:
# #         with open(_DATASET_PATH, "r", encoding="utf-8") as f:
# #             _dataset = json.load(f)
# #         # Combine title + details for easier processing
# #         for item in _dataset:
# #             item["_combined_text"] = f"{item.get('title','')} {item.get('details','')}"
# #     return _dataset

# # # -------------------------
# # # Sentence embeddings model
# # # -------------------------
# # _model = None
# # _embeddings = None

# # def _ensure_embeddings():
# #     global _model, _embeddings
# #     _load_dataset()
# #     if _model is None:
# #         _model = SentenceTransformer('all-MiniLM-L6-v2')
# #         texts = [item["_combined_text"] for item in _dataset]
# #         _embeddings = _model.encode(texts, convert_to_tensor=True)
# #     return _model, _embeddings

# # # -------------------------
# # # Keyword extraction (from dataset)
# # # -------------------------
# # def _extract_keywords(text: str, top_n: int = 10) -> List[str]:
# #     words = text.lower().split()
# #     freq = {}
# #     for w in words:
# #         if len(w) > 3:
# #             freq[w] = freq.get(w, 0) + 1
# #     sorted_words = sorted(freq.items(), key=lambda x: -x[1])
# #     return [w for w,_ in sorted_words[:top_n]]

# # # -------------------------
# # # Remediation templates
# # # -------------------------
# # _REMEDIATION_TEMPLATES = {
# #     "sql-injection": [
# #         "Use parameterized queries / prepared statements.",
# #         "Validate and sanitize all user inputs.",
# #         "Apply least privilege to DB accounts.",
# #         "Enable query logging for anomaly detection."
# #     ],
# #     "xss": [
# #         "Escape and encode all user content before rendering.",
# #         "Apply strict Content-Security-Policy (CSP).",
# #         "Use secure templating engines with auto-escape.",
# #         "Validate HTML or markdown inputs."
# #     ],
# #     "command-injection": [
# #         "Avoid shelling out with user input. Use safe APIs.",
# #         "Use argument arrays and proper escaping if shelling out.",
# #         "Run code in sandbox with minimal privileges.",
# #         "Validate filenames and restrict upload directories."
# #     ],
# #     "default": [
# #         "Enforce strong authentication and least privilege.",
# #         "Validate and sanitize all inputs.",
# #         "Monitor logs and alert suspicious activity.",
# #         "Apply timely updates and patches."
# #     ]
# # }

# # def _get_remediation(tag: str) -> List[str]:
# #     return _REMEDIATION_TEMPLATES.get(tag.lower(), _REMEDIATION_TEMPLATES["default"])

# # # -------------------------
# # # Scoring function
# # # -------------------------
# # def calculate_severity(query: str) -> Tuple[float, Dict]:
# #     """
# #     Compute 0-10 severity score using:
# #     - Keyword matches (dataset extracted)
# #     - Semantic similarity (embeddings)
# #     """
# #     if not query.strip():
# #         return 0.0, {"reason":"empty query"}
    
# #     _load_dataset()
# #     model, embeddings = _ensure_embeddings()
    
# #     query_emb = model.encode(query, convert_to_tensor=True)
    
# #     # Semantic similarity
# #     sims = util.cos_sim(query_emb, embeddings).cpu().numpy().flatten()
# #     best_idx = int(sims.argmax())
# #     best_sim = float(sims[best_idx])
    
# #     # Map similarity to score (0-10)
# #     sem_score = min(10.0, best_sim * 12)  # scale similarity
    
# #     # Keyword heuristic
# #     dataset_keywords = _extract_keywords(_dataset[best_idx]["_combined_text"])
# #     query_words = query.lower().split()
# #     matched_keywords = [w for w in query_words if w in dataset_keywords]
# #     heur_score = min(10.0, len(matched_keywords) * 1.5)
    
# #     final_score = min(10.0, heur_score + sem_score)
    
# #     details = {
# #         "heuristic_score": round(heur_score,3),
# #         "semantic_score": round(sem_score,3),
# #         "final_score": round(final_score,3),
# #         "matched_keywords": matched_keywords,
# #         "top_match": {
# #             "id": _dataset[best_idx].get("id"),
# #             "title": _dataset[best_idx].get("title"),
# #             "similarity": round(best_sim,3)
# #         }
# #     }
    
# #     return final_score, details

# # # -------------------------
# # # Main API: app.py compatibility
# # # -------------------------
# # def analyze_query_with_cvss(user_query: str, example: dict) -> Dict:
# #     """
# #     Returns dict compatible with app.py display:
# #       - classification
# #       - cvss_score
# #       - explanation
# #       - remediation
# #     """
# #     _load_dataset()
# #     classification = example.get("tag", "default")
    
# #     score, details = calculate_severity(user_query)
    
# #     # Explanation
# #     explanation_points = [
# #         f"Computed severity score: {round(score,2)}/10",
# #         f"Matched keywords: {', '.join(details.get('matched_keywords',[])) or 'None'}",
# #         f"Most similar example: {details['top_match']['title']} (sim={details['top_match']['similarity']})",
# #         f"Reference example ID: {details['top_match']['id']}"
# #     ]
    
# #     remediation = _get_remediation(classification)
    
# #     return {
# #         "classification": classification,
# #         "cvss_score": round(score,3),
# #         "explanation": " | ".join(explanation_points),
# #         "remediation": remediation
# #     }


# # backend/services/scoring.py
# # """
# # Dynamic CVSS-like severity scoring with Gemini-powered explanations and remediation.
# # """

# # import os
# # import json
# # from typing import List, Dict, Tuple
# # from sentence_transformers import SentenceTransformer, util
# # from retriever.search import search
# # from services.gemini_service import analyze_example_with_gemini  # your Gemini integration

# # # -----------------------------
# # # Dataset and embeddings
# # # -----------------------------
# # _DATASET_PATH = os.path.join(os.path.dirname(__file__), "../data/attackbench.json")
# # _dataset = None
# # _model = None
# # _embeddings = None

# # def _load_dataset():
# #     global _dataset
# #     if _dataset is None:
# #         with open(_DATASET_PATH, "r", encoding="utf-8") as f:
# #             _dataset = json.load(f)
# #         for item in _dataset:
# #             item["_combined_text"] = f"{item.get('title','')} {item.get('details','')}"
# #     return _dataset

# # def _ensure_embeddings():
# #     global _model, _embeddings
# #     _load_dataset()
# #     if _model is None:
# #         _model = SentenceTransformer('all-MiniLM-L6-v2')
# #     if _embeddings is None:
# #         _embeddings = _model.encode([item["_combined_text"] for item in _dataset], convert_to_tensor=True)
# #     return _model, _embeddings

# # # -----------------------------
# # # Keyword heuristics
# # # -----------------------------
# # _CRITICAL_ACTIONS = {
# #     "delete": 3.0, "drop": 3.0, "execute": 3.0, "rce": 4.0,
# #     "remote code execution": 4.0, "bypass": 3.5, "exploit": 3.5,
# #     "upload": 2.5, "overwrite": 2.5, "privilege escalation": 4.0,
# #     "escalate": 3.0, "bypass authentication": 4.0, "gain access": 3.5
# # }

# # _SENSITIVE_TARGETS = {
# #     "admin": 3.0, "root": 4.0, "database": 3.5, "db": 3.0,
# #     "server": 3.0, "config": 2.5, "credentials": 3.5,
# #     "api key": 3.5, "secret": 3.5, "token": 3.0, "ssh": 3.5
# # }

# # _EXPOSURE_TERMS = {
# #     "public": 1.5, "internet": 1.5, "remote": 1.5,
# #     "exposed": 1.5, "open": 1.0, "unauthenticated": 2.0, "anonymous": 1.5
# # }

# # _BASE_INTENT_SCORE = 1.5
# # _SIMILARITY_MAX = 4.0

# # # -----------------------------
# # # Core severity calculation
# # # -----------------------------
# # def calculate_severity(query: str, example: dict) -> Tuple[float, Dict]:
# #     """
# #     Compute 0-10 severity score using:
# #     - Keyword matches
# #     - Semantic similarity
# #     """
# #     if not query.strip():
# #         return 0.0, {"reason": "empty query"}

# #     _load_dataset()
# #     model, embeddings = _ensure_embeddings()

# #     query_emb = model.encode(query, convert_to_tensor=True)

# #     # Semantic similarity
# #     sims = util.cos_sim(query_emb, embeddings)[0]
# #     top_idx = int(sims.argmax())
# #     top_sim = float(sims[top_idx])

# #     # Keyword heuristic
# #     top_example_text = _dataset[top_idx]["_combined_text"].lower()
# #     heur_score = 0.0
# #     matched_keywords = []
# #     for kw_dict in [_CRITICAL_ACTIONS, _SENSITIVE_TARGETS, _EXPOSURE_TERMS]:
# #         for kw, w in kw_dict.items():
# #             if kw in query.lower():
# #                 heur_score += w
# #                 matched_keywords.append(kw)

# #     # Normalize
# #     HEURISTIC_MAX_ALLOCATION = 10.0 - _SIMILARITY_MAX
# #     RAW_HEURISTIC_CAP = 12.0
# #     heur_norm = min(heur_score, RAW_HEURISTIC_CAP) / RAW_HEURISTIC_CAP * HEURISTIC_MAX_ALLOCATION

# #     final_score = max(min(heur_norm + min(_SIMILARITY_MAX, top_sim * _SIMILARITY_MAX * 1.2), 10.0),
# #                       _BASE_INTENT_SCORE if matched_keywords else 0.0)

# #     details = {
# #         "heuristic_score_raw": heur_score,
# #         "heuristic_score_normalized": round(heur_norm,3),
# #         "semantic_score": round(top_sim,3),
# #         "final_score": round(final_score,3),
# #         "matched_keywords": matched_keywords
# #     }

# #     return final_score, details

# # # -----------------------------
# # # Public API for app.py
# # # -----------------------------
# # def analyze_query_with_cvss(user_query: str, example: dict) -> Dict:
# #     """
# #     Returns dict compatible with app.py display:
# #       - classification
# #       - cvss_score
# #       - explanation
# #       - remediation
# #     """
# #     # Step 1: core scoring
# #     score, details = calculate_severity(user_query, example)

# #     # Step 2: dynamic explanation/remediation using Gemini
# #     try:
# #         gemini_res = analyze_example_with_gemini(user_query, example)
# #         explanation = gemini_res.get("explanation") or "No explanation provided"
# #         remediation = gemini_res.get("remediation") or ["Investigate and remediate"]
# #         classification = gemini_res.get("classification") or example.get("tag","unknown")
# #         severity = gemini_res.get("severity") or round(score,2)
# #         print("Success")
# #     except Exception:
# #         # fallback
# #         explanation = "Fallback explanation: review the dataset and query context."
# #         remediation = ["Check the input query", "Review the dataset example", "Apply security best practices"]
# #         classification = example.get("tag","unknown")
# #         severity = round(score,2)
# #         print("error")

# #     return {
# #         "classification": classification,
# #         "cvss_score": float(round(severity,3)),
# #         "explanation": explanation,
# #         "remediation": remediation
# #     }
# # backend/services/scoring.py

# import os
# import json
# from typing import List, Dict, Tuple
# import numpy as np
# from sentence_transformers import SentenceTransformer, util
# import logging

# logger = logging.getLogger(__name__)

# # -------------------------
# # Paths & dataset loading
# # -------------------------
# _DATASET_PATH = os.path.join(os.path.dirname(__file__), "../data/attackbench.json")
# _dataset = None

# def _load_dataset():
#     global _dataset
#     if _dataset is None:
#         with open(_DATASET_PATH, "r", encoding="utf-8") as f:
#             _dataset = json.load(f)
#         for item in _dataset:
#             item["_combined_text"] = f"{item.get('title', '')} {item.get('details', '')}"
#     return _dataset

# # -------------------------
# # Sentence embeddings model
# # -------------------------
# _model = None
# _embeddings = None

# def _ensure_embeddings():
#     global _model, _embeddings
#     _load_dataset()
#     if _model is None:
#         logger.info("Loading embedding model and computing dataset embeddings...")
#         _model = SentenceTransformer('all-MiniLM-L6-v2')
#         texts = [item["_combined_text"] for item in _dataset]
#         _embeddings = _model.encode(texts, convert_to_tensor=True)
#     return _model, _embeddings

# # -------------------------
# # Keyword extraction
# # -------------------------
# def _extract_keywords(text: str, top_n: int = 10) -> List[str]:
#     words = text.lower().split()
#     freq = {}
#     for w in words:
#         if len(w) > 3:
#             freq[w] = freq.get(w, 0) + 1
#     sorted_words = sorted(freq.items(), key=lambda x: -x[1])
#     return [w for w, _ in sorted_words[:top_n]]

# # -------------------------
# # Remediation templates
# # -------------------------
# _REMEDIATION_TEMPLATES = {
#     "sql-injection": [
#         "Use parameterized queries / prepared statements.",
#         "Validate and sanitize all user inputs.",
#         "Apply least privilege to DB accounts.",
#         "Enable query logging for anomaly detection."
#     ],
#     "xss": [
#         "Escape and encode all user content before rendering.",
#         "Apply strict Content-Security-Policy (CSP).",
#         "Use secure templating engines with auto-escape.",
#         "Validate HTML or markdown inputs."
#     ],
#     "command-injection": [
#         "Avoid shelling out with user input. Use safe APIs.",
#         "Use argument arrays and proper escaping if shelling out.",
#         "Run code in sandbox with minimal privileges.",
#         "Validate filenames and restrict upload directories."
#     ],
#     "default": [
#         "Enforce strong authentication and least privilege.",
#         "Validate and sanitize all inputs.",
#         "Monitor logs and alert suspicious activity.",
#         "Apply timely updates and patches."
#     ]
# }

# def _get_remediation(tag: str) -> List[str]:
#     return _REMEDIATION_TEMPLATES.get(tag.lower(), _REMEDIATION_TEMPLATES["default"])

# # -------------------------
# # Scoring logic
# # -------------------------
# # def calculate_severity(query: str) -> Tuple[float, Dict]:
# #     """
# #     Compute 0–10 severity score based on dataset similarity + keyword overlap.
# #     """
# #     if not query.strip():
# #         return 0.0, {"reason": "empty query"}

# #     _load_dataset()
# #     model, embeddings = _ensure_embeddings()

# #     query_emb = model.encode(query, convert_to_tensor=True)

# #     # Compute cosine similarity with dataset examples
# #     sims = util.cos_sim(query_emb, embeddings).cpu().numpy().flatten()
# #     best_idx = int(sims.argmax())
# #     best_sim = float(sims[best_idx])

# #     # Convert similarity to 0–10 scale
# #     sem_score = min(10.0, best_sim * 12)

# #     # Keyword heuristic
# #     dataset_keywords = _extract_keywords(_dataset[best_idx]["_combined_text"])
# #     query_words = query.lower().split()
# #     matched_keywords = [w for w in query_words if w in dataset_keywords]
# #     heur_score = min(10.0, len(matched_keywords) * 1.5)

# #     final_score = min(10.0, heur_score + sem_score)

# #     details = {
# #         "heuristic_score": round(heur_score, 3),
# #         "semantic_score": round(sem_score, 3),
# #         "final_score": round(final_score, 3),
# #         "matched_keywords": matched_keywords,
# #         "top_match": {
# #             "id": _dataset[best_idx].get("id"),
# #             "title": _dataset[best_idx].get("title"),
# #             "similarity": round(best_sim, 3)
# #         }
# #     }

# #     logger.info(f"Severity Debug -> Heuristic: {heur_score}, Semantic: {sem_score}, Final: {final_score}, Match: {_dataset[best_idx]['title']}")
# #     return final_score, details

# # # -------------------------
# # # API bridge (used by app.py)
# # # -------------------------
# # def analyze_query_with_cvss(user_query: str, example: dict) -> Dict:
# #     """
# #     Return dict with computed severity + metadata (Gemini handles explanation).
# #     """
# #     _load_dataset()
# #     classification = example.get("tag", "default")

# #     score, details = calculate_severity(user_query)

# #     return {
# #         "classification": classification,
# #         "cvss_score": round(score, 3),
# #         "debug_details": details,
# #         "remediation": _get_remediation(classification)
# #     }

# # -------------------------
# # Scoring logic (updated for top 3–5 datasets)
# # -------------------------
# def calculate_severity(query: str, top_n: int = 5) -> Tuple[float, Dict]:
#     """
#     Compute 0–10 severity score based on dataset similarity + keyword overlap.
#     Returns top N dataset matches for explainability.
#     """
#     if not query.strip():
#         return 0.0, {"reason": "empty query"}

#     _load_dataset()
#     model, embeddings = _ensure_embeddings()

#     query_emb = model.encode(query, convert_to_tensor=True)

#     # Compute cosine similarity with dataset examples
#     sims = util.cos_sim(query_emb, embeddings).cpu().numpy().flatten()

#     # Get top N indices
#     top_indices = sims.argsort()[::-1][:top_n]

#     top_matches = []
#     for idx in top_indices:
#         top_matches.append({
#             "id": _dataset[idx].get("id"),
#             "title": _dataset[idx].get("title"),
#             "similarity": round(float(sims[idx]), 3),
#             "details": _dataset[idx].get("details", "")[:200]  # short snippet
#         })

#     # Use the highest similarity for scoring
#     best_idx = top_indices[0]
#     best_sim = float(sims[best_idx])

#     # Convert similarity to 0–10 scale
#     sem_score = min(10.0, best_sim * 12)

#     # Keyword heuristic based on top match
#     dataset_keywords = _extract_keywords(_dataset[best_idx]["_combined_text"])
#     query_words = query.lower().split()
#     matched_keywords = [w for w in query_words if w in dataset_keywords]
#     heur_score = min(10.0, len(matched_keywords) * 1.5)

#     # Combine scores
#     final_score = min(10.0, heur_score + sem_score)

#     details = {
#         "heuristic_score": round(heur_score, 3),
#         "semantic_score": round(sem_score, 3),
#         "final_score": round(final_score, 3),
#         "matched_keywords": matched_keywords,
#         "top_matches": top_matches  # top 3–5 dataset matches
#     }

#     logger.info(f"Severity Debug -> Heuristic: {heur_score}, Semantic: {sem_score}, Final: {final_score}, Top match: {_dataset[best_idx]['title']}")
#     return final_score, details

# # -------------------------
# # API bridge (used by app.py)
# # -------------------------
# def analyze_query_with_cvss(user_query: str, example: dict) -> Dict:
#     """
#     Returns dict compatible with app.py display:
#       - classification
#       - cvss_score
#       - top_matches (3–5 similar datasets)
#       - debug_details
#       - remediation
#     """
#     _load_dataset()
#     classification = example.get("tag", "default")

#     # Step 1: compute severity
#     score, details = calculate_severity(user_query, top_n=5)

#     # Step 2: dynamic explanation/remediation using Gemini (if available)
#     try:
#         from services.gemini_service import analyze_example_with_gemini
#         gemini_res = analyze_example_with_gemini(user_query, example)
#         explanation = gemini_res.get("explanation") or "No explanation provided"
#         remediation = gemini_res.get("remediation") or ["Investigate and remediate"]
#         classification = gemini_res.get("classification") or classification
#         severity = gemini_res.get("severity") or round(score, 2)
#     except Exception:
#         # fallback if Gemini fails
#         explanation = "Fallback explanation: review the dataset and query context."
#         remediation = ["Check the input query", "Review the dataset example", "Apply security best practices"]
#         severity = round(score, 2)

#     return {
#         "classification": classification,
#         "cvss_score": float(round(severity, 3)),
#         "top_matches": details["top_matches"],  # top 3–5 dataset matches
#         "debug_details": details,
#         "remediation": remediation,
#         "explanation": explanation
#     }


# backend/services/scoring.py

import os
import json
from typing import List, Dict, Tuple
import logging
from sentence_transformers import SentenceTransformer, util

logger = logging.getLogger(__name__)

# -------------------------
# Paths & dataset loading
# -------------------------
_DATASET_PATH = os.path.join(os.path.dirname(__file__), "../data/attackbench.json")
_dataset = None

def _load_dataset():
    global _dataset
    if _dataset is None:
        with open(_DATASET_PATH, "r", encoding="utf-8") as f:
            _dataset = json.load(f)
        for item in _dataset:
            item["_combined_text"] = f"{item.get('title','')} {item.get('details','')}"
    return _dataset

# -------------------------
# Sentence embeddings model
# -------------------------
_model = None
_embeddings = None

def _ensure_embeddings():
    global _model, _embeddings
    _load_dataset()
    if _model is None:
        logger.info("Loading embedding model...")
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    if _embeddings is None:
        texts = [item["_combined_text"] for item in _dataset]
        _embeddings = _model.encode(texts, convert_to_tensor=True)
    return _model, _embeddings

# -------------------------
# Keyword extraction
# -------------------------
def _extract_keywords(text: str, top_n: int = 10) -> List[str]:
    words = text.lower().split()
    freq = {}
    for w in words:
        if len(w) > 3:
            freq[w] = freq.get(w, 0) + 1
    sorted_words = sorted(freq.items(), key=lambda x: -x[1])
    return [w for w, _ in sorted_words[:top_n]]

# -------------------------
# Remediation templates
# -------------------------
_REMEDIATION_TEMPLATES = {
    "sql-injection": [
        "Use parameterized queries / prepared statements.",
        "Validate and sanitize all user inputs.",
        "Apply least privilege to DB accounts.",
        "Enable query logging for anomaly detection."
    ],
    "xss": [
        "Escape and encode all user content before rendering.",
        "Apply strict Content-Security-Policy (CSP).",
        "Use secure templating engines with auto-escape.",
        "Validate HTML or markdown inputs."
    ],
    "command-injection": [
        "Avoid shelling out with user input. Use safe APIs.",
        "Use argument arrays and proper escaping if shelling out.",
        "Run code in sandbox with minimal privileges.",
        "Validate filenames and restrict upload directories."
    ],
    "default": [
        "Enforce strong authentication and least privilege.",
        "Validate and sanitize all inputs.",
        "Monitor logs and alert suspicious activity.",
        "Apply timely updates and patches."
    ]
}

def _get_remediation(tag: str) -> List[str]:
    return _REMEDIATION_TEMPLATES.get(tag.lower(), _REMEDIATION_TEMPLATES["default"])

# -------------------------
# Scoring logic
# -------------------------
def calculate_severity(query: str, top_n: int = 5) -> Tuple[float, Dict]:
    """
    Compute 0–10 severity score using:
      - Keyword matches across top N dataset matches
      - Semantic similarity (average across top N matches)
    Returns:
      - final_score (0-10)
      - details dict containing top_matches, heuristic/semantic contributions, matched keywords
    """
    if not query.strip():
        return 0.0, {"reason": "empty query"}

    _load_dataset()
    model, embeddings = _ensure_embeddings()
    query_emb = model.encode(query, convert_to_tensor=True)

    # Compute cosine similarity with dataset examples
    sims = util.cos_sim(query_emb, embeddings).cpu().numpy().flatten()

    # Get top N matches
    top_indices = sims.argsort()[::-1][:top_n]

    top_matches = []
    heuristic_scores = []
    semantic_scores = []
    all_matched_keywords = set()

    for idx in top_indices:
        example_text = _dataset[idx]["_combined_text"].lower()
        dataset_keywords = _extract_keywords(example_text)
        query_words = query.lower().split()
        matched_keywords = [w for w in query_words if w in dataset_keywords]
        all_matched_keywords.update(matched_keywords)

        # Heuristic contribution (max 5 per top example)
        heur_score = min(5.0, len(matched_keywords) * 1.5)
        heuristic_scores.append(heur_score)

        # Semantic contribution (similarity mapped 0-10 per example)
        sim_score = min(10.0, float(sims[idx]) * 12)
        semantic_scores.append(sim_score)

        top_matches.append({
            "id": _dataset[idx].get("id"),
            "title": _dataset[idx].get("title"),
            "similarity": round(float(sims[idx]), 3),
            "details": _dataset[idx].get("details", "")[:200]
        })

    # Combine top N contributions
    avg_heur_score = sum(heuristic_scores) / len(heuristic_scores)
    avg_sem_score = sum(semantic_scores) / len(semantic_scores)
    final_score = min(10.0, avg_heur_score + avg_sem_score)
    final_score = max(final_score, 0.0)

    details = {
        "heuristic_score": round(avg_heur_score, 3),
        "semantic_score": round(avg_sem_score, 3),
        "final_score": round(final_score, 3),
        "matched_keywords": list(all_matched_keywords),
        "top_matches": top_matches
    }

    logger.info(f"Severity Debug -> Heur: {avg_heur_score}, Sem: {avg_sem_score}, Final: {final_score}, Top match: {_dataset[top_indices[0]]['title']}")
    return final_score, details

# -------------------------
# Public API for app.py
# -------------------------
def analyze_query_with_cvss(user_query: str, example: dict) -> Dict:
    """
    Returns dict compatible with app.py display:
      - classification
      - cvss_score
      - top_matches (3–5 similar datasets)
      - debug_details
      - remediation
    """
    _load_dataset()
    classification = example.get("tag", "default")

    # Step 1: compute severity
    score, details = calculate_severity(user_query, top_n=5)

    # Step 2: dynamic explanation/remediation using Gemini (if available)
    try:
        from services.gemini_service import analyze_example_with_gemini
        gemini_res = analyze_example_with_gemini(user_query, example)
        explanation = gemini_res.get("explanation") or "No explanation provided"
        remediation = gemini_res.get("remediation") or ["Investigate and remediate"]
        classification = gemini_res.get("classification") or classification
        severity = gemini_res.get("severity") or round(score, 2)
    except Exception:
        # fallback if Gemini fails
        explanation = "Fallback explanation: review the dataset and query context."
        remediation = ["Check the input query", "Review the dataset example", "Apply security best practices"]
        severity = round(score, 2)

    return {
        "classification": classification,
        "cvss_score": float(round(severity, 3)),
        "top_matches": details["top_matches"],  # top 3–5 dataset matches
        "debug_details": details,
        "remediation": remediation,
        "explanation": explanation
    }
