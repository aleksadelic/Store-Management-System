from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()


class ProductCategory(database.Model):
    __tablename__ = "product_category"

    id = database.Column(database.Integer, primary_key=True)
    product_id = database.Column(database.Integer, database.ForeignKey("products.id"), nullable=False)
    category_id = database.Column(database.Integer, database.ForeignKey("categories.id"), nullable=False)


class Product(database.Model):
    __tablename__ = "products"

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False)
    price = database.Column(database.Float, nullable=False)

    categories = database.relationship("Category", secondary=ProductCategory.__table__, back_populates="products")
    items = database.relationship("Item", back_populates="product")

    def __repr__(self):
        return self.name


class Category(database.Model):
    __tablename__ = "categories"

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False)

    products = database.relationship("Product", secondary=ProductCategory.__table__, back_populates="categories")

    def __repr__(self):
        return self.name


class Order(database.Model):
    __tablename__ = "orders"

    id = database.Column(database.Integer, primary_key=True)
    customer = database.Column(database.String(256), nullable=False)
    price = database.Column(database.Float, nullable=False)
    status = database.Column(database.String(256), nullable=False)
    timestamp = database.Column(database.DateTime, nullable=False)

    items = database.relationship("Item", back_populates="order")


class Item(database.Model):
    __tablename__ = "items"

    id = database.Column(database.Integer, primary_key=True)
    order_id = database.Column(database.Integer, database.ForeignKey("orders.id"), nullable=False)
    product_id = database.Column(database.Integer, database.ForeignKey("products.id"), nullable=False)
    quantity = database.Column(database.Integer, nullable=False)

    order = database.relationship("Order", back_populates="items")
    product = database.relationship("Product", back_populates="items")
