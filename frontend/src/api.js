const API_BASE = "http://127.0.0.1:5000/api";

export async function getJSON(path) {
  const res = await fetch(API_BASE + path);

  if (!res.ok) {
    throw new Error(`API request failed: ${res.status}`);
  }

  return res.json();
}
