from flask import Blueprint, request, jsonify, session
from extensions import socketio
from models.seat_model import Seat
from models.booking_model import Booking
from models.bus_model import Bus

booking_bp = Blueprint("booking_bp", __name__)


@booking_bp.route("/api/seats/<int:bus_id>")
def seats(bus_id):
    return jsonify(Seat.get_by_bus(bus_id))


@booking_bp.route("/lock-seat", methods=["POST"])
def lock_seat():
    data = request.json or {}
    bus_id = data.get("bus_id")
    seat_no = data.get("seat")

    if not bus_id or not seat_no:
        return jsonify({"error": "missing_data"}), 400

    res = Seat.lock(bus_id, seat_no)
    if "error" in res:
        return jsonify(res), 409

    # 🔥 live broadcast seat locked
    socketio.emit("seat_update", {
        "bus_id": int(bus_id),
        "seat": str(seat_no),
        "status": "locked"
    })

    return jsonify({"success": True})


@booking_bp.route("/confirm-booking", methods=["POST"])
def confirm_booking():
    if "user" not in session:
        return jsonify({"error": "login_required"}), 401

    data = request.json or {}
    bus_id = data.get("bus_id")
    seats = data.get("seats", [])
    amount = data.get("amount", 0)

    if not bus_id or not seats:
        return jsonify({"error": "missing_data"}), 400

    # mark seats booked
    for s in seats:
        Seat.book(bus_id, s)
        socketio.emit("seat_update", {
            "bus_id": int(bus_id),
            "seat": str(s),
            "status": "booked"
        })

    Booking.create(
        user_id=session["user"]["id"],
        bus_id=bus_id,
        seats_csv=",".join([str(x) for x in seats]),
        amount=int(amount),
        payment_status="paid"
    )

    # 🔥 admin sync event
    socketio.emit("admin_booking_update", {
        "type": "bus",
        "bus_id": int(bus_id),
        "seats": seats,
        "amount": int(amount)
    })

    return jsonify({"success": True})
