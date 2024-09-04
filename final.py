import streamlit as st
import os
import io
import requests
from google.cloud import vision
from google.cloud.vision_v1 import types
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Set up environment variables
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"service_account_ocr.json"
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

headers = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

# Create a new page on notion
def create_page(data: dict):
    try:
        create_url = "https://api.notion.com/v1/pages"
        payload = {"parent": {"database_id": DATABASE_ID}, "properties": data}
        res = requests.post(create_url, headers=headers, json=payload)
        if res.status_code == 200:
            st.success("Entry successfully created in Notion.")
        else:
            st.error(f"Failed to create entry in Notion: {res.text}")
        return res
    except Exception as e:
        st.error(f"Error creating Notion entry: {e}")
        return None


#Detects text in the provided image content using Google Cloud Vision API.
def detect_document(image_content):

    client = vision.ImageAnnotatorClient()
    try:
        image = types.Image(content=image_content)
        response = client.document_text_detection(image=image)
        docText = response.full_text_annotation.text
        return docText
    except Exception as e:
        st.error(f"Error detecting text: {e}")
        return None
   

#Handles the image upload and processes the image to detect text.
def upload_image_and_process():

    uploaded_file = st.file_uploader("Choose an image...")
    if uploaded_file is not None:
        image_content = uploaded_file.getvalue()
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        return image_content
    return None


#Processes the uploaded image content to extract and display text.
def process_and_display_text(image_content):
   
    document_text = detect_document(image_content)
    if document_text:
        st.subheader(" Behold! The text has been conjured from the image by the sheer force of magic!")
        st.write(document_text)
        return document_text
    return None



def main():
   
    st.title("Handwritten Text Detection")
    st.write("Step forth, brave soul! Present your image to the mystical screen, and I shall summon the hidden words within!")

    image_content = upload_image_and_process()
    if image_content:
        with st.spinner('Processing the image...'):
            document_text = process_and_display_text(image_content)
            if document_text:
                Name = "New Entry"
                entry_date = datetime.now().astimezone(timezone.utc).isoformat()
                data = {
                    "Name": {"title": [{"text": {"content": Name}}]},
                    "Content": {"rich_text": [{"text": {"content": document_text}}]},
                    "Date of Entry": {"date": {"start": entry_date, "end": None}}
                }
                create_page(data)

if __name__ == "__main__":
    main()
