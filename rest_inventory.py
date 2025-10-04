from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, PositiveInt, condecimal
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base

# ---------------- Database Setup -----------------
DB_URL = "postgresql+psycopg2://inventory:inventory@db:5432/inventory"
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

Base.metadata.create_all(bind=engine)

# ---------------- Pydantic Models -----------------
class ProductCreate(BaseModel):
    name: str = Field(..., max_length=100)
    quantity: PositiveInt
    price: condecimal(gt=0)

class ProductUpdate(ProductCreate):
    pass

class ProductResponse(BaseModel):
    id: int
    name: str
    quantity: int
    price: float

# ---------------- FastAPI App -----------------
app = FastAPI(title="Inventory REST API")

# CRUD endpoints
@app.post("/products", response_model=ProductResponse)
def create_product(product: ProductCreate):
    session = SessionLocal()
    db_product = Product(**product.dict())
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    session.close()
    return db_product

@app.get("/products", response_model=list[ProductResponse])
def get_products():
    session = SessionLocal()
    products = session.query(Product).all()
    session.close()
    return products

@app.get("/products/{id}", response_model=ProductResponse)
def get_product(id: int):
    session = SessionLocal()
    product = session.query(Product).filter_by(id=id).first()
    session.close()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put("/products/{id}", response_model=ProductResponse)
def update_product(id: int, product: ProductUpdate):
    session = SessionLocal()
    db_product = session.query(Product).filter_by(id=id).first()
    if not db_product:
        session.close()
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in product.dict().items():
        setattr(db_product, key, value)
    session.commit()
    session.refresh(db_product)
    session.close()
    return db_product

@app.delete("/products/{id}")
def delete_product(id: int):
    session = SessionLocal()
    product = session.query(Product).filter_by(id=id).first()
    if not product:
        session.close()
        raise HTTPException(status_code=404, detail="Product not found")
    session.delete(product)
    session.commit()
    session.close()
    return {"detail": f"Product {id} deleted successfully"}
