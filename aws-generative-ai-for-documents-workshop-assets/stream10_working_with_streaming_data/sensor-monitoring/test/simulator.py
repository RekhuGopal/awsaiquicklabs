import boto3
import json
import random
import time
import argparse


kinesis_client = boto3.client('kinesis')

#Write a method to simulate temperature, humidity and air quality index
def generate_data(probability):

    temperature = random.randint(0, 30)
    humidity =random.randint(40, 59)
    air_quality_index = random.randint(0, 50)
    
    # Occasionally generate higher  values
    if random.random() < probability:  
        temperature = random.randint(35, 80)
        humidity =  random.randint(65, 100)
        air_quality_index = random.randint(101, 200)
    
    data = {
        'temperature': temperature,
        'humidity': humidity,
        'air_quality_index': air_quality_index,
        'timestamp': int(time.time())
    }

    return json.dumps(data)

def send_data_to_kinesis(stream_name, data):

    # Put simulated data into Kinesis stream
    response = kinesis_client.put_record(
        StreamName=stream_name,
        Data=data,
        PartitionKey='partition_key'
    )

    print(response)
    print(f"Data sent to Kinesis. ShardId: {response['ShardId']}, SequenceNumber: {response['SequenceNumber']}, Data: {data}")
    
def simulate_data_for_duration(stream_name, duration_minutes, probability):
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)

    while time.time() < end_time:
        simulated_data = generate_data(probability)
        send_data_to_kinesis(stream_name, simulated_data)
        time.sleep(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate data and send it to Kinesis.")
    parser.add_argument("--stream_name", required=True, help="Name of the Kinesis stream.")
    parser.add_argument("--duration_minutes", type=int, required=True, help="Duration of the simulation in minutes.")
    parser.add_argument("--probability", type=float, required=True, help="Probability of occasionally generate higher values for temperature, humidity, air quality index")

    args = parser.parse_args()

    simulate_data_for_duration(args.stream_name, args.duration_minutes, args.probability)
