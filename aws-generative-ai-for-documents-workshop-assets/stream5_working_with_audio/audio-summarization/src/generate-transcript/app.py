import boto3
import uuid
import os
import json
import time

INPUT_BUCKET = os.environ.get('INPUT_BUCKET')
AUDIO_PREFIX = os.environ.get('AUDIO_PREFIX') 
TRANSCRIPT_PREFIX = os.environ.get('TRANSCRIPT_PREFIX')
PODCAST_TABLE = os.environ.get('PODCAST_TABLE')
PRESIGNED_URL_EXPIRATION = os.environ.get('PRESIGNED_URL_EXPIRATION')

s3_client = boto3.client('s3')
ddb_client = boto3.resource("dynamodb").Table(PODCAST_TABLE)
transcribe = boto3.client('transcribe')

def lambda_handler(event, context):
# Convert audio file from AUDIO_INPUT_BUCKET to text and put the text in TRANSCRIPT_BUCKET. In case of error throw exception.
    job_name = f"GenerateAudioTranscript-{uuid.uuid4()}"
    audio_file_key = event['Records'][0]['s3']['object']['key']
    audio_file= audio_file_key.split('/')[1].split('.')
    audio_file_name = audio_file[0]
    audio_file_format = audio_file[1]
    
    
    audio_file_uri = f"s3://{INPUT_BUCKET}/{audio_file_key}"
    transcript_file_name = f"{audio_file_name}"
    transcript_file_key = f"{TRANSCRIPT_PREFIX}/{transcript_file_name}.json"
    
    print(f"Starting transcription job {job_name} for {audio_file_uri}")
    try:

#Add code here
        
        job = response['TranscriptionJob']
        print("Started transcription  job {}.".format(job_name))
        
        #create pre-signed url
        url = s3_client.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': INPUT_BUCKET,
                    'Key': audio_file_key,
                },
                ExpiresIn=PRESIGNED_URL_EXPIRATION
        )
        
        results = {
            "fileName": audio_file_name.strip(),
            "pre-signedURL": url
        }
        
        print(results)
        
        ddb_client.put_item(Item=results)
        
    except Exception:
        print("Error in starting transcription job")
        raise
     
    return {
        'statusCode': 200,
        'body': json.dumps('Started transcription job {}'.format(job_name))
    }
    



    

