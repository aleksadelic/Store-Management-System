from flask import Flask, request, Response, jsonify
from sqlalchemy import func, or_

from configuration import Configuration
from models import database, Product, Category, ProductCategory, Order, Item
from flask_jwt_extended import JWTManager, jwt_required
import io
import csv
from role_check_decorator import role_check

application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)


@application.route("/", methods=["GET"])
def index():
    return "Hello world!"


@application.route("/update", methods=["POST"])
@jwt_required()
@role_check(role="owner")
def update():
    if "file" not in request.files:
        return jsonify(message="Field file is missing."), 400

    content = request.files["file"].stream.read().decode("utf-8")
    stream = io.StringIO(content)
    reader = csv.reader(stream)

    # perform check
    cnt = 0
    for line in reader:
        if len(line) != 3:
            return jsonify(message="Incorrect number of values on line {}.".format(cnt)), 400

        try:
            val = float(line[2])
            if val < 0:
                return jsonify(message="Incorrect price on line {}.".format(cnt)), 400
        except ValueError:
            return jsonify(message="Incorrect price on line {}.".format(cnt)), 400

        product = Product.query.filter(Product.name == line[1]).first()
        if product:
            return jsonify(message="Product {} already exists.".format(line[1])), 400

        cnt += 1

    stream = io.StringIO(content)
    reader = csv.reader(stream)
    for line in reader:
        product = Product(name=line[1], price=float(line[2]))
        database.session.add(product)
        database.session.commit()

        categories = line[0].split("|")
        for category in categories:
            cat = Category.query.filter(Category.name == category).first()
            product_category = ProductCategory(product_id=product.id, category_id=cat.id)
            database.session.add(product_category)
            database.session.commit()

    return Response(status=200)


@application.route("/product_statistics", methods=["GET"])
@jwt_required()
@role_check(role="owner")
def product_statistics():
    sold_items = database.session.query(
        Product.name,
        func.sum(Item.quantity).label("sold")
    ).join(Item.product).join(Item.order).filter(Order.status == "COMPLETE").\
        group_by(Product.id).all()

    pending_items = database.session.query(
        Product.name,
        func.sum(Item.quantity).label("waiting")
    ).join(Item.product).join(Item.order).filter(or_(Order.status == "CREATED", Order.status == "PENDING")). \
        group_by(Product.id).all()

    print(sold_items)
    print(pending_items)

    items = {}
    for item in sold_items:
        items[item.name] = [int(item.sold), 0]

    for item in pending_items:
        if item.name in items:
            items[item.name][1] = int(item.waiting)
        else:
            items[item.name] = [0, int(item.waiting)]

    statistics = []
    for item, counts in items.items():
        statistics.append({
            "name": item,
            "sold": counts[0],
            "waiting": counts[1]
        })

    return jsonify(statistics=statistics), 200


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5001)
