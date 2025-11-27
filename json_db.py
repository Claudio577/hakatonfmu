
import json
import os

DB_FILE = "financeiro.json"

# ---------------------------------------------------------
# INICIALIZAÇÃO DO BANCO
# ---------------------------------------------------------
def init_db():
    """Cria arquivo financeiro.json se não existir."""
    if not os.path.exists(DB_FILE):
        data = {
            "saldo": 1000.00,
            "transacoes": [],
            "emprestimos": [],
            "pagamentos": [],
            "recargas": []
        }
        save_db(data)

# ---------------------------------------------------------
# Funções básicas
# ---------------------------------------------------------
def load_db():
    """Carrega os dados do banco JSON."""
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    """Salva os dados no arquivo JSON."""
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ---------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------
from financeiro import categorizar_transacao

def add_transaction(tipo, descricao, valor):
    """Adiciona transação ao banco e atualiza saldo."""

    categoria = categorizar_transacao(descricao)

    data = load_db()

    nova_transacao = {
        "tipo": tipo,
        "descricao": descricao,
        "valor": valor,
        "categoria": categoria
    }

    data["transacoes"].append(nova_transacao)
    data["saldo"] += valor  # valor positivo = entrada, negativo = saída

    save_db(data)
    return nova_transacao
