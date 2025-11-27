from json_db import load_db
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# Inicializa o LLM da OpenAI
llm = ChatOpenAI(
    model="gpt-4o-mini",  # leve e rápido, ideal para Streamlit
    temperature=0.2
)

def process_query(pergunta, vectorstore):

    # Recuperação de contexto dos PDFs
    docs = vectorstore.similarity_search(pergunta, k=4)
    contexto_pdf = "\n\n".join([d.page_content for d in docs])

    # Carrega dados reais do usuário (JSON)
    db = load_db()
    saldo = db["saldo"]
    transacoes = db["transacoes"]

    # Prompt inteligente — consultor financeiro
    prompt = ChatPromptTemplate.from_template("""
    Você é um CONSULTOR FINANCEIRO inteligente.

    Use:
    - TRANSACOES reais do usuário (banco JSON)
    - SALDO real
    - CONTEXTO extraído dos PDFs (opcional)
    - Sua própria interpretação da pergunta

    Responda sempre de forma clara, direta e profissional.
    Se a pergunta for sobre saldo, diga o saldo.
    Se for sobre gastos, analise as transações.
    Se for sobre categorias, explique.
    Se não souber, use o contexto do PDF.

    --- DADOS DO USUÁRIO ---
    Saldo atual: R$ {saldo}
    Transações recentes: {transacoes}

    --- CONTEXTO DO PDF ---
    {contexto_pdf}

    Pergunta do usuário:
    "{pergunta}"

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
