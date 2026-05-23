# ==========================================================
# IMPORTAÇÃO DAS BIBLIOTECAS
# ==========================================================

# Flask:
# Framework web utilizado para criar aplicações web em Python.
# Ele permite criar rotas, páginas, APIs e controlar requisições HTTP.
from flask import Flask, request, redirect, session, render_template, jsonify, url_for

# Flask-CORS:
# Permite que o sistema aceite requisições de outros domínios.
# Muito usado quando frontend e backend estão separados.
from flask_cors import CORS

# Werkzeug Security:
# Biblioteca usada para criptografar senhas e verificar hashes.
# Isso aumenta a segurança do sistema.
from werkzeug.security import generate_password_hash, check_password_hash

# Importa a função responsável por conectar ao banco de dados.
from db import get_connection

# Importa o cliente de IA da Groq.
from ia import client_groq


# ==========================================================
# INICIALIZAÇÃO DA APLICAÇÃO
# ==========================================================

# Cria a aplicação Flask.
app = Flask(__name__)

# Habilita o CORS no sistema.
CORS(app)

# SECRET KEY:
# Chave usada pelo Flask para proteger sessões.
#
# Sessões armazenam informações do usuário logado.
#
# Exemplo:
# session["id"] = 1
#
# IMPORTANTE:
# Nunca deixar vazio em produção.
app.secret_key = ""


# ==========================================================
# ARQUITETURA GERAL DO SISTEMA
# ==========================================================

# Este sistema segue uma arquitetura parecida com MVC:
#
# MODEL:
# Banco de dados MySQL
#
# VIEW:
# Templates HTML
#
# CONTROLLER:
# Rotas Flask
#
#
# Estrutura provável:
#
# projeto/
# │
# ├── app.py
# ├── db.py
# ├── ia.py
# │
# ├── templates/
# │   ├── login.html
# │   ├── dashboard.html
# │   └── ...
# │
# ├── static/
# │   ├── css/
# │   ├── js/
# │   └── img/
# │
# └── banco.sql
#
#
# RESPONSABILIDADES:
#
# app.py
# -> controla rotas e regras do sistema
#
# db.py
# -> conecta no banco
#
# ia.py
# -> comunicação com inteligência artificial
#
# templates/
# -> interface do usuário
#


# ==========================================================
# FUNÇÕES UTILITÁRIAS
# ==========================================================

def formatar_data_br(data):

    # Verifica se a data existe.
    if not data:
        return None

    # Converte a data para padrão brasileiro.
    #
    # %d -> dia
    # %m -> mês
    # %Y -> ano
    return data.strftime("%d/%m/%Y")


def formatar_datahora_br(datahora):

    # Verifica se a data/hora existe.
    if not datahora:
        return None

    # Formata data e hora no padrão brasileiro.
    #
    # %H -> hora
    # %M -> minuto
    return datahora.strftime("%d/%m/%Y %H:%M")


# ==========================================================
# ROTA PRINCIPAL
# ==========================================================

# @app.route define uma rota.
#
# "/" significa página inicial.
#
# methods=["GET"]
# indica que essa rota aceita apenas requisições GET.
@app.route("/", methods=["GET"])
def home():

    # Verifica se o usuário está logado.
    #
    # session funciona como um armazenamento temporário
    # do usuário autenticado.
    if 'id' in session:

        # Redireciona para dashboard.
        return redirect(url_for('dashboard'))

    # Renderiza a página index.html
    return render_template('index.html')


# ==========================================================
# LOGIN
# ==========================================================

@app.route("/login", methods=["GET"])
def get_login():

    # Se já estiver logado, vai direto para dashboard.
    if 'id' in session:
        return redirect(url_for('dashboard'))

    # Exibe tela de login.
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():

    # request.form pega dados enviados pelo formulário HTML.
    email = request.form.get("email")
    senha = request.form.get("senha")

    # Validação básica.
    if not email or not senha:
        return render_template(
            "login.html",
            erro="Email e senha são obrigatórios."
        )

    # Abre conexão com banco.
    conn = get_connection()

    # dictionary=True:
    # Faz o resultado vir como dicionário.
    #
    # Exemplo:
    # usuario["email"]
    cursor = conn.cursor(dictionary=True)

    try:

        # SQL parametrizado:
        # Evita SQL Injection.
        cursor.execute(
            "SELECT * FROM usuarios WHERE email = %s",
            (email,)
        )

        # Pega apenas um usuário.
        usuario = cursor.fetchone()

        # Verifica se usuário existe.
        if not usuario:
            return render_template(
                "login.html",
                erro="Usuário não encontrado."
            )

        # Verifica senha criptografada.
        #
        # check_password_hash(hash_do_banco, senha_digitada)
        if not check_password_hash(usuario["senha"], senha):
            return render_template(
                "login.html",
                erro="Senha incorreta."
            )

        # Cria sessão do usuário.
        session["id"] = usuario["id"]
        session["nome"] = usuario["nome"]
        session["email"] = usuario["email"]
        session["perfil"] = usuario["perfil"]

        # Redireciona para dashboard.
        return redirect(url_for("dashboard"))

    except Exception as e:

        # Captura erros.
        return render_template(
            "login.html",
            erro=str(e)
        )

    finally:

        # Fecha conexão mesmo em caso de erro.
        cursor.close()
        conn.close()


# ==========================================================
# LOGOUT
# ==========================================================

@app.route('/logout')
def logout():

    # Remove informações da sessão.
    session.pop('id', None)
    session.pop('nome', None)
    session.pop('email', None)
    session.pop('perfil', None)

    # Volta para home.
    return redirect(url_for('home'))


# ==========================================================
# CADASTRO DE USUÁRIO
# ==========================================================

@app.route("/cadastro", methods=["GET"])
def get_cadastro():

    # Exibe formulário de cadastro.
    return render_template("cadastro.html")


@app.route("/cadastro", methods=["POST"])
def cadastrar_usuario():

    # Captura dados enviados pelo formulário.
    nome = request.form.get("nome")
    email = request.form.get("email")
    senha = request.form.get("senha")

    # Perfil padrão = aluno.
    perfil = request.form.get("perfil", "aluno")

    idade = request.form.get("idade")

    # Validação.
    if not nome or not email or not senha:
        return render_template(
            "cadastro.html",
            erro="Nome, email e senha são obrigatórios."
        )

    # Criptografa senha.
    senha_hash = generate_password_hash(senha)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        # INSERT INTO:
        # Insere dados no banco.
        sql = """
        INSERT INTO usuarios (nome, email, senha, perfil, idade)
        VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(sql, (
            nome,
            email,
            senha_hash,
            perfil,
            idade
        ))

        # Salva alterações no banco.
        conn.commit()

        return redirect(url_for("get_login"))

    except Exception as e:

        return render_template(
            "cadastro.html",
            erro=str(e)
        )

    finally:

        cursor.close()
        conn.close()


# ==========================================================
# DASHBOARD
# ==========================================================

@app.route("/dashboard", methods=["GET"])
def dashboard():

    # Proteção de rota.
    #
    # Apenas usuários logados podem acessar.
    if "id" not in session:
        return redirect(url_for("get_login"))

    # Renderiza painel principal.
    return render_template(
        "dashboard.html",

        # Dados enviados para HTML.
        usuario_id=session["id"],
        nome=session.get("nome")
    )


# ==========================================================
# API DO DASHBOARD
# ==========================================================

@app.route("/dashboard/dados", methods=["GET"])
def dashboard_dados():

    # Verifica autenticação.
    if "id" not in session:
        return jsonify({
            "erro": "Usuário não autenticado."
        }), 401

    usuario_id = session["id"]

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        # Soma todas receitas do usuário.
        cursor.execute("""
            SELECT COALESCE(SUM(valor), 0) AS total_receitas
            FROM receitas
            WHERE usuario_id = %s
        """, (usuario_id,))

        receitas = cursor.fetchone()

        # Soma todas despesas.
        cursor.execute("""
            SELECT COALESCE(SUM(valor), 0) AS total_despesas
            FROM despesas
            WHERE usuario_id = %s
        """, (usuario_id,))

        despesas = cursor.fetchone()

        # Converte Decimal para float.
        total_receitas = float(receitas["total_receitas"])
        total_despesas = float(despesas["total_despesas"])

        # Calcula saldo.
        saldo = total_receitas - total_despesas

        # Retorna JSON.
        return jsonify({
            "total_receitas": total_receitas,
            "total_despesas": total_despesas,
            "saldo": saldo
        })

    except Exception as e:

        return jsonify({
            "erro": str(e)
        }), 500

    finally:

        cursor.close()
        conn.close()



# ==========================================================
# EXECUÇÃO DA APLICAÇÃO
# ==========================================================

# __name__ == "__main__"
#
# Significa:
# "Execute apenas se este arquivo
# for o principal do projeto."
#
# debug=True:
# Reinicia automaticamente ao salvar.
if __name__ == "__main__":
    app.run(debug=True)