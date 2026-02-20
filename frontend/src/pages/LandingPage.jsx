import { useEffect, useState } from "react";
import { getJSON } from "../api";
import {Link} from "react-router-dom";

export default function App() {
  const [films, setFilms] = useState([]);
  const [actors, setActors] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadTopFilms() {
      try {
        const data = await getJSON("/landing/top-films");
        setFilms(data);
        const actorsData = await getJSON("/landing/top-actors");
        setActors(actorsData);
      } catch (e) {
        setError(e.message);
      }
    }

    loadTopFilms();
  }, []);

  return (
    <div style={{ padding: 20, maxWidth: 600, margin: "0 auto", textAlign: "center" }}>
      <title>Movie Store</title>
      <h1>Top 5 Rented Films</h1>
      {films.map((f) => (
        <div key={f.film_id}>
            <Link to={`/films/${f.film_id}`} style={{ textDecoration: "none", color: "white" }}>
          <b>{f.title}</b> — rentals: {f.rental_count}
            </Link>
        </div>
        
      ))}
      <h1>Top 5 Actors</h1>
      {actors.map((a) => (
      <div key={a.actorID}>
        <Link to={`/actors/${a.actorID}`} style={{ color: "white", textDecoration: "none" }}>
          <b>{a.first_name} {a.last_name}</b>
        </Link>
      {" — films: "}{a.NumberOfFilms}
    </div>
))}

    </div>
  );
}
