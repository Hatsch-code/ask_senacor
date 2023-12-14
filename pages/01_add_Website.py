import os
import traceback
import streamlit as st
from dotenv import load_dotenv
from vector_storage import add_website_to_vector_store, add_confluence_to_vector_store


# Load environment variables from .env file (Optional)
load_dotenv()

CONFLUENCE_URL = os.getenv("CONFLUENCE_URL", None)


def setup_ui():
    # Set the title of the app
    st.title('🦜🔗 Add Website')


try:
    setup_ui()
    url = st.text_input("Insert The website URL")
    if st.button("Add Website", type="secondary"):
        # Add the website and crawl over all subpages to the vector store
        add_website_to_vector_store(url)

    if CONFLUENCE_URL and st.button("Add Confluence", type="secondary"):
        # Add defined confluence pages to the vector store
        add_confluence_to_vector_store()

except Exception:
    st.error(traceback.format_exc())