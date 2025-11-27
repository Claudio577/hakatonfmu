import re
from json_db import add_transaction

# ---------------------------------------------------------
# Categorização automática
# ---------------------------------------------------------
def categorizar_transacao(descricao):
    desc = descricao.lower()

    categorias = {
        "mercado": ["supermercado", "mercado", "carrefour", "extra", "assai"],
        "transporte": ["uber", "99", "ônibus", "metro", "combustível"],
        "restaurante": ["mc", "mcdonalds", "bk", "burguer", "restaurante", "lanche"],
        "lazer": ["cinema", "shopping", "netflix", "spotify"],
        "saúde": ["farmácia", "drogasil", "drogaria"],
        "salário": ["salário", "pagamento", "holerite"],
        "pix": ["pix"],
        "boleto": ["boleto", "pagamento"],
    }

    for categoria, termos in categorias.items():
        for termo in termos:
            if termo in desc:
                return categoria
    return "outros"


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

