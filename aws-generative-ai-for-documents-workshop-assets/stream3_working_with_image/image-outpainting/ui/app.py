import streamlit as st
import boto3
from htmlTemplates import css, bot_template, user_template
import os
import config
import ui_params
from requests_auth_aws_sigv4 import AWSSigV4
import requests
import json
from PIL import Image
from io import BytesIO


s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')


st.set_page_config(page_title="Podcast Summarization", page_icon=":books::parrot:", layout="wide")
st.write(css, unsafe_allow_html=True)

if 'clicked' not in st.session_state:
    st.session_state.clicked = False

#Upload image file to S3 bucket 
def upload_image_to_S3(image_file, image_file_name):

    try:
        s3.upload_fileobj(image_file, config.IMAGE_BUCKET, f'{config.IMAGE_PREFIX}/{image_file_name}')
        return True
    except FileNotFoundError:
        st.error('File not found.')
        return False  
        

#Detect labels from image and display in streamlit for user to select
def detect_labels(image_data):
    
    # Invokde rekongnition API to detect labels
    response = rekognition.detect_labels(Image={'Bytes': image_data})
    labels = []
    
    for label in response['Labels']:
        if len(label['Instances']) >0 :
            labels.append(label["Name"])
    
    return labels

# Calls Lambda function     
def invoke_lambda_function_endpoint(request):
    aws_auth = AWSSigV4('lambda')
    json_payload = json.dumps(request)
    headers = {'Content-Type': 'application/json'}
    response = requests.post(config.LAMBDA_FUNCTION_URL_ENDPOINT,auth=aws_auth, data=json_payload, headers=headers)
    return response
    
def click_button():
    st.session_state.clicked = True    

c1, c2, c3 = st.columns(3)

with c1:

    uploaded_image = st.file_uploader("Select an image file", ['png', 'jpg'])
    st.subheader("Prompt")
    
    prompt = st.text_area("Type in your prompt here:")
    
    if uploaded_image is not None:
        image_data = uploaded_image.getvalue()
        # Display labels
        labels = detect_labels(image_data)
        selected_labels = st.multiselect("Remove label from the list if you don't want to retain in generated image", labels, default=labels)
        
        st.button("Generate image", on_click=click_button)    

    

with c2:
    
    st.subheader("Input image")
    
    if uploaded_image is not None:
        st.image(uploaded_image)

with c3:
    st.subheader("Output image")
    
    if st.session_state.clicked:
        
        with st.spinner('Generating image...'):
            
            try:
                if uploaded_image is not None:
                    # Upload image to S3
                    upload_image_to_S3(uploaded_image, uploaded_image.name)
                    
                    # Prepare request to Lambda funtion url call
                    request = {
                    'ImageFileName': uploaded_image.name,
                        'Labels': selected_labels,
                        'Prompt': prompt

                    }
                        
                    # Call Lambda function
                    response = invoke_lambda_function_endpoint(request)
                    response_json = response.json()
                    print(response_json)
                    if response_json['StatusCode'] == 200:
                        image_file_key = response_json['Body']['Results']['ImageS3Key']
                        image_response = s3.get_object(Bucket=config.IMAGE_BUCKET, Key=image_file_key)
                        image_data = image_response['Body'].read()
                        st.image(image_data)
                    elif response_json['StatusCode'] == 500:
                        error = response_json['Body']['Message']
                        st.warning(error)
                    else:
                        st.warning("Error in generating image, returned status code {response.status_code}")

                    
            except Exception as e:
                st.error(e)
                raise        
