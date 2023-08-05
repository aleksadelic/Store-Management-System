from flask import Flask
from configuration import Configuration
from flask_migrate import Migrate, init, migrate, upgrade
from models import database, Role, UserRole, User
from sqlalchemy_utils import database_exists, create_database

application = Flask(__name__)
application.config.from_object(Configuration)

migrate_object = Migrate(application, database)

if not database_exists(application.config["SQLALCHEMY_DATABASE_URI"]):
    create_database(application.config["SQLALCHEMY_DATABASE_URI"])

database.init_app(application)

with application.app_context() as context:
    database.init_app(application)
    init()
    migrate(message="Production migration")
    upgrade()

    owner_role = Role(name="owner")
    customer_role = Role(name="customer")
    courier_role = Role(name="courier")

    database.session.add(owner_role)
    database.session.add(customer_role)
    database.session.add(courier_role)
    database.session.commit()

    owner = User(email="onlymoney@gmail.com", password="evenmoremoney", forename="Scrooge", surname="McDuck")

    database.session.add(owner)
    database.session.commit()

    user_role_owner = UserRole(user_id=owner.id, role_id=owner_role.id)

    database.session.add(user_role_owner)
    database.session.commit()
