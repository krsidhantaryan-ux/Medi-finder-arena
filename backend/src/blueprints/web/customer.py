"""
Customer Web Portal and Session Management.
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from backend.src.core.database import get_db
from backend.src.core.utils import serialize_doc, to_object_id
from backend.src.services.auth_service import AuthService
from backend.src.services.reservation_service import ReservationService

customer_web = Blueprint("customer_web", __name__, url_prefix="/account")


@customer_web.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            phone = request.form.get("phone", "").strip()
            password = request.form.get("password", "")
            city = request.form.get("city", "Patna").strip()

            result = AuthService.register_customer({
                "name": name,
                "email": email,
                "phone": phone,
                "password": password,
                "city": city,
            })

            user = result["user"]
            session["customer_id"] = user["id"]
            session["customer_name"] = user["name"]
            session["customer_email"] = user["email"]
            flash(f"Welcome to MediFinder, {user['name']}!", "success")
            return redirect(url_for("customer_web.account_dashboard"))
        except Exception as e:
            flash(str(e), "danger")

    return render_template("customer_auth.html", mode="register")


@customer_web.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "")

            result = AuthService.login_customer(email, password)
            user = result["user"]
            session["customer_id"] = user["id"]
            session["customer_name"] = user["name"]
            session["customer_email"] = user["email"]
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for("customer_web.account_dashboard"))
        except Exception as e:
            flash(str(e), "danger")

    return render_template("customer_auth.html", mode="login")


@customer_web.route("/logout")
def logout():
    session.pop("customer_id", None)
    session.pop("customer_name", None)
    session.pop("customer_email", None)
    flash("You have been signed out.", "info")
    return redirect(url_for("public_web.index"))


@customer_web.route("")
def account_dashboard():
    customer_id = session.get("customer_id")
    if not customer_id:
        return redirect(url_for("customer_web.login"))

    db = get_db()
    user = db.users.find_one({"$or": [{"_id": to_object_id(customer_id)}, {"_id": customer_id}]})
    reservations = ReservationService.get_customer_reservations(customer_id)
    favourites = list(db.favourites.find({"user_id": customer_id}))

    return render_template(
        "account.html",
        customer=serialize_doc(user),
        reservations=reservations,
        favourites=serialize_doc(favourites),
    )


@customer_web.route("/reservation/<string:rid>/cancel", methods=["POST"])
def cancel_reservation(rid: str):
    customer_id = session.get("customer_id")
    if not customer_id:
        flash("Please log in to manage your reservations.", "warning")
        return redirect(url_for("customer_web.login"))

    try:
        ReservationService.update_reservation_status(
            reservation_id=rid,
            action="cancel",
            actor_role="customer",
            actor_id=customer_id
        )
        flash("Reservation cancelled successfully.", "info")
    except Exception as e:
        flash(str(e), "danger")

    return redirect(url_for("customer_web.account_dashboard"))
