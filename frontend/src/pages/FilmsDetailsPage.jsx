import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getJSON } from "../api";

export default function FilmsDetailsPage() {
  const { filmid } = useParams();
  const [data, setData] = useState(null);

  useEffect(() => {
    async function loadFilm() {
      const result = await getJSON(`/films/${filmid}`);
      setData(result);
    }

    loadFilm();
  }, [filmid]);

  if (!data) return <p>Loading...</p>;

  return (
    <div style={{ padding: 20 }}>
      <h1>{data.film.title}</h1>
      <p>{data.film.description}</p>
      <p>Rating: {data.film.rating}</p>

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
    </div>
  );
}
