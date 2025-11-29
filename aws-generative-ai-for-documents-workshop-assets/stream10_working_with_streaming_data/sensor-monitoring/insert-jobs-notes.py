import boto3
from datetime import datetime, timedelta

#Write python method to insert into DynamoDB table with columns column jobId, jobDescription, status, notes, assignedTo
def insert_data_dynamodb(job_id, job_description, status, completion_date, notes, assigned_to):
    # Initialize DynamoDB client
    dynamodb = boto3.resource('dynamodb') 
    table = dynamodb.Table("JobsTable")

    # Define the item to be inserted
    item = {
        'jobId': job_id,
        'jobDescription': job_description,
        'status': status,
        'completionDate': completion_date,
        'notes': notes,
        'assignedTo': assigned_to
    }

    # Insert the item into DynamoDB
    table.put_item(Item=item)
    
    print(f'Jobs {job_id} created successfully')

# Calculate completion date as 7 days back from the current date
completion_date = datetime.now() - timedelta(days=7)

# Insert job#1
insert_data_dynamodb(
    job_id=1,
    job_description='Building is too hot. Optimize cooling.',
    status='Completed',
    completion_date=completion_date.isoformat(),
    notes='The HVAC system was recalibrated to optimize cooling, additional ventilation was introduced.',
    assigned_to='John Doe'
)

# Calculate completion date as 7 days back from the current date
completion_date = datetime.now() - timedelta(days=14)

# Insert job#2
insert_data_dynamodb(
    job_id=2,
    job_description='Direct sunligh exposure',
    status='Completed',
    completion_date=completion_date.isoformat(),
    notes='Sun-shading elements were installed to mitigate direct sunlight exposure.',
    assigned_to='Jane Colin'
)