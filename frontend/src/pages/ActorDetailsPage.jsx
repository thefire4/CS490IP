import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getJSON } from "../api";

export default function ActorDetailsPage() {
  const { actorID } = useParams();
  const [data, setData] = useState(null);

  useEffect(() => {
    async function loadActor() {
      const result = await getJSON(`/actors/${actorID}`);
      setData(result);
    }

    loadActor();
  }, [actorID]);

  if (!data) return <p>Loading...</p>;

  return (
    <div style={{ padding: 20 }}>
      <h1>{data.actor.first_name} {data.actor.last_name}</h1>
      
        <h2>Top 5 Films:</h2>
        {data.films.map((f) => (
          <div key={f.film_id}>{f.title}</div>
        ))}
    </div>
  );
}
