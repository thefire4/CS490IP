import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Link } from "react-router-dom";
import { getJSON } from "../api";

export default function CustomerDetailsPage() {
  const { customerID } = useParams();
  const navigate = useNavigate();

  const [data, setData] = useState(null);

  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({ first_name: "", last_name: "", email: "", active: 1 });
  const [saving, setSaving] = useState(false);

  const [returningId, setReturningId] = useState(null);

  async function loadCustomer() {
    const result = await getJSON(`/customers/${customerID}`);
    setData(result);
    setForm({
      first_name: result.customer.first_name,
      last_name: result.customer.last_name,
      email: result.customer.email || "",
      active: result.customer.active,
    });
  }

  useEffect(() => {
    loadCustomer();
  }, [customerID]);

  function handleFormChange(e) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function saveEdit() {
    setSaving(true);
    const res = await fetch(`http://127.0.0.1:5000/api/customers/${customerID}`, {
      method: "PUT",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ ...form, active: Number(form.active) }),
    });
    setSaving(false);
    setEditing(false);
    await loadCustomer();
  }

  async function deleteCustomer() {
    if (!window.confirm("Are you sure you want to delete this customer?")) return;
    await fetch(`http://127.0.0.1:5000/api/customers/${customerID}`, { method: "DELETE" });
    navigate("/customers");
  }

  async function returnRental(rentalId) {
    setReturningId(rentalId);
    await fetch(`http://127.0.0.1:5000/api/rentals/${rentalId}/return`, { method: "POST" });
    setReturningId(null);
    await loadCustomer();
  }

  function formatDate(dateStr) {
    if (!dateStr) return "—";
    return new Date(dateStr).toLocaleDateString();
  }

  if (!data) return <p>Loading...</p>;

  const { customer, rentals } = data;
  const activeRentals = rentals.filter((r) => !r.return_date);
  const pastRentals = rentals.filter((r) => r.return_date);

  return (
    <div style={{ padding: 20, maxWidth: 600, margin: "0 auto", textAlign: "center" }}>
      <h1>{customer.first_name} {customer.last_name}</h1>
      <p>Customer ID: {customer.customer_id}</p>
      <p>Email: {customer.email || "—"}</p>
      <p>
        Status:{" "}
        <span style={{ color: customer.active ? "#4caf50" : "#f44336" }}>
          {customer.active ? "active" : "inactive"}
        </span>
      </p>

      <div style={{ marginTop: 12, display: "flex", justifyContent: "center", gap: 10 }}>
        <button onClick={() => setEditing((v) => !v)}>
          {editing ? "cancel edit" : "edit customer"}
        </button>
        <button onClick={deleteCustomer} style={{ color: "#f44336" }}>
          delete customer
        </button>
      </div>

      {editing && (
        <div style={{ marginTop: 16, border: "1px solid #444", borderRadius: 8, padding: 16 }}>
          <h3 style={{ marginTop: 0 }}>Edit Customer</h3>

          {["first_name", "last_name", "email"].map((field) => (
            <div key={field} style={{ marginBottom: 8 }}>
              <input
                name={field}
                value={form[field]}
                onChange={handleFormChange}
                placeholder={field.replace("_", " ")}
                style={{ padding: 8, width: 260 }}
              />
            </div>
          ))}

          <div style={{ marginBottom: 8 }}>
            <label style={{ marginRight: 8 }}>Active:</label>
            <select name="active" value={form.active} onChange={handleFormChange} style={{ padding: 8 }}>
              <option value={1}>Yes</option>
              <option value={0}>No</option>
            </select>
          </div>

          <button onClick={saveEdit} disabled={saving}>
            {saving ? "saving..." : "save changes"}
          </button>
        </div>
      )}

      <hr style={{ margin: "24px 0" }} />

      <h2>Current Rentals ({activeRentals.length})</h2>

      {activeRentals.length === 0 ? (
        <p>No active rentals.</p>
      ) : (
        activeRentals.map((r) => (
          <div key={r.rental_id} style={{ marginBottom: 10 }}>
            <Link to={`/films/${r.film_id}`} style={{ color: "white" }}>
              <b>{r.title}</b>
            </Link>
            {" — rented: "}{formatDate(r.rental_date)}
            {" "}
            <button
              onClick={() => returnRental(r.rental_id)}
              disabled={returningId === r.rental_id}
              style={{ marginLeft: 8, fontSize: "0.85em", padding: "4px 10px" }}
            >
              {returningId === r.rental_id ? "returning..." : "mark returned"}
            </button>
          </div>
        ))
      )}

      <h2>Rental History ({pastRentals.length})</h2>

      {pastRentals.length === 0 ? (
        <p>No past rentals.</p>
      ) : (
        pastRentals.map((r) => (
          <div key={r.rental_id} style={{ marginBottom: 6 }}>
            <Link to={`/films/${r.film_id}`} style={{ color: "white" }}>
              <b>{r.title}</b>
            </Link>
            {" — rented: "}{formatDate(r.rental_date)}
            {" — returned: "}{formatDate(r.return_date)}
          </div>
        ))
      )}
    </div>
  );
}