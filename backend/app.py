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


@app.route("/api/health")
def health():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT 1")
    result = cur.fetchone()
    cur.close()
    conn.close()
    return jsonify({"status": "ok", "db": result[0]})

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


    if film is None:
        cur.close()
        conn.close()
        return jsonify({"error": "Film not found"}), 404
    
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

    if film:
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
    else:
        return jsonify({"error": "Film not found"}), 404
    
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

    if actor is None:
        cur.close()
        conn.close()
        return jsonify({"error": "Actor not found"}), 404
    
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

    if actor:
        return jsonify({
            "actor": actor,
            "films": films
        })
    else:
        return jsonify({"error": "Actor not found"}), 404

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

    # 1) does the film exist?
    cur.execute("""
        select film_id, title
        from film
        where film_id = %s
    """, (film_id,))
    film = cur.fetchone()
    if film is None:
        cur.close(); conn.close()
        return jsonify({"error": "film not found"}), 404

    # 2) does the customer exist?
    cur.execute("""
        select customer_id
        from customer
        where customer_id = %s
    """, (customer_id,))
    cust = cur.fetchone()
    if cust is None:
        cur.close(); conn.close()
        return jsonify({"error": "customer not found"}), 404

    # 3) find one available inventory copy (not currently rented out)
    cur.execute("""
        select i.inventory_id
        from inventory i
        left join rental r
            on r.inventory_id = i.inventory_id
            and r.return_date is null
        where i.film_id = %s
          and r.rental_id is null
        order by i.inventory_id
        limit 1
    """, (film_id,))
    inv = cur.fetchone()

    if inv is None:
        cur.close(); conn.close()
        return jsonify({"error": "no copies available"}), 409

    inventory_id = inv["inventory_id"]

    # 4) create the rental
    # NOTE: staff_id is required in sakila.rental; use 1 unless your project says otherwise
    cur.execute("""
        insert into rental (rental_date, inventory_id, customer_id, staff_id)
        values (now(), %s, %s, 1)
    """, (inventory_id, customer_id))
    conn.commit()

    rental_id = cur.lastrowid

    cur.close()
    conn.close()

    return jsonify({
        "message": "rented",
        "film_id": film_id,
        "inventory_id": inventory_id,
        "rental_id": rental_id
    }), 201



if __name__ == "__main__":
    app.run(debug=True)
