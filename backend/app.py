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

# Test route
@app.route("/api/health")
def health():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT 1")
    result = cur.fetchone()
    cur.close()
    conn.close()
    return jsonify({"status": "ok", "db": result[0]})

# Feature 1: Top 5 films
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

#Feature 2: Top 5 actors
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

    cur.close()
    conn.close()

    if film:
        return jsonify({
            "film": film,
            "actors": actors,
            "categories": categories
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





if __name__ == "__main__":
    app.run(debug=True)
