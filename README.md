# "AskSenacor" Prototype
Simple streamlit app that allows you to interact with websites and confluence pages.

### Components
- [Confluence](https://www.atlassian.com/software/confluence) as data source
- [Azure AI Search](https://azure.microsoft.com/de-de/products/ai-services/ai-search) as vector storage
- [Azure OpenAI](https://azure.microsoft.com/de-de/products/ai-services/openai-service) as embeddings model and LLM
- [LangChain](https://python.langchain.com/en/latest/modules/models/llms/integrations/huggingface_hub.html) as framework to orchestrate components
- [Streamlit](https://streamlit.io/) for creating the UI
- (optional) [SkyPilot](https://skypilot.readthedocs.io/en/latest/) for deploying a self-hosted LLM

## System Requirements

- You must have Python 3.9 or later installed. Earlier versions of python may not compile
- You must have an Azure subscription and access to Azure OpenAI service

---

## Steps to Replicate (with Azure OpenAI)

1. Setup Azure AI Search
   - Create an Azure AI Search resource in your subscription
   - Note down your AI Search endpoint and admin key
   - Create an index

2. Setup Azure OpenAI
   - Create an Azure OpenAI resource in your subscription
   - Note down your Azure OpenAI endpoint and key
   - Open Azure OpenAI Studio and deploy two models:
     - `text-embedding-ada-002` (or later) as embeddings model
     - `gpt-35-turbo` (or later) as large language model

3. Setup confluence access
   - Create a confluence user with appropriate access
   - Note down your confluence URL, username, and user token

4. Fork this repository
   ```
   git clone https://github.com/Hatsch-code/ask_senacor.git
   ```

5. Rename example.env to .env and adapt the variables with your personal ones
   ```
   CONFLUENCE_URL = <your Confluence url>
   CONFLUENCE_USERNAME = <your Confluence username>
   CONFLUENCE_TOKEN = <your Confluence token>
   
   YOUR_AZURE_SEARCH_ENDPOINT = <your Azure AI Search endpoint>
   YOUR_AZURE_SEARCH_ADMIN_KEY = <your Azure AI Search admin key>
   
   AZURE_OPENAI_ENDPOINT = <your Azure OpenAI endpoint>
   AZURE_OPENAI_API_KEY = <your Azure OpenAI key>
   ```
   
6. Create a virtualenv and activate it
   ```
   python3 -m venv .venv && source .venv/bin/activate
   ```

7. Run the following command in the terminal to install necessary python packages:
   ```
   pip install -r requirements.txt
   ```

8. Run the following command in your terminal to start the UI:
   ```
   streamlit run 01_Direct_Query.py
   ```

---

## Steps to Replicate (with open-source self-hosted LLM)

1. Install SkyPilot
   ```
   pip install -U "skypilot-nightly[azure]"
   ```
2. Setup access to Azure
   ```
   az login
   az account set -s <your Azure subscription ID>
   ```
3. Check that SkyPilot access to Azure is enabled
   ```
   sky check
   ```
4. Configure SkyPilot to use [all regions](https://skypilot.readthedocs.io/en/latest/reference/faq.html#advanced-how-to-make-skypilot-use-all-global-regions), because we will use West Europe
   ```
   bash update_skypilot.sh
   ```
5. If necessary, [increase the quotas](https://skypilot.readthedocs.io/en/latest/cloud-setup/quota.html) for VMs with A10 GPU

6. Create the VMs and deploy Mistral-7B-instruct as LLM.
   Mistral's original YAML included "A10G" accelerators, but it seems they're not available on Azure.
   Thus, we changed the requirements to "A10".
   ```
   sky launch -c asksenacor-mistral mistral.yaml --region westeurope
   ```
7. Check status
   ```
   sky status --ip asksenacor-mistral
   ```
8. Check if Mitral LLM is running
   ```
   curl http://$IP:8000/v1/completions \
   -H "Content-Type: application/json" \
   -d '{
      "model": "mistralai/Mistral-7B-Instruct-v0.2",
      "prompt": "My favourite condiment is",
      "max_tokens": 25
   }'
   ```
8. Configure langchain to use Mistral LLM instead of Azure OpenAI

9. Stop (some billing still occurs) or terminate (no billing occurs anymore) the instances
   ```
   sky stop asksenacor-mistral
   sky down asksenacor-mistral
   ```
