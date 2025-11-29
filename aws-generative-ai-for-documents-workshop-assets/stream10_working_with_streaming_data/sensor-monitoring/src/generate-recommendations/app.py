import boto3
import os
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Attr
import base64
import json

JOBS_TABLE = os.environ.get('JOBS_TABLE')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN') 
BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID')
REGION = os.environ.get('AWS_REGION')

ddb_client = boto3.resource("dynamodb").Table(JOBS_TABLE)
bedrock_client = boto3.client(service_name='bedrock-runtime', region_name=REGION)
sns_client = boto3.client("sns")


def lambda_handler(event, context):

    try:

        notes = fetch_notes()
       
        
        for record in event['Records']:
            
            # Kinesis data is base64 encoded so need to decode
            data = base64.b64decode(record['kinesis']['data']).decode('utf-8')
            data_json = json.loads(data)
            temperature = data_json['temperature']
            humidity = data_json['humidity']
            air_quality_index = data_json['air_quality_index']
            
            if temperature > 30 or not (40 <= humidity <= 59) or air_quality_index >50:
                print("Sending recommendtaions.")
                prompt = build_prompt_text(temperature,humidity,air_quality_index,format_notes(notes))
                send_recommendations(prompt)
                print("Notification email sent successfully.")

        
    except Exception as e:
        #if any error discard message and continue with the next message in Kinesis
        print(f"Error processing message: {str(e)}. Continuing with the next message")

     
def invoke_endpoint(json):
    print(f"Request: {json}")
    response = bedrock_client.invoke_model(body=json, modelId=BEDROCK_MODEL_ID, accept='application/json', contentType='application/json')
    return response
    
def parse_response(response):
    responce_body = json.loads(response.get('body').read())
    print(f"Response body: {responce_body}")
    generated_text = responce_body['content'][0]['text']
    start_index = generated_text.find('<recommendation>') + len('<recommendation>')
    end_index = generated_text.find('</recommendation>', start_index)
    
    return generated_text[start_index:end_index]  

# Write a python method to fetch notes from JobsTable DynamoDB table for last 15 days
def fetch_notes():
    start_date = (datetime.now() - timedelta(days=15)).isoformat()
    filter_expression = Attr('completionDate').gte(start_date)
    response = ddb_client.scan(FilterExpression=filter_expression)
    items = response.get('Items', [])
    notes = [{'note': item.get('notes', None), 'completionDate': item.get('completionDate', None)} for item in items]
    return notes

def format_notes(notes):
    formatted_notes = ''

    for index, notes in enumerate(notes, 1):
        note = notes['note']
        completion_date= notes['completionDate']
        formmated_completion_date = datetime.fromisoformat(completion_date)
        formmated_completion_date = formmated_completion_date.strftime('%B %d, %Y')
        print(formmated_completion_date)
        formatted_note = f"Note {index}: [{formmated_completion_date}] - {note} \n"
        formatted_notes = formatted_notes + formatted_note

    formatted_notes = formatted_notes.rstrip('\n')
    return formatted_notes
    
def format_email_body(recommendations):
    message_text = f"Dear Facility Manager, \n {recommendations} \n Regards,\n Your AI Assistant"
    subject_text = "Facility update: Action required for climate control"


def build_prompt_text(temperature, humidity, air_quality_index,notes):
    
    prompt=f'''Provide detailed recommendations based on the latest  live streaming sensor data captured in a smart building environment. 
Temperature (°C): {temperature}
Humidity Data (%): {humidity}%
Air Quality Index (AQI): {air_quality_index}
Below are the acceptable values:
Temperature: between 0 to 30
Humidity: between 40 to 59
Air Quality Index (AQI): between 0 to 50
Here are the important notes from the past data:
{notes}
Here are some important rules for generating recommendations:
- Your recommendations should address any identified anomalies and suggest optimizations for maintaining a comfortable and healthy indoor environment. 
- Based on the above data and past data, generate actionable and meaningful recommendations. These recommendations should reflect the learned patterns, predictive insights, or potential outcomes derived from the historical data.
- Leverage the notes to guide the generated content. Formulate recommendations in a manner that aligns with the key takeaways, trends, or significant events highlighted in the provided notes.
- Ensure that the recommendations are comprehensive, relevant. Strive for actionable suggestions that reflect an understanding of the patterns and correlations present in the past information.
- Don't ask for additional questions.
- Don't ask follow-up questions.
Please encapsulate the entire recommendations text in <recommendation></recommendation> tags.'''
    
    return prompt

#Add code here
    

