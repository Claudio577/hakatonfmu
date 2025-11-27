import re
from json_db import add_transaction

# ---------------------------------------------------------
# Categorização automática simples
# ---------------------------------------------------------

def categorizar_transacao(desc):
    desc = desc.lower()
    if "mercado" in desc or "super" in desc:
        return "supermercado"
    if "uber" in desc:
        return "transporte"
    if "ifood" in desc:
        return "alimentação"
    if "pix" in desc:
        return "pix"
    if "boleto" in desc or "pagamento" in desc:
        return "pagamentos"
    return "outros"


# ---------------------------------------------------------
# Extrator único (limpo e funcionando)
# ---------------------------------------------------------
def extrair_transacoes_do_texto(texto):
    """
    Extrai transações do PDF detectando:
    - 01/11 Mercadinho Central R 45,90
    - 02/10 Uber Viagem R$ 18,00
    - Mercadinho Central R$ 45,90
    """

    # limpa quebras estranhas
    texto = texto.replace("R$", "R$ ")

    padroes = [
        # data + descrição + valor
        r"(\d{1,2}/\d{1,2})\s+(.+?)\s+R\$\s*([\d.,]+)",

        # descrição + valor (sem data)
        r"(.+?)\s+R\$\s*([\d.,]+)"
    ]

    resultados = []

    for regex in padroes:
        matches = re.findall(regex, texto)

        for m in matches:
            if len(m) == 3:
                data, descricao, valor = m
            else:
                data = ""
                descricao, valor = m

            # trata valor
            valor = float(valor.replace(".", "").replace(",", "."))
            valor = -abs(valor)  # sempre despesa

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
            descricao=f"{t['data']} - {t['descricao']}".strip(" -"),
            valor=t["valor"],
            categoria=categoria
        )


