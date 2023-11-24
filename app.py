from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

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
    return render_template("index.html")


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
        if not request.form.get("username"):
            return apology("Warning: Must provide username", "register.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Warning: Must provide password", "register.html")

        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("Warning: Must confirm password", "register.html")

        # Ensure confirmation matches password
        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("Warning: Passwords dont match", "register.html")

        elif db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        ):
            return apology("Warning: Username taken", "register.html")

        phash = generate_password_hash(request.form.get("password"))

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
    if request.method == "GET":
        return render_template("shop.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Allow user to sell his owned pets and accessories"""
    if request.method == "GET":
        return render_template("sell.html")


@app.route("/inventory")
@login_required
def inventory():
    """Display accessories/pet food the user owns"""
    return render_template("inventory.html")


if __name__ == '__main__':
    app.run(debug=True)
