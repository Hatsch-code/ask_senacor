import os
from dotenv import load_dotenv

from langchain.document_loaders import WebBaseLoader, ConfluenceLoader
from langchain.embeddings import AzureOpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter

from langchain.vectorstores.azuresearch import AzureSearch
import requests
from bs4 import BeautifulSoup
from enum import Enum

# Load environment variables from .env file (Optional)
load_dotenv()

CONFLUENCE_URL = os.getenv("CONFLUENCE_URL", None)
CONFLUENCE_USERNAME = os.getenv("CONFLUENCE_USERNAME", None)
CONFLUENCE_API_KEY = os.getenv("CONFLUENCE_API_KEY", None)
CONFLUENCE_TOKEN = os.getenv("CONFLUENCE_TOKEN", None)

vector_store_address: str = os.getenv("YOUR_AZURE_SEARCH_ENDPOINT")
vector_store_password: str = os.getenv("YOUR_AZURE_SEARCH_ADMIN_KEY")


class ContentFormat(str, Enum):
    """Enumerator of the content formats of Confluence page."""

    EDITOR = "body.editor"
    EXPORT_VIEW = "body.export_view"
    ANONYMOUS_EXPORT_VIEW = "body.anonymous_export_view"
    STORAGE = "body.storage"
    VIEW = "body.view"

    def get_content(self, page: dict) -> str:
        return page["body"][self.name.lower()]["value"]


def print_semantic_similarity(question, vector_store, k=3, search_type="similarity"):
    # Can be used to test the semantic search function of the vector store
    docs = vector_store.similarity_search(
        query=question,
        k=k,
        search_type=search_type,
    )
    print(docs[0].page_content)


def init_vector_store(embeddings, index_name="langchain-vector-demo"):
    # Initialize the vector store, which is used to store and retrieve the source documents
    index_name: str = index_name
    vector_store: AzureSearch = AzureSearch(
        azure_search_endpoint=vector_store_address,
        azure_search_key=vector_store_password,
        index_name=index_name,
        embedding_function=embeddings.embed_query,
    )
    return vector_store


def add_website_to_vector_store(url):
    # Add a website to the vector store, and all of its subpages
    vector_store = init_vector_store(embeddings=AzureOpenAIEmbeddings(
        azure_deployment="AskSenacor-ada002-v1",
        openai_api_version="2023-05-15",
    ),
        index_name="langchain-vector-demo")
    # Load all subpages of the website
    grab = requests.get(url)
    soup = BeautifulSoup(grab.text, 'html.parser')
    urls = list({link.get('href') for link in soup.find_all("a")})
    # Load the data from the website and all subpages
    loader = WebBaseLoader(urls)
    data = loader.load()
    # Split the loaded data
    # TODO: Add a more sophisticated text splitter
    text_splitter = CharacterTextSplitter(separator='\n',
                                          chunk_size=500,
                                          chunk_overlap=40)

    docs = text_splitter.split_documents(data)
    for i, d in enumerate(docs):
        d.metadata["chunk_id"] = str(i)
    # Add the documents to the vector store
    vector_store.add_documents(documents=docs)


def add_confluence_to_vector_store(page_ids=["209421559", "209421568", "209421563"]):
    # Load data from the specified Confluence site and the specified pages
    embeddings = AzureOpenAIEmbeddings(
        azure_deployment="AskSenacor-ada002-v1",
        openai_api_version="2023-05-15",
    )
    vector_store = init_vector_store(embeddings, index_name="langchain-vector-demo")
    # Username and API Token
    if CONFLUENCE_API_KEY:
        loader = ConfluenceLoader(
            url=CONFLUENCE_URL, username=CONFLUENCE_USERNAME, api_key=CONFLUENCE_API_KEY
        )
        data = loader.load(space_key="SPACE", include_attachments=True, limit=50)
    # This is the preferred way to authenticate
    elif CONFLUENCE_TOKEN:
        loader = ConfluenceLoader(url=CONFLUENCE_URL, token=CONFLUENCE_TOKEN)
        data = loader.load(page_ids=page_ids, content_format=ContentFormat.VIEW)

    # Split the loaded data
    # TODO: Add a more sophisticated text splitter
    text_splitter = RecursiveCharacterTextSplitter(separators=['\n', '\n\n', ' '],
                                                   chunk_size=500,
                                                   chunk_overlap=40)

    docs = text_splitter.split_documents(data)
    for i, d in enumerate(docs):
        d.metadata["id"] = d.metadata["id"] + '_' + str(i)
    vector_store.add_documents(documents=docs)