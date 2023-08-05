from datetime import timedelta
import os

# database_url = os.environ["DATABASE_URL"]
database_url = "localhost:3307"


class Configuration:
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{database_url}/authentication"
    JWT_SECRET_KEY = "JWT_SECRET_DEV_KEY"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
