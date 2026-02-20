import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getJSON } from "../api";

export default function FilmsPage() {
  const [q, setQ] = useState("");
  const [results, setResults] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function runSearch() {
      // if the box is empty, clear results
      if (!q.trim()) {
        setResults([]);
        setError("");
        return;
      }

      try {
        setLoading(true);
        setError("");

        // IMPORTANT: no /api here
        const data = await getJSON(`/films/search?q=${encodeURIComponent(q)}`);
        setResults(data);
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    }

    runSearch();
  }, [q]);

  return (
    <div style={{ padding: 20 }}>
      <h1>film search</h1>

      <input
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder="search by film title, actor name, or genre..."
        style={{ padding: 10, width: 400 }}
      />

      {loading && <p>loading...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      <div style={{ marginTop: 20 }}>
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
