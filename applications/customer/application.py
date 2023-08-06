from flask import Flask, request, Response, jsonify
from applications.configuration import Configuration
from applications.models import database, Product, Category, ProductCategory
from sqlalchemy import and_
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, decode_token, \
    create_refresh_token, get_jwt
import io
import csv

application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)


@application.route("/", methods=["GET"])
def index():
    return "Hello world!"


@application.route("/search", methods=["GET"])
@jwt_required()
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


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5002)
