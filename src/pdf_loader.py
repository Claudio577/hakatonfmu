from langchain.document_loaders import PyPDFLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS

def load_and_index_pdfs(pdf_bytes_list):
    docs = []

    for pdf_bytes in pdf_bytes_list:
        loader = PyPDFLoader(pdf_bytes)
        docs.extend(loader.load())

    embeddings = HuggingFaceEmbeddings()
    vectorstore = FAISS.from_documents(docs, embeddings)

    return vectorstore
