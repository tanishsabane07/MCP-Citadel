import React, { useEffect, useState } from "react";
import axios from "axios";

const API_BASE = "http://localhost:5000/api";

function QueryHistory() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchLogs = async () => {
    try {
      const res = await axios.get(`${API_BASE}/logs`);
      setLogs(res.data.logs || []);
    } catch (err) {
      console.error("Error fetching logs:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  if (loading) return <p className="text-gray-400">Loading recent queries...</p>;

  return (
    <div className="bg-gray-900 p-4 rounded-2xl shadow-md border border-gray-800 mt-4">
      <h2 className="text-xl font-semibold text-blue-400 mb-3">
        🕒 Recent Query History
      </h2>

      {logs.length === 0 ? (
        <p className="text-gray-400">No logs yet. Run a query to get started!</p>
      ) : (
        <div className="space-y-3">
          {logs.map((log) => (
            <div
              key={log.id}
              className="p-3 bg-gray-800 rounded-xl hover:bg-gray-700 transition"
            >
              <p className="text-white font-medium">{log.user_query}</p>
              <p className="text-sm text-gray-400">{log.result_summary}</p>
              <p className="text-xs text-gray-500">{log.timestamp}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default QueryHistory;
