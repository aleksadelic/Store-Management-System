from flask import Flask, request, jsonify
from configuration import Configuration
from models import database, Product, Category, ProductCategory, Order, Item
from sqlalchemy import and_
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from role_check_decorator import role_check
import datetime

application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)


@application.route("/", methods=["GET"])
def index():
    return "Hello world!"


@application.route("/search", methods=["GET"])
@jwt_required()
@role_check(role="customer")
def search():
    name = request.args.get("name", "")
    category = request.args.get("category", "")

    products = Product.query.join(ProductCategory).join(Category).filter(
        and_(Product.name.like("%{}%".format(name)), Category.name.like("%{}%".format(category)))
    ).all()

    category_response = set()
    for prod in products:
        cats = Category.query.join(ProductCategory).filter(ProductCategory.product_id == prod.id).all()
        for cat in cats:
            category_response.add(str(cat))

    product_response = []
    for product in products:
        categories = Category.query.join(ProductCategory).filter(ProductCategory.product_id == product.id).all()
        product_json = {
            "categories": [str(cat) for cat in categories],
            "id": product.id,
            "name": product.name,
            "price": product.price
        }
        product_response.append(product_json)

    return jsonify(categories=list(category_response), products=product_response), 200


@application.route("/order", methods=["POST"])
@jwt_required()
@role_check(role="customer")
def order():
    if not request.data or "requests" not in request.json:
        return jsonify(message="Field requests is missing."), 400

    ind = 0
    requests = request.json["requests"]
    for req in requests:
        if "id" not in req:
            return jsonify(message="Product id is missing for request number {}.".format(ind)), 400
        if "quantity" not in req:
            return jsonify(message="Product quantity is missing for request number {}.".format(ind)), 400
        if not isinstance(req["id"], int) or req["id"] < 0:
            return jsonify(message="Invalid product id for request number {}.".format(ind)), 400
        if not isinstance(req["quantity"], int) or req["quantity"] < 0:
            return jsonify(message="Invalid product quantity for request number {}.".format(ind)), 400

        product = Product.query.filter(Product.id == req["id"]).first()
        if not product:
            return jsonify(message="Invalid product for request number {}.".format(ind)), 400
        ind += 1

    customer = get_jwt_identity()
    total_price = 0
    order = Order(customer=customer, price=total_price, status="CREATED",
                  timestamp=datetime.datetime.now().isoformat())

    database.session.add(order)
    database.session.commit()

    items = []
    for req in requests:
        item = Item(order_id=order.id, product_id=req["id"], quantity=req["quantity"])
        items.append(item)
        product = Product.query.filter(Product.id == req["id"]).first()
        total_price += product.price * req["quantity"]

    database.session.add_all(items)
    database.session.commit()

    order.price = total_price
    database.session.commit()

    return jsonify(id=order.id), 200


@application.route("/status", methods=["GET"])
@jwt_required()
@role_check(role="customer")
def status():
    customer = get_jwt_identity()
    orders = Order.query.filter(Order.customer == customer).all()
    orders_json = []
    for order in orders:
        items = Item.query.filter(Item.order_id == order.id).all()

        products = []
        for item in items:
            product = Product.query.filter(Product.id == item.product_id).first()
            categories = Category.query.join(ProductCategory).filter(ProductCategory.product_id == product.id).all()
            product_json = {
                "categories": [str(category) for category in categories],
                "name": product.name,
                "price": product.price,
                "quantity": item.quantity
            }
            products.append(product_json)

        order_json = {
            "products": products,
            "price": order.price,
            "status": order.status,
            "timestamp": order.timestamp
        }
        orders_json.append(order_json)

    return jsonify(orders=orders_json), 200




if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5002)
