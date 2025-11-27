from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
import tempfile
import os

def load_and_index_pdfs(pdf_bytes_list):
    texts = []

    # Salva PDFs temporariamente
    for pdf_bytes in pdf_bytes_list:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_bytes)
            tmp.flush()
            loader = PyPDFLoader(tmp.name)
            pages = loader.load()
            for p in pages:
                texts.append(p.page_content)

    # Embeddings da OpenAI (funciona no Streamlit Cloud)
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=os.getenv("OPENAI_API_KEY")
    )

    # Indexação no ChromaDB
    vectorstore = Chroma.from_texts(texts, embeddings)

    return vectorstore

