import React, { useState } from "react";

function App() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSearch = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await fetch("http://127.0.0.1:5000/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, top_k: 3 }),
      });

      if (!response.ok) throw new Error("Failed to fetch");

      const data = await response.json();
      setResults(data.enriched || []);
    } catch (err) {
      console.error(err);
      setError("Error fetching results: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "20px", fontFamily: "Arial" }}>
      <h1>Security Query Analyzer</h1>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Enter your security query"
        style={{ width: "400px", padding: "8px" }}
      />
      <button onClick={handleSearch} style={{ marginLeft: "10px", padding: "8px 12px" }}>
        Analyze
      </button>

      {loading && <p>Loading results...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {results.length > 0 && (
        <div style={{ marginTop: "20px" }}>
          {results.map((item, idx) => (
            <div key={idx} style={{ border: "1px solid #ccc", padding: "10px", marginBottom: "10px" }}>
              <p><strong>Dataset:</strong> {item.dataset.name || "N/A"}</p>
              <p><strong>Classification:</strong> {item.gemini.classification}</p>
              <p><strong>Severity:</strong> {item.gemini.severity}</p>
              <p><strong>Explanation:</strong> {item.gemini.explanation}</p>
              <p><strong>Remediation:</strong></p>
              <ul>
                {(() => {
                  try {
                    const remediation = JSON.parse(item.gemini.remediation);
                    return remediation.map((r, i) => <li key={i}>{r}</li>);
                  } catch {
                    return <li>{item.gemini.remediation}</li>;
                  }
                })()}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;
