from flask import Flask, request, redirect, session, render_template, jsonify, url_for
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_connection
from ia import client_groq

app = Flask(__name__)
CORS(app)

app.secret_key = ""

####

# =========================
# ROTA PRINCIPAL
# =========================
@app.route("/", methods=["GET"])
def home():
    if 'id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

# =========================
# ROTAS DE LOGIN E LOGOUT
# =========================
@app.route("/login", methods=["GET"])
def get_login():
    if 'id' in session:
        return redirect(url_for('dashboard'))
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    senha = request.form.get("senha")

    if not email or not senha:
        return render_template("login.html", erro="Email e senha são obrigatórios.")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        usuario = cursor.fetchone()

        if not usuario:
            return render_template("login.html", erro="Usuário não encontrado.")

        if not check_password_hash(usuario["senha"], senha):
            return render_template("login.html", erro="Senha incorreta.")

        session["id"] = usuario["id"]
        session["nome"] = usuario["nome"]
        session["email"] = usuario["email"]
        session["perfil"] = usuario["perfil"]

        return redirect(url_for("dashboard"))

    except Exception as e:
        return render_template("login.html", erro=str(e))

    finally:
        cursor.close()
        conn.close()

@app.route('/logout')
def logout():
    session.pop('id', None)
    session.pop('nome', None)
    session.pop('email', None)
    session.pop('perfil', None)
    return redirect(url_for('home'))

# =============================
# ROTAS DE CADASTRO DE USUÁRIO
# =============================
@app.route("/cadastro", methods=["GET"])
def get_cadastro():
    return render_template("cadastro.html")

@app.route("/cadastro", methods=["POST"])
def cadastrar_usuario():
    nome = request.form.get("nome")
    email = request.form.get("email")
    senha = request.form.get("senha")
    perfil = request.form.get("perfil", "aluno")
    idade = request.form.get("idade")

    if not nome or not email or not senha:
        return render_template(
            "cadastro.html",
            erro="Nome, email e senha são obrigatórios."
        )

    senha_hash = generate_password_hash(senha)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        sql = """
        INSERT INTO usuarios (nome, email, senha, perfil, idade)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (nome, email, senha_hash, perfil, idade))
        conn.commit()

        return redirect(url_for("get_login"))

    except Exception as e:
        return render_template("cadastro.html", erro=str(e))

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    app.run(debug=True)
