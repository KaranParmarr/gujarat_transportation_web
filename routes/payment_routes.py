from flask import Blueprint, request, jsonify, session
from extensions import socketio

payment_bp = Blueprint("payment_bp", __name__)

@payment_bp.route("/api/pay", methods=["POST"])
def pay():
    """
    Payment Simulation:
    Frontend sends amount, bookingType, etc.
    Returns success and emits live revenue update to admin dashboard.
    """
    if "user" not in session:
        return jsonify({"error": "login_required"}), 401

    data = request.json or {}
    amount = int(data.get("amount", 0))

    if amount <= 0:
        return jsonify({"error": "invalid_amount"}), 400

    # 🔥 Live revenue update for admin dashboard
    socketio.emit("admin_revenue_update", {
        "amount": amount
    })

    return jsonify({"success": True, "paid": True})
