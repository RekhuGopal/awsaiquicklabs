from gremlin_python.structure.graph import Graph
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.graph_traversal import __
import boto3
import json
import os

g = None
remoteConn = None
connection_string = os.environ.get('NEPTUNE_CONNECTION_STRING')

# Function to create and populate the graph
def create_graph():
    global g
    global remoteConn
    graph = Graph()
    remoteConn = DriverRemoteConnection(connection_string, 'g')
    g = graph.traversal().withRemote(remoteConn)
    
    print('Connection created.')

    # Clearing out all the vertices to start fresh
    g.V().drop().iterate()
    print('Deleting everything and starting clean.')
    
    # Ingest data from fashion_data.txt
    with open("data/fashion_data.txt", 'r') as file:
        lines = file.readlines()
        
        reading_nodes = True
        
        for line in lines:
            line = line.strip()
            
            # Skip comments and empty lines
            if line.startswith("#") or not line:
                if "Edges" in line:
                    reading_nodes = False
                continue
            
            if reading_nodes:
                # Ingest nodes
                node_data = line.split(", ")
                if node_data[0] == "product":
                    g.addV(node_data[0]).property('name', node_data[1]).property('color', node_data[2]).property('brand', node_data[3]).property('size', node_data[4]).property('price', node_data[5]).next()
                elif node_data[0] == "brand":
                    g.addV(node_data[0]).property('name', node_data[1]).property('origin', node_data[2]).next()
                elif node_data[0] == "category":
                    g.addV(node_data[0]).property('name', node_data[1]).next()
            else:
                edge_data = line.split(", ")
                if edge_data[0] == 'product':
                    source_vertex = g.V().has(edge_data[0], 'name', edge_data[1])
                else:
                    source_vertex = g.V().has(edge_data[0], 'type', edge_data[1])
                
                source_vertex.addE(edge_data[2]).to(__.V().has(edge_data[3], 'name', edge_data[4])).next()

    print('Data ingestion complete.')

def test_query():
    fashionista_products = g.V().has('brand', 'name', 'Fashionista').in_('belongs_to_brand').valueMap().toList()

    # Print the results
    print("\nPerforming a sample query...")
    print("Products under the brand 'Fashionista':")
    for product in fashionista_products:
        product_name = product.get('name')[0]
        color = product.get('color')[0]
        size = product.get('size')[0]
        price = product.get('price')[0]
        print(f"Type: {product_name}, Color: {color}, Size: {size}, Price: ${price}")

def close_connection():
    global remoteConn  # Use the global remoteConn variable

    # Closing the connection
    if remoteConn:
        remoteConn.close()
        print('\nConnection closed')

if __name__ == "__main__":
    create_graph()
    test_query()
    close_connection()