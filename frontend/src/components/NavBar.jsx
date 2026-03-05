import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        right: 0,
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

      <Link to="/customers" style={{ color: "white", textDecoration: "none" }}>
        Customers
      </Link>
    </div>
  );
}