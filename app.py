import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

load_dotenv()

def fetch_notion_content(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    
    # Wait for content to load and expand all toggles
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "notion-page-content"))
    )
    time.sleep(5)  # Additional wait for dynamic content
    
    # Expand all toggles
    toggles = driver.find_elements(By.CSS_SELECTOR, "[role='button']")
    for toggle in toggles:
        try:
            toggle.click()
            time.sleep(0.5)
        except:
            pass
    
    # Get all text content
    content = driver.find_element(By.CLASS_NAME, "notion-page-content").text
    driver.quit()
    return content

@st.cache_data
def load_api_docs():
    discovery_api_url = "https://crustdata.notion.site/Crustdata-Discovery-And-Enrichment-API-c66d5236e8ea40df8af114f6d447ab48"
    dataset_api_url = "https://crustdata.notion.site/Crustdata-Dataset-API-Detailed-Examples-b83bd0f1ec09452bb0c2cac811bba88c"
    
    return f"""
    Discovery API: {fetch_notion_content(discovery_api_url)}
    Dataset API: {fetch_notion_content(dataset_api_url)}
    """

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
st.title("Crustdata API Support")

if "messages" not in st.session_state:
    api_docs = load_api_docs()
    st.session_state.messages = [{"role": "system", "content": f"""You are a helpful API support chatbot for Crustdata. Answer questions based on this documentation:

{api_docs}"""}]

for message in st.session_state.messages[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about Crustdata's APIs"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response = client.chat.completions.create(
        model="gpt-4",
        messages=st.session_state.messages,
        temperature=0
    )

    assistant_response = response.choices[0].message.content
    with st.chat_message("assistant"):
        st.markdown(assistant_response)
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})