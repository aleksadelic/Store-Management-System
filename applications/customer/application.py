from flask import Flask, request, jsonify
from configuration import Configuration
from models import database, Product, Category, ProductCategory
from sqlalchemy import and_
from flask_jwt_extended import JWTManager, jwt_required
from role_check_decorator import role_check


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
    if "Authorization" not in request.headers:
        return jsonify(msg="Missing Authorization Header"), 401

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


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5002)
