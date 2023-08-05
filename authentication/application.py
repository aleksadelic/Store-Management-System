from flask import Flask, request, Response, jsonify
from configuration import Configuration
from models import database, User, UserRole
from sqlalchemy import and_
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, decode_token, create_refresh_token, get_jwt
import re

EMAIL_REGEX = re.compile(r"^[a-z0-9\.]+@([a-z0-9]+\.)+[a-z]{2,4}$")

application = Flask(__name__)
application.config.from_object(Configuration)


@application.route("/", methods=["GET"])
def index():
    return "Hello world!"


@application.route("/register_customer", methods=["POST"])
def register_customer():
    return register(request, 2)


@application.route("/register_courier", methods=["POST"])
def register_courier():
    return register(request, 3)


def register(my_request, role_id):
    forename = my_request.json.get("forename", "")
    surname = my_request.json.get("surname", "")
    email = my_request.json.get("email", "")
    password = my_request.json.get("password", "")

    if forename == "":
        response = {"message": "Field forename is missing."}
        return response, 400
    if surname == "":
        response = {"message": "Field surname is missing."}
        return response, 400
    if email == "":
        response = {"message": "Field email is missing."}
        return response, 400
    if password == "":
        response = {"message": "Field password is missing."}
        return response, 400

    if not EMAIL_REGEX.match(email):
        response = {"message": "Invalid email."}
        return response, 400

    if len(password) < 8:
        response = {"message": "Invalid password."}
        return response, 400

    user = User.query.filter(User.email == email).first()
    if user:
        response = {"message": "Email already exists."}
        return response, 400

    user = User(forename=forename, surname=surname, email=email, password=password)
    database.session.add(user)
    database.session.commit()

    user_role = UserRole(user_id=user.id, role_id=role_id)
    database.session.add(user_role)
    database.session.commit()

    return Response(status=200)


jwt = JWTManager(application)


@application.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    if email == "":
        response = {"message": "Field email is missing."}
        return response, 400
    if password == "":
        response = {"message": "Field password is missing."}
        return response, 400

    if not EMAIL_REGEX.match(email):
        response = {"message": "Invalid email."}
        return response, 400

    user = User.query.filter(and_(User.email == email, User.password == password)).first()

    if not user:
        response = {"message": "Invalid credentials."}
        return response, 400

    additional_claims = {
        "forename": user.forename,
        "surname": user.surname,
        "roles": [str(role) for role in user.roles]
    }

    access_token = create_access_token(identity=user.email, additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=user.email, additional_claims=additional_claims)

    response = {"accessToken": access_token}

    return jsonify(accessToken=access_token, refreshToken=refresh_token), 200


@application.route("/check", methods=["POST"])
@jwt_required()
def check():
    return "Token is valid"


@application.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    refresh_claims = get_jwt()

    additional_claims = {
        "forename": refresh_claims["forename"],
        "surname": refresh_claims["surname"],
        "roles": refresh_claims["roles"]
    }

    return Response(create_access_token(identity=identity, additional_claims=additional_claims), status=200)


@application.route("/delete", methods=["POST"])
@jwt_required()
def delete_user():
    # token = decode_token(request.headers["Authorization"].split(" ")[1])
    # email = token["sub"]

    email = get_jwt_identity()
    user = User.query.filter(User.email == email).first()

    if not user:
        response = {"message": "Unknown user."}
        return response, 400

    UserRole.query.filter(UserRole.user_id == user.id).delete()
    User.query.filter(User.id == user.id).delete()
    database.session.commit()

    return Response(status=200)


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5000)
