# ask_senacor
simple streamlit app interaction with content from website and confluence webpages.

### Chat with your documents 🚀
- [Azure OpenAI model](https://azure.microsoft.com/de-de/products/ai-services/openai-service) as Large Language model
- [Azure AI Search](https://azure.microsoft.com/de-de/products/ai-services/ai-search) as Vector Storage
- [LangChain](https://python.langchain.com/en/latest/modules/models/llms/integrations/huggingface_hub.html) as a Framework for LLM
- [Streamlit](https://streamlit.io/) for deploying.

## System Requirements

You must have Python 3.9 or later installed. Earlier versions of python may not compile.  

---

## Steps to Replicate 

1. Fork this repository
```
git clone https://github.com/Hatsch-code/ask_senacor.git
```

2. Rename example.env to .env and adapt the variables with your personal ones
   ```
    CONFLUENCE_URL=https://***
	CONFLUENCE_USERNAME=YOUR CONFLUENCE USERNAME
	CONFLUENCE_TOKEN=YOUR CONFLUENCE TOKEN

	YOUR_AZURE_SEARCH_ENDPOINT=YOUR AZURE SEARCH ENDPOINT
	YOUR_AZURE_SEARCH_ADMIN_KEY=YOUR AZURE SEARCH ADMIN KEY

	AZURE_OPENAI_API_KEY=YOUR OPENAI API KEY
	AZURE_OPENAI_ENDPOINT=YOUR OPENAI ENDPOINT
   ```
   
3. Create a virtualenv and activate it
   ```
   python3 -m venv .venv && source .venv/bin/activate
   ```

4. Run the following command in the terminal to install necessary python packages:
   ```
   pip install -r requirements.txt
   ```

5. Run the following command in your terminal to start the chat UI:
   ```
   streamlit run 01_Direct_Query.py
   ```
