import tempfile

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


def load_and_index_pdfs(pdf_bytes_list):
    documentos = []

    for pdf_bytes in pdf_bytes_list:
        # Criar arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_bytes)
            tmp.flush()
            loader = PyPDFLoader(tmp.name)
            documentos.extend(loader.load())

    embeddings = HuggingFaceEmbeddings()

    vectorstore = FAISS.from_documents(documentos, embeddings)
    return vectorstore
