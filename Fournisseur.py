import Api
from fastapi import FastAPI, BackgroundTasks
import requests


app = FastAPI()

base_url = "http://localhost:8000"
fournisseur_url="http://localhost:8002"
client_url="http://localhost:8001"


def check_order(order_data: Api.OrderResponse, background_tasks:BackgroundTasks):
    product_id=order_data["product_id"]
    quantity=order_data["quantity"]
    order_endpoint = f"{base_url}/check_order?product_id={product_id}&quantity={quantity}"
    
    response = requests.post(order_endpoint)
    response_json = response.json()

    if response_json["status"] == "Available":
        # Order verified successfully
        print("Order verified successfully")
        print(response_json)

        order_endpoint = f"{client_url}/receive_validation"
        print("Works ?")
        response = requests.post(order_endpoint,json=response_json)

        background_tasks.add_task(generate_devis,order_data)

    else:
        # Failed to verify order, print error details
        print(f"Failed to verify order. Status: {response_json['status']}, Message: {response_json['message']}")
        



def generate_devis(order_data : Api.OrderResponse):
    product_id=order_data["product_id"]
    order_endpoint = f"{base_url}/remplissage/{product_id}"
    response = requests.get(order_endpoint)
    response_json = response.json()

    print(response_json)
    montant= order_data["quantity"]*response_json["unit_price"]

    devis_request={
    "idcommande" : order_data["idcommande"],
    "quantity" : order_data["quantity"],
    "customer_name" : order_data["customer_name"],
    "montant": montant}

    print(devis_request)

    order_endpoint=f"{base_url}/devis"
    response = requests.post(order_endpoint,json=devis_request)
    response_json=response.json()

    print(response_json)
    order_endpoint = f"{client_url}/receive_devis/"
    response = requests.post(order_endpoint,json=response_json)



@app.post("/place_order/")
def place_order(order_data: Api.OrderRequest, background_tasks: BackgroundTasks):

    print("placing order..")
    order_endpoint = f"{base_url}/orders/"

    response = requests.post(order_endpoint, json=order_data.dict())

    if response.status_code == 200:
        # Order placed successfully
        print("Order placed successfully")
        print(response.json())

        #call check_order from a backgroundtask
        background_tasks.add_task(check_order,response.json(),background_tasks)
    else:
        # Failed to place order
        print(f"Failed to place order. Status Code: {response.status_code}")
        print(response.text)
    
    return {"status" : "finished"}


@app.post("/receive_payement/")
def receive_payement(payement_data: Api.PayementResponse):
    print(payement_data)
    print("Payement reçu, GG!")
