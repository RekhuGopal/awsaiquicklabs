import boto3
import uuid
import os
import json
import math

INPUT_BUCKET = os.environ.get('INPUT_BUCKET')
TRANSCRIPT_PREFIX = os.environ.get('TRANSCRIPT_PREFIX')
BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID')
PODCAST_TABLE = os.environ.get('PODCAST_TABLE')
REGION = os.environ.get('AWS_REGION')

s3_client = boto3.client('s3')
bedrock_client = boto3.client(service_name='bedrock-runtime', region_name=REGION)
ddb_client = boto3.resource("dynamodb").Table(PODCAST_TABLE)

def lambda_handler(event, context):

    print(event)
    
    # Load transcript
    transcript_file_key = event['Records'][0]['s3']['object']['key']
    transcript_file = transcript_file_key.split('/')[1].split('.')
    transcript_file_name = transcript_file[0]
    transcript_file_format = transcript_file[1]

    transcript_file_uri = f"s3://{INPUT_BUCKET}/{transcript_file_key}"

    transcript_response = s3_client.get_object(Bucket=INPUT_BUCKET, Key=transcript_file_key)
    transcript_data = transcript_response['Body'].read().decode('utf-8')

    # Parse the JSON data  
    transcript_json = json.loads(transcript_data)
    transcript = transcript_json['results']['transcripts'][0]['transcript']

    try:
        
#Add code here


        results = {
            "fileName": transcript_file_name.strip(),
            "title": title.strip(),
            "summary": summary.strip()
        }
        
        print(results)
        
        results = ddb_client.update_item(
            Key={'fileName': transcript_file_name.strip()},
            UpdateExpression="set title=:t, summary=:s",
            ExpressionAttributeValues={
                ':t': title.strip(),
                ':s': summary.strip()
            },
            
            ReturnValues="UPDATED_NEW"
        )
            
        
    except Exception as e:
        print('Error generating text')
        print(e)
        raise

    return {
        'statusCode': 200,
        'body': {
            'message': json.dumps('Completed summary job {}'.format(transcript_file_name)),
            'results': results
        }
    }

def invoke_endpoint(json):
    print(f"Request: {json}")
    response = bedrock_client.invoke_model(body=json, modelId=BEDROCK_MODEL_ID, accept='application/json', contentType='application/json')
    return response


def parse_response(response):
    responce_body = json.loads(response.get('body').read())
    print(f"Response body: {responce_body}")
    generated_text = responce_body['content'][0]['text']
    return generated_text
    

