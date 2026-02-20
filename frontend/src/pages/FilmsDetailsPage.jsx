import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getJSON } from "../api";

export default function FilmsDetailsPage() {
  const { filmid } = useParams();

  const [data, setData] = useState(null);

  // rent ui
  const [customerId, setCustomerId] = useState("");
  const [rentMsg, setRentMsg] = useState("");
  const [renting, setRenting] = useState(false);

  async function loadFilm() {
    const result = await getJSON(`/films/${filmid}`);
    setData(result);
  }

  useEffect(() => {
    loadFilm();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filmid]);

  async function rentFilm() {
    const cid = Number(customerId);

    if (!cid || Number.isNaN(cid)) {
      setRentMsg("❌ enter a valid customer id");
      return;
    }

    try {
      setRenting(true);
      setRentMsg("");

      const res = await fetch(`http://127.0.0.1:5000/api/films/${filmid}/rent`, {
        method: "post",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ customer_id: cid }),
      });

      const payload = await res.json();

      if (!res.ok) {
        throw new Error(payload.error || `rent failed (${res.status})`);
      }

      setRentMsg(`✅ rented! inventory copy: ${payload.inventory_id}`);

      // refresh film details so inventory counts update
      await loadFilm();
    } catch (e) {
      setRentMsg("❌ " + String(e.message || e));
    } finally {
      setRenting(false);
    }
  }

  if (!data) return <p>Loading...</p>;

  return (
    <div style={{ padding: 20 }}>
      <h1>{data.film.title}</h1>
      <p>{data.film.description}</p>
      <p>Rating: {data.film.rating}</p>

      <h2>Special Features</h2>
      <p>
        {data.film.special_features && data.film.special_features.length
          ? data.film.special_features.join(", ")
          : "none"}
      </p>

      <h2>Categories</h2>
      {data.categories.map((c) => (
        <div key={c.category_id}>{c.name}</div>
      ))}

      <h2>Actors</h2>
      {data.actors.map((a) => (
        <div key={a.actor_id}>
          {a.first_name} {a.last_name}
        </div>
      ))}

      <h2>Inventory</h2>
      <p>Total copies: {data.stock.total_copies}</p>
      <p>Available copies: {data.stock.available_copies}</p>

      <hr style={{ margin: "20px 0" }} />

      <h2>Rent this film</h2>
      <input
        type="number"
        value={customerId}
        onChange={(e) => setCustomerId(e.target.value)}
        placeholder="enter customer id"
        style={{ padding: 8, width: 220, marginRight: 10 }}
      />

      <button onClick={rentFilm} disabled={renting}>
        {renting ? "renting..." : "rent film"}
      </button>

      {rentMsg && <p style={{ marginTop: 10 }}>{rentMsg}</p>}
    </div>
  );
}