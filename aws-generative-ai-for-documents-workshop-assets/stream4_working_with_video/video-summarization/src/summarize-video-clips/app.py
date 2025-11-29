import boto3
import os
import json
import uuid


VIDEO_PROCESSING_STAGING_PREFIX = os.environ.get('VIDEO_PROCESSING_STAGING_PREFIX')
VIDEO_SUMMARY_FILES_PREFIX = os.environ.get('VIDEO_SUMMARY_FILES_PREFIX')
BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID')
REGION = os.environ.get('AWS_REGION')

s3 = boto3.client('s3')
bedrock = boto3.client(service_name='bedrock-runtime', region_name=REGION)


def lambda_handler(event, context):

    print(event)


    try:
        
        # Summarize transcripts
        summarize_transcripts(event)

    except Exception:
        print("Error in summarizing transcripts")
        raise
    

        

def invoke_endpoint(json):
    print(f"Request: {json}")
    response = bedrock.invoke_model(body=json, modelId=BEDROCK_MODEL_ID, accept='application/json', contentType='application/json')
    return response


def parse_response(response):
    responce_body = json.loads(response.get('body').read())
    print(f"Response body: {responce_body}")
    generated_text = responce_body['content'][0]['text']
    return generated_text        
    


    