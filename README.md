# ask_senacor
Simple streamlit app interaction with content from website and confluence webpages.

### Chat with your documents
- [Azure OpenAI Service](https://azure.microsoft.com/de-de/products/ai-services/openai-service) as Large Language model (LLM) and embeddings
- [Azure AI Search](https://azure.microsoft.com/de-de/products/ai-services/ai-search) as Vector Storage
- [LangChain](https://python.langchain.com/en/latest/modules/models/llms/integrations/huggingface_hub.html) as a Framework for LLM
- [Streamlit](https://streamlit.io/) for deploying

## System Requirements

- You must have Python 3.9 or later installed. Earlier versions of python may not compile
- You must have an Azure subscription and access to Azure OpenAI service

---

## Steps to Replicate (with Azure OpenAI LLM)

1. Setup Azure AI Search
   - Create an Azure AI Search resource in your subscription
   - Note down your AI Search endpoint and admin key
   - Create an index

2. Setup Azure OpenAI
   - Create an Azure OpenAI resource in your subscription
   - Note down your Azure OpenAI endpoint and key
   - Open Azure OpenAI Studio and deploy two models:
     - `text-embedding-ada-002` (or later) as model for embeddings
     - `gpt-35-turbo` (or later) as LLM

3. Setup confluence access
   - Create a confluence user with appropriate access
   - Note down your confluence URL, username, and user token

3. Fork this repository
   ```
   git clone https://github.com/Hatsch-code/ask_senacor.git
   ```

4. Rename example.env to .env and adapt the variables with your personal ones
   ```
   CONFLUENCE_URL = <your Confluence url>
   CONFLUENCE_USERNAME = <your Confluence username>
   CONFLUENCE_TOKEN = <your Confluence token>
   
   YOUR_AZURE_SEARCH_ENDPOINT = <your Azure Search endpoint>
   YOUR_AZURE_SEARCH_ADMIN_KEY = <your Azure Search admin key>
   
   AZURE_OPENAI_API_KEY = <your Azure OpenAI key>
   AZURE_OPENAI_ENDPOINT = <your Azure OpenAI endpoint>
   ```
   
5. Create a virtualenv and activate it
   ```
   python3 -m venv .venv && source .venv/bin/activate
   ```

6. Run the following command in the terminal to install necessary python packages:
   ```
   pip install -r requirements.txt
   ```

5. Run the following command in your terminal to start the chat UI:
   ```
   streamlit run 01_Direct_Query.py
   ```

---

## Steps to Replicate (with open-source self-hosted LLM)

1. Install SkyPilot