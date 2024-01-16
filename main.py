from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel

# Configuration de la base de données
DATABASE_URL = "sqlite:///./test4.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modèle de base de données

class Order(Base):
    __tablename__ = "orders"

    idcommande = Column(Integer, primary_key=True, index=True)
    product_id = Column(String, index=True)
    quantity =  Column(Integer, index=True)
    customer_name = Column(String, index=True)

class Product(Base):
    __tablename__ = "product"

    product_id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True)
    quantity_available =  Column(Integer, index=True)
    unit_price = Column(Integer, index=True)

class Devis(Base):
    __tablename__ = "devis"

    idDevis = Column(Integer, primary_key=True, index=True)
    idcommande = Column(String, index=True)
    quantity = Column(Integer, index=True)
    montant = Column(Integer, index=True)

# Création de la table
Base.metadata.create_all(bind=engine)

# Modèles
class OrderRequest(BaseModel):
    product_id: int
    customer_name: str
    quantity : int

class OrderResponse(BaseModel):
    idcommande: int
    product_id: int
    customer_name: str
    quantity : int

class DevisRequest(BaseModel):
    idcommande : int
    quantity : int
    montant: int

class DevisReponse(BaseModel):
    idDevis: int
    idcommande : int
    quantity : int
    montant: int

class ProductRequest(BaseModel):
    product_name : str
    quantity_available : int
    unit_price : int

class ProductResponse(BaseModel):
    product_id : int
    product_name : str
    quantity_available : int
    unit_price : int

app = FastAPI()

@app.post("/orders/", response_model=OrderResponse)
def create_order(order_request: OrderRequest):
    db = SessionLocal()
    db_order = Order(**order_request.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

@app.get("/orders/{order_idcommande}", response_model=OrderResponse)
def read_order(order_idcommande: int):
    db = SessionLocal()
    db_order = db.query(Order).filter(Order.idcommande == order_idcommande).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@app.post("/devis/", response_model=DevisReponse)
def create_devis(devis_request: DevisRequest):
    db = SessionLocal()
    db_devis = Devis(**devis_request.dict())
    db.add(db_devis)
    db.commit()
    db.refresh(db_devis)
    return db_devis

@app.get("/devis/{devis_idDevis}", response_model=DevisRequest)
def read_order(devis_idDevis: int):
    db = SessionLocal()
    db_devis = db.query(Devis).filter(Devis.idDevis == devis_idDevis).first()
    if db_devis is None:
        raise HTTPException(status_code=404, detail="Devis not found")
    return db_devis


@app.post("/check_order")
def check_order(product_id: int, quantity: int):
    # Trouver le produit dans la base de données
    db = SessionLocal()
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Comparer la quantité demandée avec la quantité disponible
    if quantity > product.quantity_available:
        return {"status": "Unavailable", "message": "Requested quantity exceeds available stock."}
    else:
        return {"status": "Available", "message": "Order can be processed."}
    
@app.post("/remplissage/", response_model=ProductResponse)
def create_order(product_request: ProductRequest):
    db = SessionLocal()
    db_product = Product(**product_request.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/remplissage/{product_product_id}", response_model=ProductResponse)
def read_order(product_product_id: int):
    db = SessionLocal()
    db_product = db.query(Product).filter(Product.product_id == product_product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product is not found")
    return db_product


#uvicorn nom_du_fichier:app --reload
