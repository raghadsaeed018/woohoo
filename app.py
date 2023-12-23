from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import re

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///woohoo.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of pets the user owns"""
    cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]
    pets = db.execute("""
        SELECT animals.*
        FROM purchases
        JOIN animals ON purchases.animal_id = animals.id
        WHERE purchases.user_id = ? AND animals.category NOT IN (
            SELECT category FROM animals WHERE category IN ('food', 'accessory')
        )
    """, session["user_id"])


    return render_template("index.html", cash=cash, pets=pets)

@app.route("/get_owned_food")
@login_required
def get_owned_food():
    # Retrieve pet details based on the pet_id
    owned_food = db.execute("""
        SELECT animals.*, COUNT(*) as count
        FROM purchases
        JOIN animals ON purchases.animal_id = animals.id
        WHERE purchases.user_id = ? AND animals.category = (
            SELECT category FROM animals WHERE category = 'food'
        )
        GROUP BY animals.id
    """, session["user_id"])

    if owned_food:
        # Extract images and names from the list of dictionaries
        images = [food["image"] for food in owned_food]
        names = [food["name"] for food in owned_food]
        count = [food["count"] for food in owned_food]

        return jsonify({
            "images": images,
            "names": names,
            "count": count
        })
    else:
        return jsonify(None)

@app.route("/pet_action", methods=["POST"])
def pet_action():
    if session["user_id"]:
        # Update the user's cash (add 1 coin)
        result = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])

        if result:
            cash = result[0]["cash"]
            db.execute("UPDATE users SET cash = ? WHERE id = ?", cash + 1, session["user_id"])

            # Query the database again to get the updated cash value
            updated_cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]

            # Return the new cash amount in the response
            return jsonify({"success": True, "newCashAmount": updated_cash})
        else:
            return apology("Error fetching user cash data")

    # Return failure if the user is not found
    return jsonify({"success": False})

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Warning: Must provide username", "login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Warning: Must provide password", "login.html")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("Warning: Invalid username and/or password", "login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        db.execute("UPDATE users SET timestamp = ? WHERE id = ?", datetime.now(), session["user_id"])
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Ensure username was submitted
        password = request.form.get("password")

        if not request.form.get("username"):
            return apology("Warning: Must provide username", "register.html")

        # Ensure password was submitted
        elif not password:
            return apology("Warning: Must provide password", "register.html")

        elif not (
            len(password) >= 6
            and any(char.isdigit() for char in password)
            and any(char.isalpha() for char in password)
            and any(char.isupper() for char in password)
            and not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)
        ):
            return apology(
                "Warning: Password must be at least 6 characters long, "
                "include a number, a letter, and a capital letter, and exclude symbols",
                "register.html"
            )

        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("Warning: Must confirm password", "register.html")

        # Ensure confirmation matches password
        elif request.form.get("confirmation") != password:
            return apology("Warning: Passwords dont match", "register.html")

        elif db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        ):
            return apology("Warning: Username taken", "register.html")

        phash = generate_password_hash(password)

        user = db.execute(
            "INSERT INTO users (username, hash, timestamp) VALUES (?,?,?)",
            request.form.get("username"),
            phash,
            datetime.now(),
        )

        session["user_id"] = user
        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/shop", methods=["GET", "POST"])
@login_required
def shop():
    """Allow user to buy new pets/accessories/pet food"""
    if request.method == "POST":
        animal_id = request.form.get("animal_id")

        result = db.execute("SELECT price FROM animals WHERE id = ?", animal_id)[0]
        
        if result:
            animal_price = result["price"]
            cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]
            if cash >= animal_price:
                db.execute("INSERT INTO purchases (user_id, animal_id, price) VALUES (?, ?, ?)",
                        session["user_id"], animal_id, animal_price)
                
                db.execute("UPDATE users SET cash = ? WHERE id = ?", cash - animal_price, session["user_id"])
                return redirect("/")
            else:
                flash("Cannot afford pet")
                return redirect("/shop")
        else:
            flash("Invalid pet")
            return redirect("/shop")

    else:
        def user_owns_pet(id):
            return bool(db.execute("SELECT id FROM purchases WHERE user_id = ? AND animal_id = ?", session["user_id"], id))
        
        categories = [
            {"name": "Elegant"},
            {"name": "Goofball"},
            {"name": "Adventurous"},
            {"name": "Noodle-brain"},
            {"name": "Mischievous"},
            {"name": "Food"},
            {"name": "Accessory"}
        ]

        cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]
        animals = db.execute("SELECT * FROM animals ORDER BY price")
        return render_template("shop.html", animals=animals, categories=categories, user_owns_pet=user_owns_pet, cash=cash)


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Allow user to sell his owned pets and accessories"""
    if request.method == "POST":
        animal_id = request.form.get("animal_id")

        result = db.execute("SELECT animal_id FROM purchases WHERE user_id = ? AND animal_id = ?", session["user_id"], animal_id)

        if result:
            result = result[0]
            animal_price = db.execute("SELECT price FROM purchases WHERE user_id = ? AND animal_id = ?", session["user_id"], animal_id)[0]

            if animal_price:
                cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]

                if cash:
                    db.execute("UPDATE users SET cash = ? WHERE id = ?", cash["cash"] + animal_price["price"], session["user_id"])
                    db.execute("DELETE FROM purchases WHERE user_id = ? AND animal_id = ?", session["user_id"], animal_id)
                    return redirect("/")
                else:
                    flash("Error fetching user's cash")
                    return redirect("/sell")
            else:
                flash("Error fetching pet's price")
                return redirect("/sell")
        else:
            flash("Invalid pet")
            return redirect("/sell")
        
    else:
        cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]
        pets = db.execute("""
            SELECT animals.*
            FROM purchases
            JOIN animals ON purchases.animal_id = animals.id
            WHERE purchases.user_id = ? AND animals.category NOT IN (
                SELECT category FROM animals WHERE category IN ('food', 'accessory')
            )
        """, session["user_id"])
        return render_template("sell.html", pets=pets, cash=cash)


@app.route("/get_pet_details/<int:pet_id>")
@login_required
def get_pet_details(pet_id):
    # Retrieve pet details based on the pet_id
    pet_details = db.execute("SELECT * FROM animals WHERE id = ?", pet_id)[0]

    if pet_details:
        return jsonify({
            "image": pet_details["image"],
            "name": pet_details["name"],
            "description": pet_details["description"],
            "price": pet_details["price"],
            "category": pet_details["category"]
        })
    else:
        return jsonify(None)

@app.route("/inventory")
@login_required
def inventory():
    """Display accessories/pet food the user owns"""
    cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]
    items = db.execute("""
        SELECT animals.*, COUNT(*) as count
        FROM purchases
        JOIN animals ON purchases.animal_id = animals.id
        WHERE purchases.user_id = ? AND animals.category IN (
            SELECT category FROM animals WHERE category IN ('food', 'accessory')
        )
        GROUP BY animals.id
    """, session["user_id"])

    return render_template("inventory.html", cash=cash, items=items)


if __name__ == '__main__':
    app.run(debug=True)
