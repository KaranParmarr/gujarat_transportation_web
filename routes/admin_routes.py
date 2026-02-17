from flask import Blueprint, render_template, session, redirect, request, jsonify
from models.user_model import User
from models.booking_model import Booking

admin_bp = Blueprint("admin_bp", __name__)

def admin_only():
    return "user" in session and session["user"].get("role") == "admin"

@admin_bp.route("/adminpanel")
def adminpanel():
    if not admin_only():
        return redirect("/")

    user_count = User.count_all()
    users = User.recent(10)

    bus_count = 0
    truck_count = 0

    total_revenue = Booking.total_revenue_paid()
    bookings = Booking.recent(10)

    return render_template(
        "adminpanel.html",
        user_count=user_count,
        users=users,
        bus_count=bus_count,
        truck_count=truck_count,
        total_revenue=total_revenue,
        bookings=bookings
    )

@admin_bp.route("/api/admin-stats")
def admin_stats():
    if not admin_only():
        return jsonify({"error": "unauthorized"}), 401

    return jsonify({
        "user_count": User.count_all(),
        "users": User.recent(10),
        "total_revenue": Booking.total_revenue_paid(),
        "recent_bookings": Booking.recent(10)
    })

@admin_bp.route("/users")
def manage_users():
    if not admin_only():
        return redirect("/")
    return render_template("manage-users.html")

@admin_bp.route("/get-users")
def get_users():
    if not admin_only():
        return jsonify({"error": "unauthorized"}), 401
    return jsonify(User.all_users())

@admin_bp.route("/delete-user/<int:user_id>")
def delete_user(user_id):
    if not admin_only():
        return jsonify({"error": "unauthorized"}), 401
    User.delete(user_id)
    return "deleted"

@admin_bp.route("/toggle-user/<int:user_id>")
def toggle_user(user_id):
    if not admin_only():
        return jsonify({"error": "unauthorized"}), 401
    new_status = User.toggle_status(user_id)
    if new_status is None:
        return jsonify({"error": "not_found"}), 404
    return new_status

@admin_bp.route("/edit-user", methods=["POST"])
def edit_user():
    if not admin_only():
        return jsonify({"error": "unauthorized"}), 401

    user_id = request.form.get("id")
    fullname = request.form.get("fullname", "").strip()
    email = request.form.get("email", "").strip()

    User.update_basic(user_id, fullname, email)
    return "updated"
