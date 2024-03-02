import sqlite3
import streamlit as st
import requests
import pika
import json
import time

base_url = "http://localhost:8000"
fournisseur_url = "http://localhost:8002"

# Connect to RabbitMQ server
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Function to fetch data from SQLite database
def fetch_data():
    conn = sqlite3.connect('test4.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders ORDER BY idcommande DESC')
    orders_data = cursor.fetchall()
    conn.close()
    return orders_data

def process_order(order_data):
    print("Processing the order...")
    order_data = transform_data(order_data)
    order_endpoint = f"{fournisseur_url}/check_order/"
    response = requests.post(order_endpoint, json=order_data)
    print(response.text)

def refuse_order(order_data):
    print("Refusing the order...")
    order_data = transform_data(order_data)
    order_endpoint = f"{base_url}/validate_order/{order_data['idcommande']}/refused"
    response = requests.post(order_endpoint)
    print(response.text)

# Function to transform data
def transform_data(data):
    transformed_data = {
        'idcommande': data[0],
        'product_id': int(data[1]),
        'quantity': data[2],
        'customer_name': data[3],
        'state': data[4]
    }
    return transformed_data

# Connect to SQLite database
conn = sqlite3.connect('test4.db')

# Display data in a Streamlit table with buttons
st.title("Orders Table")

# Store initial orders data
orders_data = fetch_data()

# Placeholder for triggering Streamlit update
refresh_placeholder = st.empty()

while True:
    st.write("---")
    for row in orders_data:
        st.write(f"Order ID: {row[0]}, Product ID: {row[1]}, Quantity: {row[2]}, Customer Name: {row[3]}, State: {row[4]}")
        if row[4] == 'Pending':
            # Buttons for validation and refusal
            validate_key = f"validate_{row[0]}"
            refuse_key = f"refuse_{row[0]}"
            validate = st.button("Validate", key=validate_key)
            refuse = st.button("Refuse", key=refuse_key)
            
            if validate:
                process_order(row)
                orders_data = fetch_data()  # Refresh data
                refresh_placeholder.empty()
                st.rerun()  # Force Streamlit to rerun the entire script
            elif refuse:
                refuse_order(row)
                orders_data = fetch_data()  # Refresh data
                refresh_placeholder.empty()
                st.rerun()  # Force Streamlit to rerun the entire script

        st.write("---")
    # Sleep for a short duration before refreshing data
    time.sleep(5)
    st.rerun()

# Close the database connection
conn.close()
