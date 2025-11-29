import boto3
import json
import mysql.connector

# Load the data from the JSON file
with open('./data/data.json', 'r') as file:
    data = json.load(file)

def get_secret(secret_name):
    # Initialize a session using Amazon Secrets Manager
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager')

    # Get the secret value
    get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    secret = get_secret_value_response['SecretString']
    return json.loads(secret)

# Fetch the secret values
secret_name = "mysql_secrets"
secret_values = get_secret(secret_name)

cursor = None
conn = None

try:
    # Connect to the MySQL server (without specifying a database)
    conn = mysql.connector.connect(
        host=secret_values['host'],
        user=secret_values['username'],
        password=secret_values['password'],
        port=secret_values['port']
    )
    cursor = conn.cursor()

    # Create the `sales` database
    cursor.execute("CREATE DATABASE IF NOT EXISTS sales")
    cursor.execute("USE sales")
    print("Database 'sales' created successfully!")

    # Create the `products` table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            ProductID INT PRIMARY KEY,
            ProductName VARCHAR(255) NOT NULL,
            Description TEXT,
            Price DECIMAL(10, 2) NOT NULL,
            StockQuantity INT NOT NULL,
            CategoryID INT
        )
    """)
    print("Table 'products' created successfully!")

    # Create the `customers` table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            CustomerID INT PRIMARY KEY,
            FirstName VARCHAR(255) NOT NULL,
            LastName VARCHAR(255) NOT NULL,
            Email VARCHAR(255) UNIQUE NOT NULL,
            Address TEXT,
            Phone VARCHAR(15)
        )
    """)
    print("Table 'customers' created successfully!")

    # Create the `orders` table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            OrderID INT PRIMARY KEY,
            CustomerID INT,
            ProductID INT,
            Quantity INT NOT NULL,
            OrderDate DATE NOT NULL,
            TotalPrice DECIMAL(10, 2) NOT NULL,
            FOREIGN KEY (CustomerID) REFERENCES customers(CustomerID),
            FOREIGN KEY (ProductID) REFERENCES products(ProductID)
        )
    """)
    print("Table 'orders' created successfully!")

    # Insert data into the `products` table
    for product in data['Products']:
        cursor.execute("""
            INSERT INTO products (ProductID, ProductName, Description, Price, StockQuantity, CategoryID)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (product['ProductID'], product['ProductName'], product['Description'], product['Price'], product['StockQuantity'], product['CategoryID']))
    print("Data inserted into 'products' table successfully!")

    # Insert data into the `customers` table
    for customer in data['Customers']:
        cursor.execute("""
            INSERT INTO customers (CustomerID, FirstName, LastName, Email, Address, Phone)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (customer['CustomerID'], customer['FirstName'], customer['LastName'], customer['Email'], customer['Address'], customer['Phone']))
    print("Data inserted into 'customers' table successfully!")

    # Insert data into the `orders` table
    for order in data['Orders']:
        cursor.execute("""
            INSERT INTO orders (OrderID, CustomerID, ProductID, Quantity, OrderDate, TotalPrice)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (order['OrderID'], order['CustomerID'], order['ProductID'], order['Quantity'], order['OrderDate'], order['TotalPrice']))
    print("Data inserted into 'orders' table successfully!")

    # Commit the transactions
    conn.commit()

except mysql.connector.Error as err:
    print(f"Error: {err}")
finally:
    # Close the connection
    if cursor:
        cursor.close()
    if conn:
        conn.close()