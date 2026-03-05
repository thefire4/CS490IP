import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getJSON } from "../api";

const emptyForm = { first_name: "", last_name: "", email: "", active: 1 };

export default function CustomersPage() {
  const [q, setQ] = useState("");
  const [page, setPage] = useState(1);
  const [data, setData] = useState({ customers: [], total: 0, limit: 20 });
  const [loading, setLoading] = useState(false);

  const [showAdd, setShowAdd] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);

  async function loadCustomers(pageNum = page, query = q) {
    setLoading(true);
    const params = new URLSearchParams({ page: pageNum, q: query.trim() });
    const result = await getJSON(`/customers?${params}`);
    setData(result);
    setLoading(false);
  }

  useEffect(() => {
    const t = setTimeout(() => {
      setPage(1);
      loadCustomers(1, q);
    }, 400);
    return () => clearTimeout(t);
  }, [q]);

  useEffect(() => {
    loadCustomers(page, q);
  }, [page]);

  function handleFormChange(e) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function addCustomer() {
    setSaving(true);
    const res = await fetch(`http://127.0.0.1:5000/api/customers`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ ...form, active: Number(form.active) }),
    });
    const payload = await res.json();
    setForm(emptyForm);
    setShowAdd(false);
    await loadCustomers(1, q);
    setSaving(false);
  }

  const totalPages = Math.ceil(data.total / data.limit);

  return (
    <div style={{ padding: 20, maxWidth: 600, margin: "0 auto", textAlign: "center" }}>
      <h1>Customers</h1>

      <input
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder="Search by ID, first name, or last name..."
        style={{ padding: 10, width: 360 }}
      />

      <div style={{ marginTop: 12 }}>
        <button onClick={() => { setShowAdd((v) => !v); }}>
          {showAdd ? "cancel" : "+ add customer"}
        </button>
      </div>

      {showAdd && (
        <div style={{ marginTop: 16, border: "1px solid #444", borderRadius: 8, padding: 16 }}>
          <h3 style={{ marginTop: 0 }}>New Customer</h3>

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

          <button onClick={addCustomer} disabled={saving}>
            {saving ? "saving..." : "save customer"}
          </button>
        </div>
      )}

      {loading && <p>Loading...</p>}

      <div style={{ marginTop: 20 }}>
        {data.customers.map((c) => (
          <div key={c.customer_id} style={{ marginBottom: 8 }}>
            <Link to={`/customers/${c.customer_id}`} style={{ color: "white" }}>
              <b>{c.first_name} {c.last_name}</b>
            </Link>
            {" — "}ID: {c.customer_id}
            {" — "}
            <span style={{ color: c.active ? "#4caf50" : "#f44336" }}>
              {c.active ? "active" : "inactive"}
            </span>
          </div>
        ))}
      </div>

      {totalPages > 1 && (
        <div style={{ marginTop: 20, display: "flex", justifyContent: "center", gap: 8 }}>
          <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1}>
            prev
          </button>
          <span style={{ padding: "6px 10px" }}>
            page {page} of {totalPages}
          </span>
          <button onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page === totalPages}>
            next
          </button>
        </div>
      )}
    </div>
  );
}