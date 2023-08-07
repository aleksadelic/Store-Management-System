from flask import Flask, request, jsonify, Response
from configuration import Configuration
from models import database, Order
from flask_jwt_extended import JWTManager, jwt_required
from role_check_decorator import role_check

application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)


@application.route("/", methods=["GET"])
def index():
    return "Hello world!"


@application.route("/orders_to_deliver", methods=["GET"])
@jwt_required()
@role_check(role="courier")
def order_to_deliver():
    orders = Order.query.filter(Order.status == "CREATED").all()
    orders_json = [{"id": order.id, "email": order.customer} for order in orders]

    return jsonify(orders=orders_json), 200


@application.route("/pick_up_order", methods=["POST"])
@jwt_required()
@role_check(role="courier")
def pick_up_order():
    if not request.data or "id" not in request.json:
        return jsonify(message="Missing order id."), 400

    order_id = request.json["id"]
    if not isinstance(order_id, int) or order_id <= 0:
        return jsonify(message="Invalid order id."), 400

    order = Order.query.filter(Order.id == order_id).first()

    if not order or order.status != "CREATED":
        return jsonify(message="Invalid order id."), 400

    order.status = "PENDING"
    database.session.commit()

    return Response(status=200)


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5003)
