import streamlit as st
import boto3
import pandas as pd
from htmlTemplates import css, bot_template, user_template



ddb_client = boto3.resource("dynamodb").Table("PodcastSummaryTable")

response = ddb_client.scan()
data = response['Items']

st.set_page_config(page_title="Podcast Summarization", page_icon=":books::parrot:")

try:
    
    st.write(css, unsafe_allow_html=True)
    df=pd.DataFrame(data)
    
    records = df.to_dict("records")
    
    selected_data = st.selectbox('Please select podcast title:',options=records, format_func=lambda record: record['title'])
    
    st.write('**Title**:', selected_data['title'])    
    st.audio(selected_data['pre-signedURL'])
    st.write('**Summary**:\n', selected_data['summary'])
except:
    st.warning("Generating title and summary...")
    st.write("Please refresh after some time")


