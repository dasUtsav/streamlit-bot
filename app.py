import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

load_dotenv()

def fetch_notion_content(url):
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    
    driver = uc.Chrome(options=options)
    
    try:
        driver.get(url)
        
        # Wait for content to load
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
                continue
        
        # Get content
        content = driver.find_element(By.CLASS_NAME, "notion-page-content").text
        return content
    
    finally:
        driver.quit()

@st.cache_data
def load_api_docs():
    try:
        discovery_api_url = "https://crustdata.notion.site/Crustdata-Discovery-And-Enrichment-API-c66d5236e8ea40df8af114f6d447ab48"
        dataset_api_url = "https://crustdata.notion.site/Crustdata-Dataset-API-Detailed-Examples-b83bd0f1ec09452bb0c2cac811bba88c"
        
        discovery_content = fetch_notion_content(discovery_api_url)
        dataset_content = fetch_notion_content(dataset_api_url)
        
        return f"""
        Discovery API Documentation:
        {discovery_content}
        
        Dataset API Documentation:
        {dataset_content}
        """
    except Exception as e:
        st.error(f"Error loading API documentation: {str(e)}")
        return "Error loading documentation. Using fallback content."

# Initialize OpenAI client with API key from environment or secrets
openai_api_key = os.getenv('OPENAI_API_KEY') or st.secrets['OPENAI_API_KEY']
client = OpenAI(api_key=openai_api_key)

# App title
st.title("Crustdata API Support")

# Initialize chat history with system prompt
if "messages" not in st.session_state:
    api_docs = load_api_docs()
    st.session_state.messages = [{"role": "system", "content": f"""You are a helpful API support chatbot for Crustdata. Answer questions based on this documentation:

{api_docs}"""}]

# Display chat history
for message in st.session_state.messages[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input and response
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

# Sidebar info
with st.sidebar:
    st.markdown("""
    ### About
    This chatbot helps you with questions about Crustdata's APIs:
    - Discovery And Enrichment API
    - Dataset API
    """)