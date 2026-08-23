"""
Pharmacy Portal Web Routes:
- Shop registration with license uploads
- Shop login & session
- Pharmacy dashboard (real-time inventory CRUD, reservation management pipeline, status filter)
- Shop settings / profile updates
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from backend.src.core.database import get_db
from backend.src.core.utils import serialize_doc, save_uploaded_file, to_object_id
from backend.src.models.category import CATEGORIES
from backend.src.services.auth_service import AuthService
from backend.src.services.pharmacy_service import PharmacyService
from backend.src.services.reservation_service import ReservationService

pharmacy_web = Blueprint("pharmacy_web", __name__, url_prefix="/pharmacy")


@pharmacy_web.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            form = request.form
            files = {}
            if "license_image" in request.files:
                img_name = save_uploaded_file(request.files["license_image"])
                if img_name:
                    files["license_image"] = img_name

            if "gst_certificate" in request.files:
                gst_name = save_uploaded_file(request.files["gst_certificate"])
                if gst_name:
                    files["gst_certificate"] = gst_name

            if "shop_photo" in request.files:
                photo_name = save_uploaded_file(request.files["shop_photo"])
                if photo_name:
                    files["shop_photo"] = photo_name

            payload = {
                "name": form.get("name", "").strip(),
                "email": form.get("email", "").strip(),
                "phone": form.get("phone", "").strip(),
                "password": form.get("password", ""),
                "owner_name": form.get("owner_name", "").strip(),
                "license_number": form.get("license_number", "").strip(),
                "address": form.get("address", "").strip(),
                "city": form.get("city", "Patna").strip(),
                "state": form.get("state", "Bihar").strip(),
                "pincode": form.get("pincode", "").strip(),
                "lat": float(form.get("lat", 25.6110)),
                "lng": float(form.get("lng", 85.1430)),
                "open_time": form.get("open_time", "08:00"),
                "close_time": form.get("close_time", "22:00"),
                "is_open_24h": "is_open_24h" in form,
                "delivery": "delivery" in form,
                "description": form.get("description", "").strip(),
            }

            shop = AuthService.register_pharmacy(payload, files)
            session["shop_id"] = shop["id"]
            session["shop_name"] = shop["name"]
            session["shop_status"] = shop["status"]

            flash("Registration submitted! Our verification team is reviewing your pharmacy documents.", "success")
            return redirect(url_for("pharmacy_web.dashboard"))
        except Exception as e:
            flash(str(e), "danger")

    return render_template("shop_register.html")


@pharmacy_web.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "")

            result = AuthService.login_pharmacy(email, password)
            shop = result["pharmacy"]

            session["shop_id"] = shop["id"]
            session["shop_name"] = shop["name"]
            session["shop_status"] = shop["status"]

            flash(f"Welcome back, {shop['name']}!", "success")
            return redirect(url_for("pharmacy_web.dashboard"))
        except Exception as e:
            flash(str(e), "danger")

    return render_template("shop_login.html")


@pharmacy_web.route("/logout")
def logout():
    session.pop("shop_id", None)
    session.pop("shop_name", None)
    session.pop("shop_status", None)
    flash("You have logged out of the pharmacy portal.", "info")
    return redirect(url_for("public_web.index"))


@pharmacy_web.route("/dashboard")
def dashboard():
    shop_id = session.get("shop_id")
    if not shop_id:
        return redirect(url_for("pharmacy_web.login"))

    db = get_db()
    shop = db.pharmacies.find_one({"$or": [{"_id": to_object_id(shop_id)}, {"_id": shop_id}]})
    if not shop:
        session.clear()
        return redirect(url_for("pharmacy_web.login"))

    inventory = list(db.inventory.find({"pharmacy_id": str(shop_id)}).sort("med_name", 1))
    reservations = ReservationService.get_pharmacy_reservations(str(shop_id))

    # Calculate summary metrics
    total_items = len(inventory)
    low_stock = sum(1 for item in inventory if 0 < (item.get("stock_quantity") or 0) <= 5)
    out_of_stock = sum(1 for item in inventory if (item.get("stock_quantity") or 0) == 0)
    pending_reservations = sum(1 for r in reservations if r.get("status") == "Pending")

    return render_template(
        "shop_dashboard.html",
        shop=serialize_doc(shop),
        inventory=serialize_doc(inventory),
        reservations=reservations,
        categories=CATEGORIES,
        stats={
            "total_items": total_items,
            "low_stock": low_stock,
            "out_of_stock": out_of_stock,
            "pending_reservations": pending_reservations,
        }
    )


@pharmacy_web.route("/inventory/add", methods=["POST"])
def add_inventory():
    shop_id = session.get("shop_id")
    if not shop_id:
        return redirect(url_for("pharmacy_web.login"))

    try:
        form = request.form
        payload = {
            "med_name": form.get("med_name", "").strip(),
            "salt_composition": form.get("salt_composition", "").strip(),
            "category_slug": form.get("category_slug", "tablets").strip(),
            "manufacturer": form.get("manufacturer", "").strip(),
            "batch_no": form.get("batch_no", "").strip(),
            "expiry_date": form.get("expiry_date"),
            "price": float(form.get("price", 0)),
            "mrp": float(form.get("mrp", 0) or form.get("price", 0)),
            "stock_quantity": int(form.get("stock_quantity", 0)),
            "dosage": form.get("dosage", "").strip(),
            "prescription": "prescription" in form,
        }
        PharmacyService.add_inventory_item(shop_id, payload)
        flash(f"Added '{payload['med_name']}' to inventory.", "success")
    except Exception as e:
        flash(str(e), "danger")

    return redirect(url_for("pharmacy_web.dashboard"))


@pharmacy_web.route("/inventory/<string:item_id>/update", methods=["POST"])
def update_inventory(item_id: str):
    shop_id = session.get("shop_id")
    if not shop_id:
        return redirect(url_for("pharmacy_web.login"))

    try:
        form = request.form
        payload = {
            "med_name": form.get("med_name", "").strip(),
            "salt_composition": form.get("salt_composition", "").strip(),
            "category_slug": form.get("category_slug", "tablets").strip(),
            "manufacturer": form.get("manufacturer", "").strip(),
            "batch_no": form.get("batch_no", "").strip(),
            "expiry_date": form.get("expiry_date"),
            "price": float(form.get("price", 0)),
            "mrp": float(form.get("mrp", 0) or form.get("price", 0)),
            "stock_quantity": int(form.get("stock_quantity", 0)),
            "dosage": form.get("dosage", "").strip(),
            "prescription": "prescription" in form,
            "is_active": "is_active" in form,
        }
        PharmacyService.update_inventory_item(shop_id, item_id, payload)
        flash("Medicine updated successfully.", "success")
    except Exception as e:
        flash(str(e), "danger")

    return redirect(url_for("pharmacy_web.dashboard"))


@pharmacy_web.route("/inventory/<string:item_id>/delete", methods=["POST"])
def delete_inventory(item_id: str):
    shop_id = session.get("shop_id")
    if not shop_id:
        return redirect(url_for("pharmacy_web.login"))

    try:
        PharmacyService.delete_inventory_item(shop_id, item_id)
        flash("Inventory item removed.", "info")
    except Exception as e:
        flash(str(e), "danger")

    return redirect(url_for("pharmacy_web.dashboard"))


@pharmacy_web.route("/reservation/<string:rid>/<string:action>", methods=["POST"])
def reservation_action(rid: str, action: str):
    shop_id = session.get("shop_id")
    if not shop_id:
        return redirect(url_for("pharmacy_web.login"))

    try:
        ReservationService.update_reservation_status(
            reservation_id=rid,
            action=action,
            actor_role="pharmacist",
            actor_id=shop_id
        )
        flash(f"Reservation marked as {action.capitalize()}.", "success")
    except Exception as e:
        flash(str(e), "danger")

    return redirect(url_for("pharmacy_web.dashboard"))


@pharmacy_web.route("/profile", methods=["GET", "POST"])
def profile():
    shop_id = session.get("shop_id")
    if not shop_id:
        return redirect(url_for("pharmacy_web.login"))

    db = get_db()
    if request.method == "POST":
        try:
            form = request.form
            payload = {
                "phone": form.get("phone", "").strip(),
                "owner_name": form.get("owner_name", "").strip(),
                "license_number": form.get("license_number", "").strip(),
                "description": form.get("description", "").strip(),
                "address": form.get("address", "").strip(),
                "city": form.get("city", "Patna").strip(),
                "state": form.get("state", "Bihar").strip(),
                "pincode": form.get("pincode", "").strip(),
                "lat": float(form.get("lat", 25.6110)),
                "lng": float(form.get("lng", 85.1430)),
                "open_time": form.get("open_time", "08:00"),
                "close_time": form.get("close_time", "22:00"),
                "is_open_24h": "is_open_24h" in form,
                "delivery": "delivery" in form,
            }
            PharmacyService.update_pharmacy_profile(shop_id, payload)
            flash("Store profile updated successfully.", "success")
        except Exception as e:
            flash(str(e), "danger")

    shop = db.pharmacies.find_one({"$or": [{"_id": to_object_id(shop_id)}, {"_id": shop_id}]})
    return render_template("shop_profile.html", shop=serialize_doc(shop), is_owner=True)
