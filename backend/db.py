# ==========================================================
# IMPORTAÇÕES
# ==========================================================

# Recursos usados para conectar o sistema ao banco de dados MySQL.
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

# ==========================================================
# CONEXÃO COM O BANCO DE DADOS
# ==========================================================

def get_connection():

    # Cria e retorna uma conexão com o MySQL usando as configurações do projeto.
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection

    except Error as e:
        print("Erro ao conectar ao MySQL:", e)
        return None