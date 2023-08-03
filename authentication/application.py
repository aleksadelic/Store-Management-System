from flask import Flask, request, Response
from configuration import Configuration
from models import database, User, Role, UserRole
from email.utils import parseaddr

application = Flask(__name__)
application.config.from_object(Configuration)


@application.route("/", methods=["GET"])
def index():
    return "Hello world!"


@application.route("/register_customer", methods=["POST"])
def register_customer():
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    if forename == "" or surname == "" or email == "" or password == "":
        return Response("All fields are required!", status=400)

    # ne radi dobro izgleda
    if len(parseaddr(email)) == 0:
        return Response("Email invalid!", status=400)

    user = User(forename=forename, surname=surname, email=email, password=password)
    database.session.add(user)
    database.session.commit()

    user_role = UserRole(user_id=user.id, role_id=2)
    database.session.add(user_role)
    database.session.commit()

    return Response("Registration successful!", status=200)


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5002)
