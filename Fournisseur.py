import Api
from fastapi import FastAPI, BackgroundTasks
import requests
import pika
import json

app = FastAPI()

base_url = "http://localhost:8000"
fournisseur_url="http://localhost:8002"
client_url="http://localhost:8001"


def order_mq_order(order_data : Api.OrderResponse) :

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='MQ1')

    message = json.dumps(order_data)
    channel.basic_publish(exchange='', routing_key='MQ1', body=message)

    print(f" [x] Sent '{message}'")

    connection.close()
        
def order_mq_devis(order_data : Api.OrderResponse):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='MQ2')

    message = json.dumps(order_data)
    channel.basic_publish(exchange='', routing_key='MQ2', body=message)

    print(f" [x] Sent '{message}'")

    connection.close()



@app.post("/generate_devis/")
def generate_devis(order_data : dict):

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
        #background_tasks.add_task(order_mq_order,response.json())
    else:
        # Failed to place order
        print(f"Failed to place order. Status Code: {response.status_code}")
        print(response.text)
    
    return {"status" : "finished"}



@app.post("/check_order/")
def check_order(order_data : dict, background_tasks: BackgroundTasks):
    product_id=order_data["product_id"]
    quantity=order_data["quantity"]
    order_endpoint = f"{base_url}/check_order?product_id={product_id}&quantity={quantity}"
    response = requests.post(order_endpoint)
    response_json = response.json()
    print(response_json)
    if response_json["status"] == "Available":
        # Order verified successfully
        print("Order verified successfully")
        
        order_endpoint = f"{base_url}/validate_order/{order_data['idcommande']}/{'validated'}"
        response = requests.post(order_endpoint)
        print(response)
        response_json=response.json()

        order_endpoint = f"{client_url}/receive_validation"
        response = requests.post(order_endpoint,json=response_json)
        background_tasks.add_task(order_mq_devis,order_data)

    else:
        # Failed to verify order, print error details
        print(f"Failed to verify order. Status: {response_json['status']}, Message: {response_json['message']}")

        order_endpoint = f"{base_url}/validate_order/{order_data['idcommande']}/{'refused'}"
        response = requests.post(order_endpoint)


@app.post("/receive_payement/")
def receive_payement(payement_data: Api.PayementResponse):
    print(payement_data)
    print("Payement reçu, GG!")
