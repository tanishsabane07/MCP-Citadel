// // // // src/App.js
// // // import React, { useState } from "react";

// // // function App() {
// // //   const [userQuery, setUserQuery] = useState("");
// // //   const [results, setResults] = useState([]);
// // //   const [loading, setLoading] = useState(false);
// // //   const [error, setError] = useState("");

// // //   const handleAnalyze = async () => {
// // //     if (!userQuery.trim()) return;
// // //     setLoading(true);
// // //     setError("");
// // //     setResults([]);

// // //     try {
// // //       const response = await fetch("http://127.0.0.1:5000/api/analyze", {
// // //         method: "POST",
// // //         headers: { "Content-Type": "application/json" },
// // //         body: JSON.stringify({ query: userQuery, top_k: 3 }),
// // //       });

// // //       if (!response.ok) {
// // //         setError(`Server error: ${response.status}`);
// // //         setLoading(false);
// // //         return;
// // //       }

// // //       const data = await response.json();
// // //       console.log("Analysis data:", data); // debugging
// // //       setResults(data.enriched || []);
// // //     } catch (err) {
// // //       console.error(err);
// // //       setError("Failed to fetch results. Check backend.");
// // //     } finally {
// // //       setLoading(false);
// // //     }
// // //   };

// // //   return (
// // //     <div style={{ padding: "20px" }}>
// // //       <h1>Security Scanner Analysis</h1>

// // //       <input
// // //         type="text"
// // //         value={userQuery}
// // //         onChange={(e) => setUserQuery(e.target.value)}
// // //         placeholder="Enter query"
// // //         style={{ width: "300px", marginRight: "10px" }}
// // //       />
// // //       <button onClick={handleAnalyze} disabled={loading}>
// // //         {loading ? "Analyzing..." : "Analyze"}
// // //       </button>

// // //       {error && <p style={{ color: "red" }}>{error}</p>}

// // //       {results.map((item, index) => (
// // //         <div
// // //           key={index}
// // //           style={{
// // //             border: "1px solid #ccc",
// // //             padding: "10px",
// // //             marginTop: "10px",
// // //             borderRadius: "5px",
// // //           }}
// // //         >
// // //           <h3>
// // //             Dataset: {item.dataset.name || "N/A"}
// // //           </h3>
// // //           <p>Description: {item.dataset.description || "N/A"}</p>
// // //           <p>
// // //             Classification: {item.gemini.classification || "N/A"} | Severity:{" "}
// // //             {item.gemini.severity ?? "N/A"}
// // //           </p>
// // //           <p>Explanation:</p>
// // //           <ul>
// // //             {item.gemini.explanation
// // //               ? item.gemini.explanation.split("\n").map((line, idx) => (
// // //                   <li key={idx}>{line}</li>
// // //                 ))
// // //               : <li>No explanation provided</li>}
// // //           </ul>
// // //           <p>Remediation:</p>
// // //           <ul>
// // //             {Array.isArray(item.gemini.remediation)
// // //               ? item.gemini.remediation.map((step, idx) => (
// // //                   <li key={idx}>{step}</li>
// // //                 ))
// // //               : <li>No remediation steps</li>}
// // //           </ul>
// // //         </div>
// // //       ))}
// // //     </div>
// // //   );
// // // }

// // // export default App;

// // // src/App.js
// // // import React, { useState } from "react";

// // // function App() {
// // //   const [query, setQuery] = useState("");
// // //   const [results, setResults] = useState([]);
// // //   const [history, setHistory] = useState([]);

// // //   const handleSearch = async () => {
// // //     if (!query) return;
// // //     try {
// // //       const res = await fetch("http://127.0.0.1:5000/api/analyze", {
// // //         method: "POST",
// // //         headers: { "Content-Type": "application/json" },
// // //         body: JSON.stringify({ query, top_k: 3 }),
// // //       });
// // //       const data = await res.json();
// // //       setResults(data.enriched || []);
// // //     } catch (err) {
// // //       console.error("Error fetching results:", err);
// // //     }
// // //   };

// // //   const fetchHistory = async () => {
// // //     try {
// // //       const res = await fetch("http://127.0.0.1:5000/api/history");
// // //       const data = await res.json();
// // //       setHistory(data.history || []);
// // //     } catch (err) {
// // //       console.error("Error fetching history:", err);
// // //     }
// // //   };

// // //   return (
// // //     <div style={{ padding: "20px", fontFamily: "Arial" }}>
// // //       <h2>Security Scanner</h2>
// // //       <div>
// // //         <input
// // //           type="text"
// // //           value={query}
// // //           onChange={(e) => setQuery(e.target.value)}
// // //           placeholder="Enter your query"
// // //           style={{ width: "300px", marginRight: "10px" }}
// // //         />
// // //         <button onClick={handleSearch}>Analyze</button>
// // //         <button onClick={fetchHistory} style={{ marginLeft: "10px" }}>
// // //           Check History
// // //         </button>
// // //       </div>

// // //       <h3>Analysis Results</h3>
// // //       {results.length === 0 ? (
// // //         <p>No results yet.</p>
// // //       ) : (
// // //         results.map((item, idx) => (
// // //           <div key={idx} style={{ border: "1px solid #ccc", padding: "10px", marginBottom: "10px" }}>
// // //             <p><strong>Dataset Name:</strong> {item.dataset.name}</p>
// // //             <p><strong>Description:</strong> {item.dataset.description || "N/A"}</p>
// // //             <p><strong>Classification:</strong> {item.gemini.classification}</p>
// // //             <p><strong>Severity:</strong> {item.gemini.severity}</p>
// // //             <p><strong>Explanation:</strong> {item.gemini.explanation || "No explanation provided"}</p>
// // //             <p><strong>Remediation:</strong></p>
// // //             <ul>
// // //               {item.gemini.remediation.map((step, i) => (
// // //                 <li key={i}>{step}</li>
// // //               ))}
// // //             </ul>
// // //           </div>
// // //         ))
// // //       )}

// // //       <h3>History</h3>
// // //       {history.length === 0 ? (
// // //         <p>No history yet.</p>
// // //       ) : (
// // //         history.map((item, idx) => (
// // //           <div key={idx} style={{ border: "1px dashed #999", padding: "10px", marginBottom: "10px" }}>
// // //             <p><strong>Query:</strong> {item.query}</p>
// // //             <p><strong>Dataset:</strong> {item.dataset_name || item.example_id || "N/A"}</p>
// // //             <p><strong>Classification:</strong> {item.classification}</p>
// // //             <p><strong>Severity:</strong> {item.severity}</p>
// // //             <p><strong>Explanation:</strong> {item.explanation || "No explanation"}</p>
// // //             <p><strong>Remediation:</strong></p>
// // //             <ul>
// // //               {item.remediation && item.remediation.map((step, i) => <li key={i}>{step}</li>)}
// // //             </ul>
// // //           </div>
// // //         ))
// // //       )}
// // //     </div>
// // //   );
// // // }

// // // export default App;

// // import React, { useState } from "react";
// // import axios from "axios";

// // function App() {
// //   const [query, setQuery] = useState("");
// //   const [results, setResults] = useState([]);

// //   const handleAnalyze = async () => {
// //     try {
// //       const response = await axios.post("http://localhost:5000/api/analyze", {
// //         query,
// //         top_k: 3
// //       });
// //       setResults(response.data.enriched || []);
// //     } catch (err) {
// //       console.error(err);
// //       alert("Analysis failed");
// //     }
// //   };

// //   return (
// //     <div className="p-4">
// //       <h1 className="text-2xl mb-4">Dynamic CVSS Analyzer</h1>
// //       <input
// //         type="text"
// //         className="border p-2 w-full mb-2"
// //         value={query}
// //         onChange={(e) => setQuery(e.target.value)}
// //         placeholder="Enter your query"
// //       />
// //       <button className="bg-blue-500 text-white px-4 py-2 mb-4" onClick={handleAnalyze}>
// //         Analyze
// //       </button>

// //       {results.map((item, idx) => (
// //         <div key={idx} className="border p-3 mb-3">
// //           <h2 className="font-bold">{item.dataset.name}</h2>
// //           <p>{item.dataset.description}</p>
// //           <p className="mt-1">
// //             <strong>CVSS Score:</strong> {item.analysis.cvss_score}
// //           </p>
// //           <p className="mt-1"><strong>Classification:</strong> {item.analysis.classification}</p>
// //           <p className="mt-1"><strong>Explanation:</strong> {item.analysis.explanation}</p>
// //           <p className="mt-1">
// //             <strong>Remediation:</strong>
// //             <ul>
// //               {item.analysis.remediation.map((step, i) => (
// //                 <li key={i}>{step}</li>
// //               ))}
// //             </ul>
// //           </p>
// //         </div>
// //       ))}
// //     </div>
// //   );
// // }

// // export default App;

// import React, { useState } from "react";

// function App() {
//   const [query, setQuery] = useState("");
//   const [result, setResult] = useState(null);
//   const [loading, setLoading] = useState(false);

//   const analyzeQuery = async () => {
//     setLoading(true);
//     setResult(null);
//     try {
//       const res = await fetch("http://localhost:5000/analyze", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ query }),
//       });
//       const data = await res.json();
//       setResult(data);
//     } catch (err) {
//       console.error(err);
//       setResult({ error: "Failed to fetch analysis." });
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <div className="p-6 max-w-3xl mx-auto text-gray-800">
//       <h1 className="text-2xl font-bold mb-4">AI Security Vulnerability Analyzer</h1>
//       <textarea
//         className="w-full p-3 border rounded-md"
//         rows="4"
//         placeholder="Describe a potential attack or vulnerability..."
//         value={query}
//         onChange={(e) => setQuery(e.target.value)}
//       ></textarea>
//       <button
//         className="mt-3 px-5 py-2 bg-blue-600 text-white rounded-md"
//         onClick={analyzeQuery}
//         disabled={loading}
//       >
//         {loading ? "Analyzing..." : "Analyze"}
//       </button>

//       {result && (
//         <div className="mt-6 p-4 border rounded-md bg-gray-50">
//           {result.error && <p className="text-red-500">{result.error}</p>}
//           {!result.error && (
//             <>
//               <p><strong>Classification:</strong> {result.classification}</p>
//               <p><strong>Severity Score:</strong> {result.severity}/10</p>
//               <p><strong>Explanation:</strong> {result.explanation}</p>

//               <p className="mt-2 font-semibold">Remediation Steps:</p>
//               <ul className="list-disc pl-5">
//                 {result.remediation?.map((r, i) => <li key={i}>{r}</li>)}
//               </ul>

//               <details className="mt-3">
//                 <summary className="cursor-pointer text-blue-600">Debug Info</summary>
//                 <pre className="text-xs bg-gray-100 p-2 mt-1 rounded">
//                   {JSON.stringify(result.debug, null, 2)}
//                 </pre>
//               </details>
//             </>
//           )}
//         </div>
//       )}
//     </div>
//   );
// }

// export default App;

// // frontend/src/App.js
// import React, { useState } from "react";
// import "./App.css";

// function App() {
//   const [query, setQuery] = useState("");
//   const [result, setResult] = useState(null);
//   const [loading, setLoading] = useState(false);
//   const [history, setHistory] = useState([]);
//   const [showHistory, setShowHistory] = useState(false);

//   const handleAnalyze = async () => {
//     if (!query.trim()) return alert("Please enter a query!");
//     setLoading(true);
//     setResult(null);

//     try {
//       const response = await fetch("http://localhost:5000/analyze", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ query }),
//       });
//       const data = await response.json();
//       setResult(data);
//     } catch (error) {
//       console.error("Error analyzing:", error);
//       alert("Error analyzing query");
//     } finally {
//       setLoading(false);
//     }
//   };

//   const handleShowHistory = async () => {
//     setShowHistory(!showHistory);
//     if (!showHistory) {
//       try {
//         const res = await fetch("http://localhost:5000/history");
//         const data = await res.json();
//         setHistory(data.history || []);
//       } catch (err) {
//         console.error("Error fetching history:", err);
//       }
//     }
//   };

//   return (
//     <div className="app-container">
//       <h1>AI Security Scanner</h1>

//       <div className="query-box">
//         <textarea
//           placeholder="Enter a query, e.g. 'Insert malware through email'"
//           value={query}
//           onChange={(e) => setQuery(e.target.value)}
//           rows={3}
//         />
//         <button onClick={handleAnalyze} disabled={loading}>
//           {loading ? "Analyzing..." : "Analyze"}
//         </button>
//         <button onClick={handleShowHistory}>
//           {showHistory ? "Hide History" : "Show History"}
//         </button>
//       </div>

//       {result && (
//         <div className="result-box">
//           <h2>Analysis Result</h2>
//           <p>
//             <strong>Classification:</strong> {result.classification}
//           </p>
//           <p>
//             <strong>Severity Score:</strong> {result.severity?.toFixed(2)} / 10
//           </p>
//           <p>
//             <strong>Explanation:</strong> {result.explanation}
//           </p>
//           <p>
//             <strong>Remediation:</strong>
//           </p>
//           <ul>
//             {Array.isArray(result.remediation)
//               ? result.remediation.map((r, i) => <li key={i}>{r}</li>)
//               : <li>{result.remediation}</li>}
//           </ul>
//         </div>
//       )}

//       {showHistory && (
//         <div className="history-box">
//           <h2>Query History</h2>
//           {history.length === 0 ? (
//             <p>No history found</p>
//           ) : (
//             <table className="history-table">
//               <thead>
//                 <tr>
//                   <th>ID</th>
//                   <th>Timestamp</th>
//                   <th>Query</th>
//                   <th>Classification</th>
//                   <th>Score</th>
//                   <th>Dataset</th>
//                   <th>Explanation</th>
//                   <th>Remediation</th>
//                 </tr>
//               </thead>
//               <tbody>
//                 {history.map((item) => (
//                   <tr key={item.id}>
//                     <td>{item.id}</td>
//                     <td>{new Date(item.timestamp).toLocaleString()}</td>
//                     <td>{item.query}</td>
//                     <td>{item.classification}</td>
//                     <td>{item.cvss_score?.toFixed(2)}</td>
//                     <td>{item.dataset_name || "—"}</td>
//                     <td className="wrap-text">{item.explanation || "—"}</td>
//                     <td className="wrap-text">
//                       {Array.isArray(item.remediation)
//                         ? item.remediation.join(", ")
//                         : item.remediation || "—"}
//                     </td>
//                   </tr>
//                 ))}
//               </tbody>
//             </table>
//           )}
//         </div>
//       )}

// <button
//   onClick={() => window.open("http://localhost:5000/export_history", "_blank")}
//   className="bg-blue-600 text-white hover:bg-blue-700"
// >
//   Export CSV
// </button>

      
//     </div>
//   );
// }

// export default App;


// import React, { useState, useEffect } from "react";
// import axios from "axios";

// function App() {
//   const [query, setQuery] = useState("");
//   const [result, setResult] = useState(null);
//   const [history, setHistory] = useState([]);
//   const [showDatasets, setShowDatasets] = useState(false);
//   const [showHistory, setShowHistory] = useState(false);
  

//   // Fetch history on mount
//   useEffect(() => {
//     fetchHistory();
//   }, []);

//   const fetchHistory = async () => {
//     try {
//       const res = await axios.get("http://localhost:5000/history");
//       setHistory(res.data.history);
//     } catch (err) {
//       console.error(err);
//     }
//   };

//   const handleAnalyze = async () => {
//     if (!query.trim()) return;
//     try {
//       const res = await axios.post("http://localhost:5000/analyze", { query });
//       setResult(res.data);
//       setShowDatasets(false); // reset datasets toggle
//       fetchHistory();
//     } catch (err) {
//       console.error(err);
//     }
//   };

//   const handleExportCSV = async () => {
//     try {
//       const res = await axios.get("http://localhost:5000/export_history", { responseType: "blob" });
//       const url = window.URL.createObjectURL(new Blob([res.data]));
//       const link = document.createElement("a");
//       link.href = url;
//       link.setAttribute("download", "query_history.csv");
//       document.body.appendChild(link);
//       link.click();
//     } catch (err) {
//       console.error(err);
//     }
//   };

//   const handleShowHistory = async () => {
//         setShowHistory(!showHistory);
//         if (!showHistory) {
//           try {
//             const res = await fetch("http://localhost:5000/history");
//             const data = await res.json();
//             setHistory(data.history || []);
//           } catch (err) {
//             console.error("Error fetching history:", err);
//           }
//         }
//       };

//   return (
//     <div className="container mx-auto p-4">
//       <h1 className="text-2xl font-bold mb-4">Query Analyzer</h1>

//       {/* Input */}
//       <div className="mb-4">
//         <input
//           type="text"
//           value={query}
//           onChange={(e) => setQuery(e.target.value)}
//           placeholder="Enter your query..."
//           className="border p-2 w-full"
//         />
//         <button
//           onClick={handleAnalyze}
//           className="bg-blue-500 text-white px-4 py-2 mt-2"
//         >
//           Analyze
//         </button>
//         <button
//           onClick={handleExportCSV}
//           className="bg-green-500 text-white px-4 py-2 mt-2 ml-2"
//         >
//           Export History CSV
//         </button>
//       </div>

//       {/* Result */}
//       {result && (
//         <div className="border p-4 mb-4">
//           <h2 className="font-bold text-xl mb-2">Results</h2>
//           <p><strong>Classification:</strong> {result.classification}</p>
//           <p><strong>Severity:</strong> {result.severity}</p>
//           <p><strong>Explanation:</strong> {result.explanation}</p>
//           <p><strong>Remediation:</strong> {Array.isArray(result.remediation) ? result.remediation.join(", ") : result.remediation}</p>

//           {/* Show datasets button */}
//           {result.datasets && result.datasets.length > 0 && (
//             <>
//               <button
//                 onClick={() => setShowDatasets(!showDatasets)}
//                 className="bg-gray-500 text-white px-3 py-1 mt-2"
//               >
//                 {showDatasets ? "Hide Datasets" : "Show Top Datasets"}
//               </button>
//               {showDatasets && (
//                 <div className="mt-2 border-t pt-2">
//                   {result.datasets.map((ds) => (
//                     <div key={ds.id} className="border p-2 mb-2 rounded">
//                       <p><strong>{ds.title}</strong></p>
//                       <p>{ds.description}</p>
//                     </div>
//                   ))}
//                 </div>
//               )}
//             </>
//           )}
//         </div>
//       )}

//       {/* History */}
//       {/* <div>
//         <h2 className="font-bold text-xl mb-2">History (Last 50 Queries)</h2>
//         <ul>
//           {history.map((h) => (
//             <li key={h.id} className="border p-2 mb-1 rounded">
//               <p><strong>{h.query}</strong> ({h.cvss_score})</p>
//               <p>Classification: {h.classification}</p>
//             </li>
//           ))}
//         </ul>
//       </div> */}

// <button onClick={handleShowHistory}>
// //           {showHistory ? "Hide History" : "Show History"}
// //         </button>
// {showHistory && (
//         <div className="history-box">
//           <h2>Query History</h2>
//           {history.length === 0 ? (
//             <p>No history found</p>
//           ) : (
//             <table className="history-table">
//               <thead>
//                 <tr>
//                   <th>ID</th>
//                   <th>Timestamp</th>
//                   <th>Query</th>
//                   <th>Classification</th>
//                   <th>Score</th>
//                   <th>Dataset</th>
//                   <th>Explanation</th>
//                   <th>Remediation</th>
//                 </tr>
//               </thead>
//               <tbody>
//                 {history.map((item) => (
//                   <tr key={item.id}>
//                     <td>{item.id}</td>
//                     <td>{new Date(item.timestamp).toLocaleString()}</td>
//                     <td>{item.query}</td>
//                     <td>{item.classification}</td>
//                     <td>{item.cvss_score?.toFixed(2)}</td>
//                     <td>{item.dataset_name || "—"}</td>
//                     <td className="wrap-text">{item.explanation || "—"}</td>
//                     <td className="wrap-text">
//                       {Array.isArray(item.remediation)
//                         ? item.remediation.join(", ")
//                         : item.remediation || "—"}
//                     </td>
//                   </tr>
//                 ))}
//               </tbody>
//             </table>
//           )}
//         </div>
//       )}

//     </div>
//   );
// }

// export default App;

// import React, { useState, useEffect } from "react";
// import axios from "axios";
// import "./App.css";

// function App() {
//   const [query, setQuery] = useState("");
//   const [result, setResult] = useState(null);
//   const [history, setHistory] = useState([]);
//   const [showDatasets, setShowDatasets] = useState(false);
//   const [showHistory, setShowHistory] = useState(false);
//   const [loading, setLoading] = useState(false); // Loading state

//   useEffect(() => {
//     fetchHistory();
//   }, []);

//   const fetchHistory = async () => {
//     try {
//       const res = await axios.get("http://localhost:5000/history");
//       setHistory(res.data.history);
//     } catch (err) {
//       console.error(err);
//     }
//   };

//   const handleAnalyze = async () => {
//     if (!query.trim()) return;
//     setLoading(true); // Start loading
//     try {
//       const res = await axios.post("http://localhost:5000/analyze", { query });
//       setResult(res.data);
//       setShowDatasets(false);
//       fetchHistory();
//     } catch (err) {
//       console.error(err);
//     } finally {
//       setLoading(false); // Stop loading
//     }
//   };

//   const handleExportCSV = async () => {
//     try {
//       const res = await axios.get("http://localhost:5000/export_history", { responseType: "blob" });
//       const url = window.URL.createObjectURL(new Blob([res.data]));
//       const link = document.createElement("a");
//       link.href = url;
//       link.setAttribute("download", "query_history.csv");
//       document.body.appendChild(link);
//       link.click();
//     } catch (err) {
//       console.error(err);
//     }
//   };

//   const handleShowHistory = async () => {
//     setShowHistory(!showHistory);
//     if (!showHistory) {
//       try {
//         const res = await fetch("http://localhost:5000/history");
//         const data = await res.json();
//         setHistory(data.history || []);
//       } catch (err) {
//         console.error("Error fetching history:", err);
//       }
//     }
//   };

//   return (
//     <div className="app-container">
//       <h1 className="app-header">Query Analyzer Dashboard</h1>

//       <div className="card input-card">
//         <input
//           type="text"
//           value={query}
//           onChange={(e) => setQuery(e.target.value)}
//           placeholder="Enter your query..."
//         />
//         <div className="button-group">
//           {/* <button onClick={handleAnalyze} disabled={loading}>
//             {loading ? "Analyzing..." : "Analyze"}
//           </button> */}

//           <button onClick={handleAnalyze} disabled={loading} className="analyze-button">
//             {loading ? (
//               <span className="spinner-container">
//                 <span className="spinner"></span> Analyzing...
//               </span>
//             ) : (
//               "Analyze"
//             )}
//           </button>

//           <button onClick={handleExportCSV}>Export History CSV</button>
//           <button onClick={handleShowHistory}>
//             {showHistory ? "Hide History" : "Show History"}
//           </button>
//         </div>
//       </div>

//       {result && (
//         <div className="card result-card">
//           <h2>Analysis Results</h2>
//           <p><strong>Classification:</strong> {result.classification}</p>
//           <p><strong>Severity:</strong> {result.severity}</p>
//           <p><strong>Explanation:</strong> {result.explanation}</p>
//           <p><strong>Remediation:</strong> {Array.isArray(result.remediation) ? result.remediation.join(", ") : result.remediation}</p>

//           {/* {result.datasets && result.datasets.length > 0 && (
//             <div>
//               <button onClick={() => setShowDatasets(!showDatasets)}>
//                 {showDatasets ? "Hide Datasets" : "Show Top Datasets"}
//               </button>
//               {showDatasets && (
//                 <div className="dataset-list">
//                   {result.datasets.map((ds, index) => (
//                     <div key={ds.id} className="dataset-card">
//                       <p className="dataset-title">{index + 1}. {ds.title}</p>
//                       <p className="dataset-description">{ds.description}</p>
//                     </div>
//                   ))}
//                 </div>
//               )}
//             </div>
//           )} */}

// {result.datasets && result.datasets.length > 0 && (
//   <div>
//     <button onClick={() => setShowDatasets(!showDatasets)}>
//       {showDatasets ? "Hide Datasets" : "Show Top Datasets"}
//     </button>

//     {showDatasets && (
//       <div className="table-container">
//         <table className="datasets-table">
//           <thead>
//             <tr>
//               <th>#</th>
//               <th>Title</th>
//               <th>Description</th>
//             </tr>
//           </thead>
//           <tbody>
//             {result.datasets.map((ds, index) => (
//               <tr key={ds.id}>
//                 <td>{index + 1}</td>
//                 <td>{ds.title}</td>
//                 <td>{ds.description}</td>
//               </tr>
//             ))}
//           </tbody>
//         </table>
//       </div>
//     )}
//   </div>
// )}

//         </div>
//       )}

//       {showHistory && (
//         <div className="card history-card">
//           <h2>Query History</h2>
//           {history.length === 0 ? (
//             <p>No history found.</p>
//           ) : (
//             <div className="table-container">
//               <table>
//                 <thead>
//                   <tr>
//                     <th>ID</th>
//                     <th>Timestamp</th>
//                     <th>Query</th>
//                     <th>Classification</th>
//                     <th>Score</th>
//                     <th>Dataset</th>
//                     <th>Explanation</th>
//                     <th>Remediation</th>
//                   </tr>
//                 </thead>
//                 <tbody>
//                   {history.map((item) => (
//                     <tr key={item.id}>
//                       <td>{item.id}</td>
//                       <td>{new Date(item.timestamp).toLocaleString()}</td>
//                       <td>{item.query}</td>
//                       <td>{item.classification}</td>
//                       <td>{item.cvss_score?.toFixed(2)}</td>
//                       <td>{item.dataset_name || "—"}</td>
//                       <td>{item.explanation || "—"}</td>
//                       <td>{Array.isArray(item.remediation) ? item.remediation.join(", ") : item.remediation || "—"}</td>
//                     </tr>
//                   ))}
//                 </tbody>
//               </table>
//             </div>
//           )}
//         </div>
//       )}
//     </div>
//   );
// }

// export default App;



import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [showDatasets, setShowDatasets] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await axios.get("http://localhost:5000/history");
      setHistory(res.data.history);
    } catch (err) {
      console.error(err);
    }
  };

  const handleAnalyze = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const res = await axios.post("http://localhost:5000/analyze", { query });
      setResult(res.data);
      setShowDatasets(false);
      fetchHistory();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleExportCSV = async () => {
    try {
      const res = await axios.get("http://localhost:5000/export_history", { responseType: "blob" });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "query_history.csv");
      document.body.appendChild(link);
      link.click();
    } catch (err) {
      console.error(err);
    }
  };

  const handleShowHistory = async () => {
    setShowHistory(!showHistory);
    if (!showHistory) {
      try {
        const res = await fetch("http://localhost:5000/history");
        const data = await res.json();
        setHistory(data.history || []);
      } catch (err) {
        console.error("Error fetching history:", err);
      }
    }
  };

  return (
    <div className="app-container">
      <h1 className="app-header">MCP-Citadel</h1>

      <div className="card input-card">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter your query..."
        />
        <div className="button-group">
          <button onClick={handleAnalyze} disabled={loading} className="analyze-button">
            {loading ? (
              <span className="spinner-container">
                <span className="spinner"></span> Analyzing...
              </span>
            ) : (
              "Analyze"
            )}
          </button>
          <button onClick={handleExportCSV}>Export History CSV</button>
          <button onClick={handleShowHistory}>
            {showHistory ? "Hide History" : "Show History"}
          </button>
        </div>
      </div>

      {result && (
        <div className="card result-card">
          <h2>Analysis Results</h2>
          <p><strong>Classification:</strong> {result.classification}</p>
          {/* <p><strong>Severity:</strong> {result.severity}</p> */}

          <p><strong>Severity:</strong> {result.severity}</p>
<div className="severity-bar-container">
  <div
    className="severity-bar-fill"
    style={{
      width: `${(result.severity / 10) * 100}%`,
      backgroundColor:
        result.severity <= 3 ? "#4caf50" : // low - green
        result.severity <= 7 ? "#ff9800" : // medium - orange
        "#f44336", // high - red
    }}
  />
</div>


          {/* Formatted Explanation */}
          {/* <p><strong>Explanation:</strong></p>
          {result.explanation.split("\n").map((line, index) => (
            <div key={index}>{line}</div>
          ))} */}

          {/* Formatted Remediation */}
          <p><strong>Remediation:</strong></p>
          {/* {Array.isArray(result.remediation)
            ? result.remediation.map((line, index) => <div key={index}>{line}</div>)
            : result.remediation.split("\n").map((line, index) => <div key={index}>{line}</div>)} */}

            {/* Formatted Explanation */}
<p><strong>Explanation:</strong></p>
<div>
  {result.explanation
    ? Array.isArray(result.explanation)
      ? result.explanation.map((line, index) => <div key={index}>{line}</div>)
      : result.explanation.split(/\r?\n/).map((line, index) => <div key={index}>{line}</div>)
    : "—"}
</div>

{/* Formatted Remediation */}
<p><strong>Remediation:</strong></p>
<div>
  {result.remediation
    ? Array.isArray(result.remediation)
      ? result.remediation.map((line, index) => <div key={index}>{line}</div>)
      : result.remediation.split(/\r?\n/).map((line, index) => <div key={index}>{line}</div>)
    : "—"}
</div>


          {/* Datasets Table */}
          {result.datasets && result.datasets.length > 0 && (
            <div>
              <button onClick={() => setShowDatasets(!showDatasets)}>
                {showDatasets ? "Hide Datasets" : "Show Top Datasets"}
              </button>

              {showDatasets && (
                <div className="table-container">
                  <table className="datasets-table">
                    <thead>
                      <tr>
                        <th>#</th>
                        <th>Title</th>
                        <th>Description</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.datasets.map((ds, index) => (
                        <tr key={ds.id}>
                          <td>{index + 1}</td>
                          <td>{ds.title}</td>
                          <td>{ds.description}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Query History Table */}
      {showHistory && (
        <div className="card history-card">
          <h2>Query History</h2>
          {history.length === 0 ? (
            <p>No history found.</p>
          ) : (
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Timestamp</th>
                    <th>Query</th>
                    <th>Classification</th>
                    <th>Score</th>
                    {/* <th>Dataset</th> */}
                    <th>Explanation</th>
                    <th>Remediation</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((item) => (
                    <tr key={item.id}>
                      <td>{item.id}</td>
                      <td>{new Date(item.timestamp).toLocaleString()}</td>
                      <td>{item.query}</td>
                      <td>{item.classification}</td>
                      <td>{item.cvss_score?.toFixed(2)}</td>
                      {/* <td>{item.dataset_name || "—"}</td> */}
                      <td>
                        {item.explanation
                          ? item.explanation.split("\n").map((line, idx) => <div key={idx}>{line}</div>)
                          : "—"}
                      </td>
                      <td>
                        {item.remediation
                          ? Array.isArray(item.remediation)
                            ? item.remediation.map((line, idx) => <div key={idx}>{line}</div>)
                            : item.remediation.split("\n").map((line, idx) => <div key={idx}>{line}</div>)
                          : "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
