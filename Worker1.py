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

# Declare the same queue
channel.queue_declare(queue='MQ1')

def process_order(order_data):
    print("Processing the order...")
    order_endpoint = f"{fournisseur_url}/check_order/"
    response = requests.post(order_endpoint, json=order_data)
    print(response.text)


def callback(ch, method, properties, body):
    order_data = json.loads(body)
    print(f" [x] Received {order_data}")

    user_input = input("Proceed? (Y/N): ").strip().upper()

    if user_input == "Y":
        # Start a new thread for processing the order
        thread = threading.Thread(target=process_order, args=(order_data,))
        thread.start()

        print("Exiting the function without waiting for the API response.")

    elif user_input == "N":
        print("Order not processed.")
    else:
        print("Invalid input. Please enter 'Y' or 'N.'")


# Set up the consumer and specify the callback function
channel.basic_consume(queue='MQ1', on_message_callback=callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
