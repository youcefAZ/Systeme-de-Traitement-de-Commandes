import pika
import json
import requests
import threading

base_url = "http://localhost:8000"
fournisseur_url="http://localhost:8002"
client_url="http://localhost:8001"

# Connect to RabbitMQ server
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

def process_devis(devis_data:dict):
    print("Processing the order...")
    order_endpoint = f"{fournisseur_url}/generate_devis/"
    response = requests.post(order_endpoint, json=devis_data)
    print(response.text)

# Declare the same queue
channel.queue_declare(queue='MQ2')

def callback(ch, method, properties, body):
    devis_data = json.loads(body)
    print(f" [x] Received {devis_data}")

    user_input = input("Create devis? (Y/N): ").strip().upper()

    if user_input == "Y":
        # Start a new thread for processing the order
        thread = threading.Thread(target=process_devis, args=(devis_data,))
        thread.start()

        print("Exiting the function without waiting for the API response for devis.")

    elif user_input == "N":
        print("Order not processed.")
    else:
        print("Invalid input. Please enter 'Y' or 'N.'")


# Set up the consumer and specify the callback function
channel.basic_consume(queue='MQ2', on_message_callback=callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
