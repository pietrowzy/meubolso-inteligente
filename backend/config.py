# ==========================================================
# IMPORTAÇÕES
# ==========================================================

# Recursos usados para carregar variáveis de ambiente do arquivo .env.
import os
from dotenv import load_dotenv


# ==========================================================
# CARREGAMENTO DAS VARIÁVEIS DE AMBIENTE
# ==========================================================

# Carrega as configurações definidas no arquivo .env.
load_dotenv()


# ==========================================================
# CONFIGURAÇÃO DO BANCO DE DADOS
# ==========================================================

# Define os dados de conexão com o MySQL usando variáveis de ambiente.
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "meubolso_inteligente"),
    "port": int(os.getenv("DB_PORT", 3306))
}


# ==========================================================
# CHAVE DA API GROQ
# ==========================================================

# Recupera a chave usada para conectar o sistema à API da Groq.
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
