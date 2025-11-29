import boto3
import json
import os

def send_logs_to_kinesis(log_lines, stream_name):
    # Initialize Kinesis client
    kinesis_client = boto3.client('kinesis')

    # Process and send each log line to Kinesis Data Stream in JSON format
    for line in log_lines:
        try:
            timestamp, log_level, message, host, thread, request_id = line.split(',')
            log_entry = {
                "timestamp": timestamp,
                "log_level": log_level,
                "message": message,
                "host": host,
                "thread": thread,
                "request_id": request_id
            }

            # Send the log entry to Kinesis
            response = kinesis_client.put_record(
                StreamName=stream_name,
                Data=json.dumps(log_entry),
                PartitionKey=request_id  # Using request_id as partition key, can be changed as needed
            )
            print(f"Record {response['SequenceNumber']} sent to shard {response['ShardId']}")
        
        except Exception as e:
            print(f"Error processing log line {line}. Error: {str(e)}")

def process_directory_for_logs(directory, stream_name):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".log"):  # Assuming log files have a .log extension
                with open(os.path.join(root, file), 'r') as f:
                    log_lines = f.readlines()
                    send_logs_to_kinesis(log_lines, stream_name)

stream_name = "logs_ingestion_to_firehose"
logs_directory = "logs"
process_directory_for_logs(logs_directory, stream_name)
