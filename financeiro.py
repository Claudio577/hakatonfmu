import re
from json_db import add_transaction

# ---------------------------------------------------------
# Categorização automática
# ---------------------------------------------------------

def extrair_transacoes_do_texto(texto):
    """
    Extrai transações mesmo quando o PDF vem sem espaços.
    Detecta padrões como:
    01/11MercadinhoCentralR45,90
    11/11UberViagemR16,90
    """

    # 1️⃣ Garante que exista separação entre palavras e números grudados
    texto = re.sub(r"([a-zA-Z])(\d{1,2}/\d{1,2})", r"\1 \2", texto)
    texto = re.sub(r"(\d{1,2}/\d{1,2})([A-Z])", r"\1 \2", texto)
    texto = re.sub(r"([A-Za-z])(\d)", r"\1 \2", texto)

    # 2️⃣ Regex robusta: detecta linhas com DATA + DESCRIÇÃO + VALOR
    padrao = r"(\d{1,2}/\d{1,2})\s+([A-Za-zÀ-ÿ ]+?)\s*R?\s?([\d,.]+)"

    matches = re.findall(padrao, texto)

    resultado = []

    for data, descricao, valor in matches:
        valor = float(valor.replace(",", "."))
        valor = -valor  # é despesa
        resultado.append({
            "data": data,
            "descricao": descricao.strip(),
            "valor": valor
        })

    return resultado


    # ---------------  
    # CAPTURA PADRÃO 2  
    # (somente se não tiver capturado no padrão 1)  
    # ---------------
    for descricao, valor in re.findall(padrao2, texto):
        if "TOTAL" in descricao.upper():
            continue
        if not any(descricao in r["descricao"] for r in resultados):
            valor = float(valor.replace(".", "").replace(",", "."))
            resultados.append({
                "data": "",
                "descricao": descricao.strip(),
                "valor": -valor
            })

    return resultados

# ---------------------------------------------------------
# Extrair transações do PDF
# ---------------------------------------------------------
def extrair_transacoes_do_texto(texto):

    padroes = [
        r"(\d{1,2}/\d{1,2})\s+(.+?)\s+[-]?\s*R\$\s?([\d.,]+)",
        r"(.+?)\s+[-]?\s*R\$\s?([\d.,]+)"
    ]

    resultados = []

    for regex in padroes:
        matches = re.findall(regex, texto)
        for match in matches:
            if len(match) == 3:  
                data, descricao, valor = match
            else:
                data = ""
                descricao, valor = match

            valor = float(valor.replace(".", "").replace(",", "."))
            valor = -abs(valor)

            resultados.append({
                "data": data,
                "descricao": descricao.strip(),
                "valor": valor
            })

    return resultados


# ---------------------------------------------------------
# Salvar transações extraídas no banco
# ---------------------------------------------------------
def salvar_transacoes_extraidas(lista_transacoes):
    for t in lista_transacoes:
        categoria = categorizar_transacao(t["descricao"])
        add_transaction(
            tipo="PDF",
            descricao=f"{t['data']} - {t['descricao']}",
            valor=t["valor"],
            categoria=categoria
        )

