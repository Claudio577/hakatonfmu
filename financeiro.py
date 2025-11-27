import re
from json_db import add_transaction

# ---------------------------------------------------------
# Categorização automática
# ---------------------------------------------------------


def extrair_transacoes_do_texto(texto):
    """
    Extrai transações reais dos PDFs (Pix, compras, serviços etc.)
    Ignora totais e textos quebrados.
    Compatível com o formato colado dos seus PDFs.
    """

    # Remove múltiplos espaços e deixa tudo mais limpo
    texto = texto.replace("\n", " ")
    texto = re.sub(r"\s{2,}", " ", texto)

    # PADRÃO PRINCIPAL (data + descrição + valor colado sem espaço)
    padrao1 = r"(\d{1,2}/\d{1,2})([A-Za-zÀ-ÿ0-9 ]+?)R\s?([\d.,]+)"

    # PADRÃO SECUNDÁRIO (valor sem data, tipo "SupermercadoExtraR220,50")
    padrao2 = r"([A-Za-zÀ-ÿ ]+?)R\s?([\d.,]+)"

    resultados = []

    # ---------------  
    # CAPTURA PADRÃO 1  
    # ---------------
    for data, descricao, valor in re.findall(padrao1, texto):
        valor = float(valor.replace(".", "").replace(",", "."))
        if "TOTAL" in descricao.upper():  
            continue  # ignora totais
        resultados.append({
            "data": data,
            "descricao": descricao.strip(),
            "valor": -valor  # despesa padrão
        })

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

