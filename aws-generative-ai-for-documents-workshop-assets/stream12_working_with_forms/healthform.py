
import argparse

import boto3
import pprint
from botocore.client import Config
import json
import re

pp = pprint.PrettyPrinter(indent=4)

def get_bedrock_client():
    session = boto3.session.Session()
    region = session.region_name
    bedrock_config = Config(connect_timeout=120, read_timeout=120, retries={'max_attempts': 0})
    bedrock_client = boto3.client('bedrock-runtime', 
                                  region_name = region)
    
    return bedrock_client

def invoke_claude_llm(bedrock_client,
                      messages,
                      modelId ='anthropic.claude-3-sonnet-20240229-v1:0',
                      accept = 'application/json',
                      contentType = 'application/json',
                      max_tokens = 4096,
                      temperature = 0,
                     ):

    payload = json.dumps({
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": max_tokens,
    "temperature": temperature,
    "top_p": 0,
    "messages": messages})
    
    response = bedrock_client.invoke_model(
        body=payload, 
        modelId=modelId, 
        accept=accept, 
        contentType=contentType)
    
    response_body = json.loads(response.get('body').read())
    response_text = response_body.get('content')
    
    return response_text

def get_image_payload(image_path=None):
    import os
    import base64
    from pathlib import Path
    
    content=None
    if image_path:
        image_path = Path(image_path)
        _,ext=os.path.splitext(image_path)
        if "jpg" in ext: ext=".jpeg"
        with open(image_path, "rb") as image_file:
            binary_data = image_file.read()
            base_64_encoded_data = base64.b64encode(binary_data)
            base64_string = base_64_encoded_data.decode('utf-8')
            content= {
                          "type": "image",
                          "source": {
                            "type": "base64",
                            "media_type": f"image/{ext.lower().replace('.','')}",
                            "data": base64_string
                          }
                        }
    return content

def get_text_payload(text=None):
    content=None
    if text.strip():
        content = {
        "type":"text",
        "text": text.strip()
        }
    return content

def create_claude_message(prompt):
    import re
    content = []
    
    matches = re.split(r"(<img>.*?</img>)", prompt, flags=re.DOTALL|re.MULTILINE)
    for l in matches :
        if '<img>' not in l :
            content.append(get_text_payload(l))
        else:
            image_file = re.search('<img>(.*)</img>',l , re.MULTILINE | re.DOTALL).groups(0)[0]
            content.append(get_image_payload(image_file))
    
    messages = [
                { "role":"user", 
                  "content":content
                }]
    return messages

SystemPromptTemplate = """
<Task_Description>
You have been provided a baseline health form template image without any markings:

Baseline Image: <img>{original_template}</img>
Baseline Image Description: An image representing an empty health form template.

You will also be given a scanned image of a filled-out version of the same health form template. Your task is to compare the scanned image with the baseline template and identify which options have been marked by hand, as well as extract any handwritten text on the scanned form. This form may contain handwritten text like dates.

Please use below process to identify the marking by hand:
1. Go through the form section by section, examining each area methodically.
2. For each section, check if any options have been marked by hand (circled, boxed, underlined,lined etc.) and identify the corresponding text/values.
3. Also look for any handwritten text entries and determine which field or section they belong to.
4. Cross-reference the scanned image with the baseline template to accurately capture what has been filled out or modified.
5. Organize all the extracted information in a clear JSON formats. The key should be short but human readable, capitalized for each word and seperated by _

</Task_Description>

<Input>
- Scanned Image: <img>{input_img}</img>
- Scanned Image Description: An image of the same health form template, but with various options marked or filled out, and potentially handwritten text.
</Input>

<Output>
Generate a structured JSON output indicating the following:
1. The options and fields that have been marked or filled out on the scanned form compared to the baseline template, including field names and their corresponding values.
2. Any handwritten text detected on the scanned form, organized by the corresponding field or section it appears in.
</Output>

<Evaluation>
Your output will be evaluated based on:
1. Accuracy in identifying the marked/filled options and fields on the scanned form.
2. Accuracy in extracting and transcribing handwritten text from the scanned form.
3. Clarity and usability of the structured JSON output format.
</Evaluation>

<Instructions>
Please examine the provided input image completely and carefully, and then generate the most accurate and well formated JSON response indicating the marked or filled out options and fields, as well as any handwritten text compared to the baseline template.
</Instructions>
"""

bedrock_client = get_bedrock_client()

def get_json(baseimg,scannedimg):
    prompt = SystemPromptTemplate.format(original_template=baseimg,
                                        input_img=scannedimg)
    # print(prompt)
    messages = create_claude_message(prompt)
    messages.append( {"role": "assistant", "content": ""})
    # messages
    response_text = invoke_claude_llm(bedrock_client,messages)
    resp = response_text[0]['text']
    print(resp)

    return  resp


if __name__ == "__main__":
    # Accept the argument from command line
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseImage", type=str, default="SampleData/Baseline-Template.png")
    parser.add_argument("--scanImage", type=str, default="SampleData/Sample-1.png")
    
    args = parser.parse_args()
    
    if args.baseImage:
        baseImage = args.baseImage
    if args.scanImage:
        scanImage = args.scanImage
    
    content = get_json(baseImage, scanImage)
    # print(content)