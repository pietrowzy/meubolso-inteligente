# ==========================================================
# IMPORTAÇÕES
# ==========================================================

# Recursos usados para acessar variáveis de ambiente e conectar à API da Groq.
import os
from groq import Groq


# ==========================================================
# CONFIGURAÇÃO DA CHAVE DA API
# ==========================================================

# Recupera a chave da API da Groq definida nas variáveis de ambiente.
# evita deixar chaves sensíveis escritas diretamente no código-fonte.
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# ==========================================================
# VALIDAÇÃO
# ==========================================================

# Informa no terminal caso a chave da API não esteja configurada.
# o sistema exibe uma mensagem de erro no terminal para ajudar o 
# desenvolvedor a identificar o problema durante a execução.
if not GROQ_API_KEY:
    print("ERRO: GROQ_API_KEY não encontrada.")


# ==========================================================
# CLIENTE GROQ
# ==========================================================

# Cria o cliente usado para enviar requisições à API da Groq.
# Esse objeto será utilizado em outras partes do sistema para enviar
# prompts, solicitar análises e receber respostas geradas por 
# inteligência artificial.
client_groq = Groq(api_key=GROQ_API_KEY)