import tempfile

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings


def load_and_index_pdfs(pdf_bytes_list):
    documentos = []

    for pdf_bytes in pdf_bytes_list:
        # Criar arquivo temporário a partir dos bytes
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_bytes)
            tmp.flush()
            loader = PyPDFLoader(tmp.name)
            documentos.extend(loader.load())

    # Criar embeddings
    embeddings = HuggingFaceEmbeddings()

    # Criar base vetorial
    vectorstore = FAISS.from_documents(documentos, embeddings)

    return vectorstore
