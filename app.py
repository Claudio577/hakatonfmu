import streamlit as st
import tempfile

# Banco JSON
from json_db import init_db, load_db

# PDFs e RAG
from src.pdf_loader import load_and_index_pdfs
from src.rag import process_query
from financeiro import extrair_transacoes_do_texto, salvar_transacoes_extraidas
from langchain_community.document_loaders import PyPDFLoader

# Serviços financeiros
from services.pix import enviar_pix
from services.pagamentos import pagar_boleto
from services.recargas import fazer_recarga
from services.emprestimos import contratar_emprestimo


# -----------------------------------------------------
# Inicializar banco ao iniciar o app
# -----------------------------------------------------
init_db()

st.set_page_config(page_title="Hub Financeiro Inteligente", layout="wide")
st.title("💸 Hub Financeiro Inteligente — PDFs + RAG + Simulação")


# -----------------------------------------------------
# ESTADO GLOBAL
# -----------------------------------------------------
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

if "pdf_bytes" not in st.session_state:
    st.session_state.pdf_bytes = []


# -----------------------------------------------------
# MENU LATERAL
# -----------------------------------------------------
menu = st.sidebar.radio(
    "Menu",
    ["Dashboard", "Enviar PDF", "Fazer Pergunta (RAG)", "PIX", "Pagamentos", "Recargas", "Empréstimos"]
)
# -----------------------------------------------------
# BOTÃO DE RESET GERAL
# -----------------------------------------------------
if st.sidebar.button("🔄 Resetar Sistema (Limpar tudo)"):
    from json_db import save_db
    save_db({"saldo": 0.0, "transacoes": []})
    st.sidebar.success("Sistema resetado com sucesso!")
    st.rerun()


# -----------------------------------------------------
# DASHBOARD
# -----------------------------------------------------
if menu == "Dashboard":
    st.header("📊 Dashboard Financeiro Inteligente")

    data = load_db()

    st.metric("Saldo atual", f"R$ {data['saldo']:.2f}")

    transacoes = data["transacoes"]

    st.markdown("---")

    # --------------------------
    # Gráfico por categoria
    # --------------------------
    st.subheader("🏷 Gastos por categoria")
    categorias = {}

    for t in transacoes:
        if t["valor"] < 0:
            categoria = t.get("categoria", "outros")
            categorias[categoria] = categorias.get(categoria, 0) + abs(t["valor"])

    if categorias:
        st.bar_chart(categorias)
    else:
        st.info("Nenhuma despesa encontrada.")

    st.markdown("---")

    # --------------------------
    # Maiores gastos
    # --------------------------
    st.subheader("💸 Maiores gastos")
    despesas = [t for t in transacoes if t["valor"] < 0]

    if despesas:
        maiores = sorted(despesas, key=lambda x: x["valor"])[:5]
        for t in maiores:
            st.write(f"**{t['descricao']}** — R$ {abs(t['valor'])} — categoria: {t['categoria']}")
    else:
        st.info("Nenhuma despesa registrada.")

    st.markdown("---")

    # --------------------------
    # Últimas transações
    # --------------------------
    st.subheader("📜 Últimas transações")

    for t in reversed(transacoes[-10:]):
        st.write(f"- **{t['tipo']}** — {t['descricao']} — R$ {t['valor']} — categoria: {t['categoria']}")


# -----------------------------------------------------
# ENVIAR PDF
# -----------------------------------------------------
elif menu == "Enviar PDF":
    st.header("📁 Enviar PDFs de extratos, faturas ou comprovantes")

    uploaded = st.file_uploader("Envie PDFs", type=["pdf"], accept_multiple_files=True)

    if uploaded:
        import tempfile
        from langchain_community.document_loaders import PyPDFLoader

        # Armazena PDFs (usado no RAG)
        st.session_state.pdf_bytes = [u.getvalue() for u in uploaded]

        # Indexar PDFs para RAG
        with st.spinner("Lendo e indexando PDFs..."):
            st.session_state.vectorstore = load_and_index_pdfs(st.session_state.pdf_bytes)

        st.success("PDFs carregados com sucesso!")
        st.subheader("🔍 Extraindo transações dos PDFs...")

        # Extração REAL das transações
        for u in uploaded:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(u.getvalue())
                tmp.flush()

                loader = PyPDFLoader(tmp.name)
                paginas = loader.load()

                # juntar texto
                texto = "\n".join([p.page_content for p in paginas])

                # DEBUG: Mostra o texto extraído
                st.write("📄 Texto extraído:", texto[:1000])

                # extrair transações
                trans = extrair_transacoes_do_texto(texto)

                # DEBUG: Mostra as transações detectadas
                st.write("🔍 Transações encontradas:", trans)

                # salvar no banco JSON
                salvar_transacoes_extraidas(trans)

        st.success("Transações adicionadas ao banco!")


# -----------------------------------------------------
# PERGUNTA (RAG)
# -----------------------------------------------------
elif menu == "Fazer Pergunta (RAG)":
    st.header("🧠 Pergunte algo sobre os PDFs")

    pergunta = st.text_input("Digite sua pergunta:")

    if st.button("Enviar"):
        if not st.session_state.vectorstore:
            st.error("Nenhum PDF carregado ainda.")
        else:
            resposta, fontes = process_query(pergunta, st.session_state.vectorstore)
            st.markdown("### Resposta")
            st.write(resposta)

            st.markdown("### Fontes utilizadas")
            for f in fontes:
                st.write(f["texto"])


# -----------------------------------------------------
# PIX
# -----------------------------------------------------
elif menu == "PIX":
    st.header("⚡ Fazer PIX")

    chave = st.text_input("Chave PIX")
    valor = st.number_input("Valor", min_value=1.0)

    if st.button("Enviar PIX"):
        ok, msg = enviar_pix(chave, valor)
        st.success(msg) if ok else st.error(msg)


# -----------------------------------------------------
# PAGAMENTOS
# -----------------------------------------------------
elif menu == "Pagamentos":
    st.header("💳 Pagamento de Boleto")

    codigo = st.text_input("Código do boleto")
    valor = st.number_input("Valor", min_value=1.0)

    if st.button("Pagar"):
        ok, msg = pagar_boleto(codigo, valor)
        st.success(msg) if ok else st.error(msg)


# -----------------------------------------------------
# RECARGAS
# -----------------------------------------------------
elif menu == "Recargas":
    st.header("📱 Recarga de celular")

    numero = st.text_input("Número")
    operadora = st.selectbox("Operadora", ["Vivo", "Claro", "TIM", "Oi"])
    valor = st.number_input("Valor", min_value=1.0)

    if st.button("Recarregar"):
        ok, msg = fazer_recarga(numero, operadora, valor)
        st.success(msg) if ok else st.error(msg)


# -----------------------------------------------------
# EMPRÉSTIMOS
# -----------------------------------------------------
elif menu == "Empréstimos":
    st.header("🏦 Simulação de Empréstimo")

    valor = st.number_input("Valor desejado", min_value=100.0)

    if st.button("Contratar"):
        ok, total = contratar_emprestimo(valor)
        if ok:
            st.success(f"Empréstimo aprovado! Total final: R$ {total}")
        else:
            st.error(total)
