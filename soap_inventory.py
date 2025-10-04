import logging
from spyne import Application, rpc, ServiceBase, Integer, Unicode, Float
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from sqlalchemy import create_engine, Column, Integer as SQLInt, String, Float as SQLFloat
from sqlalchemy.orm import sessionmaker, declarative_base
from wsgiref.simple_server import make_server

# ----------------- Database Setup -----------------
# Use Docker Compose credentials
DB_URL = "postgresql+psycopg2://inventory:inventory@localhost:5432/inventory"
engine = create_engine(DB_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = Column(SQLInt, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    quantity = Column(SQLInt, nullable=False)
    price = Column(SQLFloat, nullable=False)

# Create tables if not exist
Base.metadata.create_all(bind=engine)

# ----------------- SOAP Service -----------------
class InventoryService(ServiceBase):

    @rpc(Integer, Unicode, Integer, Float, _returns=Unicode)
    def CreateProduct(ctx, id, name, quantity, price):
        if quantity < 0 or price < 0:
            return "Error: Quantity and Price must be non-negative"
        session = SessionLocal()
        if session.query(Product).filter_by(id=id).first():
            session.close()
            return f"Error: Product with ID {id} already exists"
        product = Product(id=id, name=name, quantity=quantity, price=price)
        session.add(product)
        session.commit()
        session.close()
        return f"Product {name} created successfully"

    @rpc(Integer, _returns=Unicode)
    def GetProduct(ctx, id):
        session = SessionLocal()
        product = session.query(Product).filter_by(id=id).first()
        session.close()
        if not product:
            return f"Error: Product with ID {id} not found"
        return f"ID: {product.id}, Name: {product.name}, Quantity: {product.quantity}, Price: {product.price}"

    @rpc(Integer, Unicode, Integer, Float, _returns=Unicode)
    def UpdateProduct(ctx, id, name, quantity, price):
        if quantity < 0 or price < 0:
            return "Error: Quantity and Price must be non-negative"
        session = SessionLocal()
        product = session.query(Product).filter_by(id=id).first()
        if not product:
            session.close()
            return f"Error: Product with ID {id} not found"
        product.name = name
        product.quantity = quantity
        product.price = price
        session.commit()
        session.close()
        return f"Product {id} updated successfully"

    @rpc(Integer, _returns=Unicode)
    def DeleteProduct(ctx, id):
        session = SessionLocal()
        product = session.query(Product).filter_by(id=id).first()
        if not product:
            session.close()
            return f"Error: Product with ID {id} not found"
        session.delete(product)
        session.commit()
        session.close()
        return f"Product {id} deleted successfully"

# ----------------- SOAP Application -----------------
application = Application(
    [InventoryService],
    tns="spyne.inventory.soap",
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

wsgi_app = WsgiApplication(application)

# ----------------- Run Server -----------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    server = make_server("0.0.0.0", 8000, wsgi_app)
    print("SOAP Inventory Service running on http://localhost:8000")
    print("WSDL available at: http://localhost:8000/?wsdl")
    server.serve_forever()
