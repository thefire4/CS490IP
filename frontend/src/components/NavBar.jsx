import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <div
      style={{
        position: "absolute", // Ensures the navbar is positioned relative to the viewport
        top: 0, // Aligns the navbar to the top
        right: 0, // Aligns the navbar to the right
        display: "flex",
        justifyContent: "flex-end",
        padding: 20,
        gap: 20,
        fontFamily: "Arial",
      }}
    >
      <Link to="/films-search" style={{ color: "white" }}>Search</Link>

      <Link to="/" style={{ color: "white", textDecoration: "none" }}>
        Home
      </Link>
    </div>
  );
}