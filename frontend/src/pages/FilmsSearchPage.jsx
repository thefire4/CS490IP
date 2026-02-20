import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getJSON } from "../api";

export default function FilmsSearchPage() {
  const [q, setQ] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
  const trimmed = q.trim();

  if (!trimmed) {
    setResults([]);
    setError("");
    setLoading(false);
    return;
  }

  setLoading(true);

  const t = setTimeout(() => {
    (async () => {
      try {
        setError("");
        const data = await getJSON(
          `/films/search?q=${encodeURIComponent(trimmed)}`
        );
        setResults(data);
      } catch (e) {
        setError(String(e.message || e));
        setResults([]);
      } finally {
        setLoading(false);
      }
    })();
  }, 400);

  return () => clearTimeout(t);
}, [q]);

  return (
    <div style={{ padding: 20, maxWidth: 600, margin: "0 auto", textAlign: "center" }}>
      <h1>Search</h1>

      <input
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder="Search by film title, actor name, or genre..."
        style={{ padding: 10, width: 420 }}
      />

      {loading && <p>Loading...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      <div style={{ padding: 20, maxWidth: 600, margin: "0 auto", textAlign: "center" }}>
        {results.map((f) => (
          <div key={f.film_id} style={{ marginBottom: 8 }}>
            <Link to={`/films/${f.film_id}`} style={{ color: "white" }}>
              <b>{f.title}</b>
            </Link>
            {" — "}
            {f.rating} {" — "}
            ${f.rental_rate}
          </div>
        ))}
      </div>
    </div>
  );
}
