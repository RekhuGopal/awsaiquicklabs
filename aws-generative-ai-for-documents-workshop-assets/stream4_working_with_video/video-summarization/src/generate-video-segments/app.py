import boto3
import os
import json
import subprocess
import shlex


VIDEO_PROCESSING_STAGING_PREFIX = os.environ.get('VIDEO_PROCESSING_STAGING_PREFIX')
VIDEO_SUMMARY_FILES_PREFIX = os.environ.get('VIDEO_SUMMARY_FILES_PREFIX')

s3_client = boto3.client('s3')

def lambda_handler(event, context):

    print(event)


    try:
        
        # Generate clips
        segments_json = create_segment_files(event)

    except Exception:
        print("Error in parsing segments")
        raise
     
    return segments_json


