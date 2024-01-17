import Api
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import requests

base_url = "http://localhost:8000"
fournisseur_url="http://localhost:8002"
client_url="http://localhost:8001"

app = FastAPI()

def payer_devis(devis_data : Api.DevisReponse):

    print(devis_data)
    print(type(devis_data))
    payement_request={
    "commande_id" : devis_data.idcommande,
    "customer_name" : devis_data.customer_name,
    "quantity" : devis_data.quantity,
    "montant": devis_data.montant
    }

    print(payement_request)

    order_endpoint=f"{base_url}/payement"
    response = requests.post(order_endpoint,json=payement_request)
    response_json=response.json()

    print(response_json)

    order_endpoint = f"{fournisseur_url}/receive_payement/"
    response = requests.post(order_endpoint,json=response_json)


class ValidationResponseModel(BaseModel):
    status: str
    message: str

@app.post("/receive_validation", response_model=ValidationResponseModel)
def receive_validation(is_validated: ValidationResponseModel):
    print("Order validation received")
    print(is_validated)

    return is_validated


@app.post("/receive_devis/", response_model=Api.DevisReponse)
def receive_devis(devis_data: Api.DevisReponse, background_tasks: BackgroundTasks):
    print("received Devis from Fournisseur")
    print(devis_data)

    background_tasks.add_task(payer_devis,devis_data)
    return devis_data