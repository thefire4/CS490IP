from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

def get_conn():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


@app.route("/api/landing/top-films")
def top_films():
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT f.film_id, f.title, COUNT(r.rental_id) AS rental_count
        FROM film f
        JOIN inventory i ON i.film_id = f.film_id
        JOIN rental r ON r.inventory_id = i.inventory_id
        GROUP BY f.film_id, f.title
        ORDER BY rental_count DESC
        LIMIT 5;
    """)

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify(rows)

@app.route("/api/landing/top-actors")
def top_actors():
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        select 
            a.actor_id as actorID,
            a.last_name as last_name,
            a.first_name as first_name,
            count(fa.film_id) as NumberOfFilms
        from sakila.actor a
        join sakila.film_actor fa
            on a.actor_id = fa.actor_id 
        group by
            a.actor_id, a.last_name, a.first_name
        order by 
            NumberOfFilms desc
        limit 5;
                """)
    
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify(rows)

@app.route("/api/films/<int:film_id>")
def film_details(film_id):
    conn = get_conn()
    cur = conn.cursor(dictionary=True, buffered=True)

    cur.execute("""
        select *
                from film
                where film_id = %s;
    """, (film_id,))
    film = cur.fetchone()

    if isinstance(film.get("special_features"), set):
        film["special_features"] = list(film["special_features"])

    cur.execute("""
                select a.actor_id, a.first_name, a.last_name
                from actor a
                join film_actor fa on a.actor_id = fa.actor_id
                where fa.film_id = %s
                order by a.last_name, a.first_name;
                """, (film_id,))
    actors = cur.fetchall()

    cur.execute("""
            select c.category_id, c.name
            from category c
            join film_category fc on c.category_id = fc.category_id
            where fc.film_id = %s
            order by c.name;    
    """, (film_id,))
    categories = cur.fetchall()

    cur.execute("""
        select
        count(i.inventory_id) as total_copies,
        sum(case when r.return_date is null and r.rental_id is not null then 1 else 0 end) as rented_out
        from inventory i
        left join rental r
        on r.inventory_id = i.inventory_id
        and r.return_date is null
        where i.film_id = %s;
    """, (film_id,))
    stock = cur.fetchone()

    total = stock["total_copies"] or 0
    rented_out = stock["rented_out"] or 0
    available = total - rented_out

    cur.close()
    conn.close()

   
    return jsonify({
    "film": film,
    "actors": actors,
    "categories": categories,
    "stock": {
        "total_copies": total,
        "rented_out": rented_out,
        "available_copies": available
    }
})

    
@app.route("/api/actors/<int:actor_id>")
def actor_details(actor_id):
    conn = get_conn()
    cur = conn.cursor(dictionary=True, buffered=True)

    cur.execute("""
        select *
                from actor
                where actor_id = %s;
    """, (actor_id,))
    actor = cur.fetchone()

    
    cur.execute("""
                select f.film_id, f.title, count(r.rental_id) as rental_count
                from film_actor fa
                join film f on f.film_id = fa.film_id
                join inventory i on i.film_id = f.film_id
                join rental r on r.inventory_id = i.inventory_id
                where fa.actor_id = %s
                group by f.film_id, f.title
                order by rental_count desc
                limit 5;
                """, (actor_id,))
    films = cur.fetchall()

    cur.close()
    conn.close()

 
    return jsonify({
        "actor": actor,
        "films": films
        })
    
@app.route("/api/films/search")
def search_films():
    q = request.args.get("q", "").strip()

    if not q:
        return jsonify([])

    term = f"%{q}%"

    conn = get_conn()
    cur = conn.cursor(dictionary=True, buffered=True)

    cur.execute("""
        select distinct
            f.film_id,
            f.title,
            f.release_year,
            f.rating,
            f.rental_rate
        from film f
        left join film_actor fa on fa.film_id = f.film_id
        left join actor a on a.actor_id = fa.actor_id
        left join film_category fc on fc.film_id = f.film_id
        left join category c on c.category_id = fc.category_id
        where
            f.title like %s
            or concat(a.first_name, ' ', a.last_name) like %s
            or c.name like %s
        order by f.title
        limit 50;
    """, (term, term, term))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify(rows)

@app.route("/api/films/<int:film_id>/rent", methods=["POST"])
def rent_film(film_id):
    body = request.get_json(silent=True) or {}
    customer_id = body.get("customer_id")

    if not customer_id:
        return jsonify({"error": "customer_id is required"}), 400

    conn = get_conn()
    cur = conn.cursor(dictionary=True, buffered=True)

    try:
        cur.execute("""
            SELECT customer_id FROM customer
            WHERE customer_id = %s;
        """, (customer_id,))
        if cur.fetchone() is None:
            return jsonify({"error": "customer not found"}), 404

        cur.execute("""
            SELECT i.inventory_id
            FROM inventory i
            LEFT JOIN rental r
              ON r.inventory_id = i.inventory_id
             AND r.return_date IS NULL
            WHERE i.film_id = %s
              AND r.rental_id IS NULL
            LIMIT 1;
        """, (film_id,))
        inv = cur.fetchone()

        if inv is None:
            return jsonify({"error": "no copies available"}), 409

        cur.execute("""
            INSERT INTO rental (rental_date, inventory_id, customer_id, staff_id)
            VALUES (now(), %s, %s, 1);
        """, (inv["inventory_id"], customer_id))

        conn.commit()

        return jsonify({
            "status": "ok",
            "film_id": film_id,
            "customer_id": customer_id,
            "inventory_id": inv["inventory_id"]
        }), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()


@app.route("/api/customers")
def list_customers():
    q = request.args.get("q", "").strip()
    page = max(1, int(request.args.get("page", 1)))
    limit = 20
    offset = (page - 1) * limit

    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    filters = []
    params = []

    if q:
        try:
            cid = int(q)
            filters.append("c.customer_id = %s")
            params.append(cid)
        except ValueError:
            term = f"%{q}%"
            filters.append("(c.first_name LIKE %s OR c.last_name LIKE %s)")
            params.extend([term, term])

    where = f"WHERE {' AND '.join(filters)}" if filters else ""

    cur.execute(f"""
        SELECT c.customer_id, c.first_name, c.last_name, c.email, c.active
        FROM customer c
        {where}
        ORDER BY c.last_name, c.first_name
        LIMIT %s OFFSET %s;
    """, (*params, limit, offset))
    rows = cur.fetchall()

    cur.execute(f"SELECT COUNT(*) as total FROM customer c {where};", params)
    total = cur.fetchone()["total"]

    cur.close()
    conn.close()

    return jsonify({"customers": rows, "total": total, "page": page, "limit": limit})


@app.route("/api/customers/<int:customer_id>")
def customer_details(customer_id):
    conn = get_conn()
    cur = conn.cursor(dictionary=True, buffered=True)

    cur.execute("SELECT * FROM customer WHERE customer_id = %s;", (customer_id,))
    customer = cur.fetchone()

    if not customer:
        cur.close()
        conn.close()
        return jsonify({"error": "customer not found"}), 404

    cur.execute("""
        SELECT r.rental_id, f.film_id, f.title, r.rental_date, r.return_date,
               i.inventory_id
        FROM rental r
        JOIN inventory i ON i.inventory_id = r.inventory_id
        JOIN film f ON f.film_id = i.film_id
        WHERE r.customer_id = %s
        ORDER BY r.rental_date DESC;
    """, (customer_id,))
    rentals = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify({"customer": customer, "rentals": rentals})


@app.route("/api/customers", methods=["POST"])
def add_customer():
    body = request.get_json(silent=True) or {}
    first_name = body.get("first_name", "").strip()
    last_name = body.get("last_name", "").strip()
    email = body.get("email", "").strip()
    active = int(body.get("active", 1))

    if not first_name or not last_name:
        return jsonify({"error": "first_name and last_name are required"}), 400

    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    try:
        cur.execute("""
            INSERT INTO customer (store_id, first_name, last_name, email, address_id, active)
            VALUES (1, %s, %s, %s, 1, %s);
        """, (first_name, last_name, email or None, active))
        conn.commit()
        new_id = cur.lastrowid
        return jsonify({"status": "ok", "customer_id": new_id}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()


@app.route("/api/customers/<int:customer_id>", methods=["PUT"])
def update_customer(customer_id):
    body = request.get_json(silent=True) or {}
    first_name = body.get("first_name", "").strip()
    last_name = body.get("last_name", "").strip()
    email = body.get("email", "").strip()
    active = int(body.get("active", 1))

    if not first_name or not last_name:
        return jsonify({"error": "first_name and last_name are required"}), 400

    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    try:
        cur.execute("""
            UPDATE customer
            SET first_name = %s, last_name = %s, email = %s, active = %s
            WHERE customer_id = %s;
        """, (first_name, last_name, email or None, active, customer_id))
        conn.commit()
        return jsonify({"status": "ok"})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()


@app.route("/api/customers/<int:customer_id>", methods=["DELETE"])
def delete_customer(customer_id):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    try:
        cur.execute("DELETE FROM payment WHERE customer_id = %s;", (customer_id,))
        cur.execute("DELETE FROM rental WHERE customer_id = %s;", (customer_id,))
        cur.execute("DELETE FROM customer WHERE customer_id = %s;", (customer_id,))
        conn.commit()
        return jsonify({"status": "ok"})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()



@app.route("/api/rentals/<int:rental_id>/return", methods=["POST"])
def return_rental(rental_id):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    try:
        cur.execute("""
            UPDATE rental SET return_date = NOW()
            WHERE rental_id = %s AND return_date IS NULL;
        """, (rental_id,))
        conn.commit()

        if cur.rowcount == 0:
            return jsonify({"error": "rental not found or already returned"}), 404

        return jsonify({"status": "ok"})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    app.run(debug=True)
