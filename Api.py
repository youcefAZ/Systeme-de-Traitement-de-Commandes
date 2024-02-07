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
    state = Column(String, default="Pending", index=True)

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
    customer_name = Column(String, index=True)
    quantity = Column(Integer, index=True)
    montant = Column(Integer, index=True)
    state = Column(String, default="Pending", index=True)

class Payement(Base):
    __tablename__ = "payement"

    payement_id=Column(Integer, primary_key=True, index=True)
    commande_id = Column(Integer, index=True)
    customer_name=Column(String,index=True)
    quantity=Column(Integer, index=True)
    montant= Column(Integer, index=True)

# Création de la table
Base.metadata.create_all(bind=engine)

# Modèles
class OrderRequest(BaseModel):
    product_id: int
    customer_name: str
    quantity : int
    state: str = "Pending"

class OrderResponse(BaseModel):
    idcommande: int
    product_id: int
    customer_name: str
    quantity : int
    state : str

class DevisRequest(BaseModel):
    idcommande : int
    customer_name: str
    quantity : int
    montant: int
    state: str = "Pending"

class DevisReponse(BaseModel):
    idDevis: int
    idcommande : int
    customer_name: str
    quantity : int
    montant: int
    state : str

class ProductRequest(BaseModel):
    product_name : str
    quantity_available : int
    unit_price : int

class ProductResponse(BaseModel):
    product_id : int
    product_name : str
    quantity_available : int
    unit_price : int

class PayementRequest(BaseModel):
    commande_id : int
    customer_name : str
    quantity : int
    montant : int

class PayementResponse(BaseModel):
    payement_id : int
    commande_id : int
    customer_name : str
    quantity : int
    montant : int

def update_order_state(order_id: int, validation: str):
    db = SessionLocal()
    order = db.query(Order).filter(Order.idcommande == order_id).first()
    if order:
        order.state=validation.lower()
        db.commit()
        db.refresh(order)
        return order
    return None


def update_devis_state(devis_id: int, validation: str):
    db = SessionLocal()
    order = db.query(Order).filter(Devis.idDevis == devis_id).first()
    if order:
        order.state=validation.lower()
        db.commit()
        db.refresh(order)
        return order
    return None


app = FastAPI()

@app.post("/orders/", response_model=OrderResponse)
def create_order(order_request: OrderRequest):
    db = SessionLocal()
    db_order = Order(**order_request.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return OrderResponse(
        idcommande=db_order.idcommande,
        product_id=db_order.product_id,
        customer_name=db_order.customer_name,
        quantity=db_order.quantity,
        state=db_order.state
        )

@app.get("/orders/{order_idcommande}", response_model=OrderResponse)
def read_order(order_idcommande: int):
    db = SessionLocal()
    db_order = db.query(Order).filter(Order.idcommande == order_idcommande).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return OrderResponse(
        idcommande=db_order.idcommande,
        product_id=db_order.product_id,
        customer_name=db_order.customer_name,
        quantity=db_order.quantity,
        state=db_order.state
        )


@app.post("/validate_order/{order_id}/{validation}", response_model=OrderResponse)
def valid_order(order_id: int, validation: str):
    order = update_order_state(order_id, validation)
    if order:
        return order
    else:
        return {"message": "Order not found"}


@app.post("/devis/", response_model=DevisReponse)
def create_devis(devis_request: DevisRequest):
    db = SessionLocal()
    db_devis = Devis(**devis_request.dict())
    db.add(db_devis)
    db.commit()
    db.refresh(db_devis)
    return DevisReponse(
        idDevis=db_devis.idDevis,
        idcommande=db_devis.idcommande,
        customer_name=db_devis.customer_name,
        quantity=db_devis.quantity,
        montant=db_devis.montant,
        state=db_devis.state
    )

@app.get("/devis/{devis_idDevis}", response_model=DevisRequest)
def read_order(devis_idDevis: int):
    db = SessionLocal()
    db_devis = db.query(Devis).filter(Devis.idDevis == devis_idDevis).first()
    if db_devis is None:
        raise HTTPException(status_code=404, detail="Devis not found")
    return DevisReponse(
        idDevis=db_devis.idDevis,
        idcommande=db_devis.idcommande,
        customer_name=db_devis.customer_name,
        quantity=db_devis.quantity,
        montant=db_devis.montant,
        state=db_devis.state
    )

@app.post("/validate_devis/{devis_id}/{validation}", response_model=OrderResponse)
def valid_devis(devis_id: int, validation: str):
    devis = update_devis_state(devis_id, validation)
    if devis:
        return devis
    else:
        return {"message": "Devis not found"}


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
    return ProductResponse(
        product_id=db_product.product_id,
        product_name=db_product.product_name,
        quantity_available=db_product.quantity_available,
        unit_price=db_product.unit_price)
        

@app.get("/remplissage/{product_id}", response_model=ProductResponse)
def read_order(product_id: int):
    db = SessionLocal()
    db_product = db.query(Product).filter(Product.product_id == product_id).first()
    print(db_product)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product is not found")
    return ProductResponse(
        product_id=db_product.product_id,
        product_name=db_product.product_name,
        quantity_available=db_product.quantity_available,
        unit_price=db_product.unit_price)


@app.post("/payement/", response_model=PayementResponse)
def create_payement(payement_request:PayementRequest):
    db = SessionLocal()
    db_payement = Payement(**payement_request.dict())
    db.add(db_payement)
    db.commit()
    db.refresh(db_payement)
    return PayementResponse(
        payement_id=db_payement.payement_id,
        commande_id=db_payement.commande_id,
        customer_name=db_payement.customer_name,
        quantity=db_payement.quantity,
        montant=db_payement.montant)
    

@app.post("/checkPayement/{payement_id}",response_model=PayementResponse)
def check_payement(payement_id: int) :
    db = SessionLocal()
    db_payement = db.query(Payement).filter(Payement.payement_id == payement_id).first()
    if db_payement is None:
        raise HTTPException(status_code=404, detail="Payement not found")
    return PayementResponse(
        payement_id=db_payement.payement_id,
        commande_id=db_payement.commande_id,
        customer_name=db_payement.customer_name,
        quantity=db_payement.quantity,
        montant=db_payement.montant)

#uvicorn nom_du_fichier:app --reload
