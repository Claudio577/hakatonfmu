from json_db import load_db
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import os

# pega API Key do Secrets
openai_api_key = os.getenv("OPENAI_API_KEY")

# inicializa LLM
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.2,
    api_key=openai_api_key
)

def process_query(pergunta, vectorstore):

    docs = vectorstore.similarity_search(pergunta, k=4)
    contexto_pdf = "\n\n".join([d.page_content for d in docs])

    db = load_db()
    saldo = db["saldo"]
    transacoes = db["transacoes"]

    prompt = ChatPromptTemplate.from_template("""
    Você é um consultor financeiro inteligente...

    --- DADOS DO USUÁRIO ---
    Saldo: R$ {saldo}
    Transações: {transacoes}

    --- CONTEXTO DO PDF ---
    {contexto_pdf}

    Pergunta:
    {pergunta}

    Resposta:
    """)

    chain = prompt | llm
    resposta = chain.invoke({
        "pergunta": pergunta,
        "saldo": saldo,
        "transacoes": transacoes,
        "contexto_pdf": contexto_pdf
    })

    return resposta, docs
