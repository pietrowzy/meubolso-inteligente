# Importa o módulo "os" da biblioteca padrão do Python.
# Esse módulo permite interagir com o sistema operacional,
# como acessar arquivos, pastas e variáveis de ambiente.
import os

# Importa a classe "Groq" da biblioteca "groq".
# Essa biblioteca é usada para se comunicar com a API da Groq,
# permitindo enviar requisições para modelos de inteligência artificial.
from groq import Groq


# Cria uma variável chamada GROQ_API_KEY.
# Ela recebe o valor da variável de ambiente chamada "GROQ_API_KEY".
#
# Variáveis de ambiente são usadas para armazenar informações sensíveis,
# como senhas e chaves de API, sem precisar escrever diretamente no código.
#
# O método os.getenv("NOME") busca o valor da variável de ambiente.
# Se ela não existir, retorna None.
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# Verifica se a variável GROQ_API_KEY está vazia ou não existe.
#
# O operador "not" verifica se o valor é falso.
# Em Python, None, vazio ("") e False são considerados falsos.
if not GROQ_API_KEY:

    # Exibe uma mensagem de erro no terminal caso a chave da API
    # não tenha sido encontrada.
    #
    # Isso ajuda o programador a identificar o problema rapidamente.
    print("ERRO: GROQ_API_KEY não encontrada.")


# Cria um objeto da classe Groq.
#
# Esse objeto será responsável por fazer a conexão com a API da Groq.
#
# O parâmetro api_key=GROQ_API_KEY envia a chave da API para autenticação.
#
# Sem essa chave, normalmente a API recusará as requisições.
client_groq = Groq(api_key=GROQ_API_KEY)