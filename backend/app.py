# ==========================================================
# IMPORTAÇÃO DAS BIBLIOTECAS
# ==========================================================

# Este bloco reúne todas as bibliotecas e recursos externos usados no sistema.
#
# Aqui são importados o Flask, recursos de requisição, sessão, templates,
# respostas em JSON, segurança de senhas, conexão com o banco de dados
# e o cliente de inteligência artificial usado no projeto.
import os
from flask import Flask, request, redirect, session, render_template, jsonify, url_for
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_connection
from ia import client_groq


# ==========================================================
# INICIALIZAÇÃO DA APLICAÇÃO
# ==========================================================

# Este bloco cria e configura a aplicação Flask.
#
# A aplicação é inicializada, o CORS é habilitado e a chave secreta
# é definida para proteger as sessões dos usuários logados.

app = Flask(__name__)
CORS(app)

app.secret_key = os.getenv("SECRET_KEY", "")


# ==========================================================
# FUNÇÕES UTILITÁRIAS
# ==========================================================

def formatar_data_br(data):

    # Esta função recebe uma data do banco de dados e converte para
    # o padrão brasileiro, facilitando a leitura pelo usuário.
 
    if not data:
        return None

    return data.strftime("%d/%m/%Y")


def formatar_datahora_br(datahora):

    # Esta função recebe uma data com horário e converte para o padrão
    # brasileiro, exibindo dia, mês, ano, hora e minuto.
    #
    
    if not datahora:
        return None

    return datahora.strftime("%d/%m/%Y %H:%M")


# ==========================================================
# ROTA PRINCIPAL
# ==========================================================

@app.route("/", methods=["GET"])
def home():

    # Esta rota representa a página inicial do sistema.
    #
    # Se o usuário já estiver logado, ele será redirecionado diretamente
    # para o dashboard. Caso contrário, será exibida a página inicial.
    if 'id' in session:
        return redirect(url_for('dashboard'))

    return render_template('index.html')


# ==========================================================
# LOGIN
# ==========================================================

@app.route("/login", methods=["GET"])
def get_login():

    # Esta rota exibe a tela de login.
    #
    # Caso o usuário já esteja autenticado, não há necessidade de fazer
    # login novamente, então ele é redirecionado para o dashboard.
    if 'id' in session:
        return redirect(url_for('dashboard'))

    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():

    # Esta rota processa o formulário de login.
    #
    # Ela recebe email e senha, consulta o usuário no banco de dados,
    # verifica se a senha está correta e, em caso positivo, cria a sessão
    # do usuário autenticado no sistema.
    email = request.form.get("email")
    senha = request.form.get("senha")

    if not email or not senha:
        return render_template(
            "login.html",
            erro="Email e senha são obrigatórios."
        )

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM usuarios WHERE email = %s",
            (email,)
        )

        usuario = cursor.fetchone()

        if not usuario:
            return render_template(
                "login.html",
                erro="Usuário não encontrado."
            )

        if not check_password_hash(usuario["senha"], senha):
            return render_template(
                "login.html",
                erro="Senha incorreta."
            )

        session["id"] = usuario["id"]
        session["nome"] = usuario["nome"]
        session["email"] = usuario["email"]
        session["perfil"] = usuario["perfil"]

        return redirect(url_for("dashboard"))

    except Exception as e:
        return render_template(
            "login.html",
            erro=str(e)
        )

    finally:
        cursor.close()
        conn.close()


# ==========================================================
# LOGOUT
# ==========================================================

@app.route('/logout')
def logout():

    # Esta rota realiza a saída do usuário do sistema.
    #
    # Para isso, remove da sessão os dados usados para identificar
    # o usuário logado e depois redireciona para a página inicial.
    session.pop('id', None)
    session.pop('nome', None)
    session.pop('email', None)
    session.pop('perfil', None)

    return redirect(url_for('home'))


# ==========================================================
# CADASTRO DE USUÁRIO
# ==========================================================

@app.route("/cadastro", methods=["GET"])
def get_cadastro():

    # Esta rota exibe o formulário de cadastro de novos usuários.
    #
    # Ela apenas carrega a página HTML onde o usuário poderá informar
    # nome, email, senha, perfil e idade.
    return render_template("cadastro.html")


@app.route("/cadastro", methods=["POST"])
def cadastrar_usuario():

    # Esta rota processa o cadastro de um novo usuário.
    #
    # Ela recebe os dados enviados pelo formulário, valida os campos
    # obrigatórios, criptografa a senha e salva o novo usuário no banco.
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

        cursor.execute(sql, (
            nome,
            email,
            senha_hash,
            perfil,
            idade
        ))

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

    # Esta rota exibe o painel principal do sistema.
    #
    # O dashboard só pode ser acessado por usuários logados. Ele envia
    # para o HTML informações básicas do usuário, como ID e nome.
    if "id" not in session:
        return redirect(url_for("get_login"))

    return render_template(
        "dashboard.html",
        usuario_id=session["id"],
        nome=session.get("nome")
    )


# ==========================================================
# API DO DASHBOARD
# ==========================================================

@app.route("/dashboard/dados", methods=["GET"])
def dashboard_dados():

    # Esta rota funciona como uma API do dashboard.
    #
    # Ela calcula o total de receitas, o total de despesas e o saldo
    # do usuário logado, retornando essas informações em formato JSON
    # para serem usadas pelo frontend.
    if "id" not in session:
        return jsonify({
            "erro": "Usuário não autenticado."
        }), 401

    usuario_id = session["id"]

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT COALESCE(SUM(valor), 0) AS total_receitas
            FROM receitas
            WHERE usuario_id = %s
        """, (usuario_id,))

        receitas = cursor.fetchone()

        cursor.execute("""
            SELECT COALESCE(SUM(valor), 0) AS total_despesas
            FROM despesas
            WHERE usuario_id = %s
        """, (usuario_id,))

        despesas = cursor.fetchone()

        total_receitas = float(receitas["total_receitas"])
        total_despesas = float(despesas["total_despesas"])

        saldo = total_receitas - total_despesas

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
# API DO DASHBOARD - DESPESAS POR CATEGORIA
# ==========================================================

@app.route("/dashboard/despesas-categorias/", methods=["GET"])
def dashboard_despesas_categoria():

    # Esta rota retorna os totais de despesas agrupados por categoria.
    #
    # Ela funciona como uma API do dashboard, pois entrega os dados em JSON
    # para que o frontend possa montar gráficos ou cards informativos.
    # Apenas usuários autenticados podem acessar essas informações.
    if "id" not in session:
        return jsonify({"erro": "Usuário não autenticado."}), 401

    usuario_id = session["id"]

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT 
                c.nome AS categoria,
                SUM(d.valor) AS total
            FROM despesas d
            LEFT JOIN categorias c ON c.id = d.categoria_id
            WHERE d.usuario_id = %s
            GROUP BY c.nome
            ORDER BY total DESC
        """, (usuario_id,))

        dados = cursor.fetchall()

        for item in dados:
            item["total"] = float(item["total"])

        return jsonify(dados)

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# ==========================================================
# RECEITAS
# ==========================================================

@app.route("/receitas", methods=["GET"])
def get_receitas():

    # Esta rota exibe a página de cadastro/listagem de receitas.
    #
    # Antes de carregar a tela, o sistema verifica se o usuário está logado.
    # Também busca no banco as categorias do tipo receita para preencher
    # o formulário da página.
    if "id" not in session:
        return redirect(url_for("get_login"))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT id, nome 
            FROM categorias 
            WHERE tipo = 'receita'
            ORDER BY nome
        """)
        categorias = cursor.fetchall()

        return render_template(
            "receitas.html",
            categorias=categorias
        )

    except Exception as e:
        return render_template(
            "receitas.html",
            categorias=[],
            erro=str(e)
        )

    finally:
        cursor.close()
        conn.close()


@app.route("/receitas", methods=["POST"])
def cadastrar_receita():

    # Esta rota recebe os dados do formulário de receitas e grava no banco.
    #
    # Ela captura descrição, valor, data e categoria da receita informada
    # pelo usuário. Após o cadastro ser concluído, o usuário é redirecionado
    # para o dashboard.
    if "id" not in session:
        return redirect(url_for("get_login"))

    usuario_id = session["id"]
    descricao = request.form.get("descricao")
    valor = request.form.get("valor")
    data_receita = request.form.get("data_receita")
    categoria_id = request.form.get("categoria_id")

    if not descricao or not valor or not data_receita:
        return redirect(url_for("get_receitas"))

    if categoria_id == "":
        categoria_id = None

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        sql = """
        INSERT INTO receitas 
        (usuario_id, categoria_id, descricao, valor, data_receita)
        VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(sql, (
            usuario_id,
            categoria_id,
            descricao,
            valor,
            data_receita
        ))

        conn.commit()

        return redirect(url_for("dashboard"))

    except Exception as e:
        return render_template(
            "receitas.html",
            categorias=[],
            erro=str(e)
        )

    finally:
        cursor.close()
        conn.close()


# ==========================================================
# DESPESAS
# ==========================================================

@app.route("/despesas", methods=["GET"])
def get_despesas():

    # Esta rota exibe a página de cadastro/listagem de despesas.
    #
    # O sistema verifica se o usuário está autenticado e busca as categorias
    # do tipo despesa para serem usadas no formulário da página.
    if "id" not in session:
        return redirect(url_for("get_login"))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT id, nome
            FROM categorias
            WHERE tipo = 'despesa'
            ORDER BY nome
        """)
        categorias = cursor.fetchall()

        return render_template(
            "despesas.html",
            categorias=categorias
        )

    except Exception as e:
        return render_template(
            "despesas.html",
            categorias=[],
            erro=str(e)
        )

    finally:
        cursor.close()
        conn.close()


@app.route("/despesas", methods=["POST"])
def cadastrar_despesa():

    # Esta rota recebe os dados do formulário de despesas e grava no banco.
    #
    # Ela registra a despesa vinculada ao usuário logado, permitindo informar
    # descrição, valor, data e categoria. Após salvar, o usuário retorna
    # para o dashboard.
    if "id" not in session:
        return redirect(url_for("get_login"))

    usuario_id = session["id"]
    descricao = request.form.get("descricao")
    valor = request.form.get("valor")
    data_despesa = request.form.get("data_despesa")
    categoria_id = request.form.get("categoria_id")

    if not descricao or not valor or not data_despesa:
        return redirect(url_for("get_despesas"))

    if categoria_id == "":
        categoria_id = None

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        sql = """
        INSERT INTO despesas 
        (usuario_id, categoria_id, descricao, valor, data_despesa)
        VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(sql, (
            usuario_id,
            categoria_id,
            descricao,
            valor,
            data_despesa
        ))

        conn.commit()

        return redirect(url_for("dashboard"))

    except Exception as e:
        return render_template(
            "despesas.html",
            categorias=[],
            erro=str(e)
        )

    finally:
        cursor.close()
        conn.close()


# ==========================================================
# RELATÓRIOS
# ==========================================================

@app.route("/relatorios", methods=["GET"])
def get_relatorios():

    # Esta rota exibe a página principal de relatórios.
    #
    # Ela apenas renderiza o HTML dos relatórios, enviando o ID do usuário
    # para que o frontend possa carregar informações específicas desse usuário.
    if "id" not in session:
        return redirect(url_for("get_login"))

    return render_template(
        "relatorios.html",
        usuario_id=session["id"]
    )


@app.route("/relatorios/despesas-categorias", methods=["GET"])
def relatorio_despesas_categoria():

    # Esta rota retorna um relatório de despesas agrupadas por categoria.
    #
    # Diferente da rota principal de relatórios, esta rota funciona como API,
    # entregando os dados em JSON para tabelas, gráficos ou outros componentes
    # da tela de relatórios.
    if "id" not in session:
        return jsonify({"erro": "Usuário não autenticado."}), 401

    usuario_id = session["id"]

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT 
                c.nome AS categoria,
                SUM(d.valor) AS total
            FROM despesas d
            LEFT JOIN categorias c ON c.id = d.categoria_id
            WHERE d.usuario_id = %s
            GROUP BY c.nome
            ORDER BY total DESC
        """, (usuario_id,))

        dados = cursor.fetchall()

        for item in dados:
            item["total"] = float(item["total"])

        return jsonify(dados)

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


@app.route("/receitas/listar", methods=["GET"])
def listar_receitas():

    # Esta rota lista todas as receitas cadastradas pelo usuário logado.
    #
    # Ela retorna os dados em formato JSON, incluindo descrição, valor,
    # data da receita e nome da categoria. Esses dados podem ser usados
    # em tabelas ou relatórios no frontend.
    if "id" not in session:
        return jsonify({"erro": "Usuário não autenticado."}), 401

    usuario_id = session["id"]

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT 
                r.id,
                r.descricao,
                r.valor,
                r.data_receita,
                c.nome AS categoria
            FROM receitas r
            LEFT JOIN categorias c ON c.id = r.categoria_id
            WHERE r.usuario_id = %s
            ORDER BY r.data_receita DESC
        """, (usuario_id,))

        receitas = cursor.fetchall()

        for item in receitas:
            item["valor"] = float(item["valor"])
            item["data_receita"] = formatar_data_br(item["data_receita"])

        return jsonify(receitas)

    finally:
        cursor.close()
        conn.close()


@app.route("/despesas/listar", methods=["GET"])
def listar_despesas():

    # Esta rota lista todas as despesas cadastradas pelo usuário logado.
    #
    # Ela retorna os dados em formato JSON, incluindo descrição, valor,
    # data da despesa e nome da categoria. As despesas são ordenadas
    # das mais recentes para as mais antigas.
    if "id" not in session:
        return jsonify({"erro": "Usuário não autenticado."}), 401

    usuario_id = session["id"]

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT 
                d.id,
                d.descricao,
                d.valor,
                d.data_despesa,
                c.nome AS categoria
            FROM despesas d
            LEFT JOIN categorias c ON c.id = d.categoria_id
            WHERE d.usuario_id = %s
            ORDER BY d.data_despesa DESC
        """, (usuario_id,))

        despesas = cursor.fetchall()

        for item in despesas:
            item["valor"] = float(item["valor"])
            item["data_despesa"] = formatar_data_br(item["data_despesa"])

        return jsonify(despesas)

    finally:
        cursor.close()
        conn.close()


# ==========================================================
# FEEDBACK
# ==========================================================

@app.route("/feedback", methods=["GET"])
def get_feedback():

    # Esta rota exibe a página de feedback do sistema.
    #
    # O usuário precisa estar logado para acessar a tela e registrar
    # sua avaliação sobre a plataforma.
    if "id" not in session:
        return redirect(url_for("get_login"))

    return render_template("feedback.html")


@app.route("/feedback", methods=["POST"])
def cadastrar_feedback():

    # Esta rota recebe e salva o feedback enviado pelo usuário.
    #
    # A nota é obrigatória, enquanto o comentário serve como complemento.
    # O feedback é vinculado ao usuário logado para manter o histórico
    # individual de avaliações.
    if "id" not in session:
        return redirect(url_for("get_login"))

    nota = request.form.get("nota")
    comentario = request.form.get("comentario")
    usuario_id = session["id"]

    if not nota:
        return render_template(
            "feedback.html",
            erro="A nota é obrigatória."
        )

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            INSERT INTO feedbacks (usuario_id, nota, comentario)
            VALUES (%s, %s, %s)
        """, (usuario_id, nota, comentario))

        conn.commit()

        return redirect(url_for("get_feedback"))

    except Exception as e:
        return render_template("feedback.html", erro=str(e))

    finally:
        cursor.close()
        conn.close()


@app.route("/feedbacks", methods=["GET"])
def listar_feedbacks():

    # Esta rota lista os feedbacks enviados pelo usuário logado.
    #
    # O retorno é feito em JSON e pode ser usado para exibir um histórico
    # de avaliações dentro do sistema.
    if "id" not in session:
        return jsonify({"erro": "Usuário não autenticado."}), 401

    usuario_id = session["id"]

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT nota, comentario, criado_em
            FROM feedbacks
            WHERE usuario_id = %s
            ORDER BY criado_em DESC
        """, (usuario_id,))

        feedbacks = cursor.fetchall()

        for item in feedbacks:
            item["criado_em"] = formatar_data_br(item["criado_em"])

        return jsonify(feedbacks)

    finally:
        cursor.close()
        conn.close()


# ==========================================================
# ROTAS IA
# ==========================================================

@app.route("/ia", methods=["GET"])
def pagina_ia():

    # Esta rota exibe a página da inteligência artificial financeira.
    #
    # Ela renderiza a tela onde o usuário poderá solicitar análises,
    # sugestões e orientações automáticas com base nos dados financeiros
    # cadastrados no sistema.
    if "id" not in session:
        return redirect(url_for("home"))

    return render_template("ia.html")


@app.route("/ia/analise-financeira", methods=["GET"])
def analise_financeira():

    # Esta rota gera uma análise financeira automática usando IA.
    #
    # O sistema calcula receitas, despesas e saldo do usuário logado.
    # Em seguida, envia essas informações para o modelo de IA, recebe
    # uma análise textual e salva essa resposta no banco de dados.
    if "id" not in session:
        return jsonify({"erro": "Usuário não autenticado."}), 401

    usuario_id = session["id"]

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT COALESCE(SUM(valor), 0) AS total_receitas
            FROM receitas
            WHERE usuario_id = %s
        """, (usuario_id,))
        receitas = cursor.fetchone()

        cursor.execute("""
            SELECT COALESCE(SUM(valor), 0) AS total_despesas
            FROM despesas
            WHERE usuario_id = %s
        """, (usuario_id,))
        despesas = cursor.fetchone()

        total_receitas = float(receitas["total_receitas"])
        total_despesas = float(despesas["total_despesas"])
        saldo = total_receitas - total_despesas

        prompt = f"""
        Analise a situação financeira abaixo de forma simples e didática.

        Receitas: R$ {total_receitas:.2f}
        Despesas: R$ {total_despesas:.2f}
        Saldo: R$ {saldo:.2f}

        Gere:
        1. Um resumo da situação.
        2. Um alerta, se necessário. Especifique em que categorias poderia reduzir os custos para obter os objetivos propostas.
        3. Três sugestões práticas para melhorar a vida financeira.
        """

        resposta = client_groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um assistente financeiro simples, claro e educativo."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4
        )

        analise_gerada = resposta.choices[0].message.content

        cursor.execute("""
            INSERT INTO sugestoes_ia (usuario_id, pergunta, resposta)
            VALUES (%s, %s, %s)
        """, (
            usuario_id,
            "Análise financeira geral",
            analise_gerada
        ))

        conn.commit()

        return jsonify({
            "analise": analise_gerada
        })

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


@app.route("/ia/sugestoes", methods=["GET"])
def listar_sugestoes_ia():

    # Esta rota lista o histórico de sugestões geradas pela IA.
    #
    # Cada análise financeira gerada é salva no banco e pode ser consultada
    # depois pelo usuário. O retorno é feito em JSON, com data e hora
    # formatadas para facilitar a leitura no frontend.
    if "id" not in session:
        return jsonify({"erro": "Usuário não autenticado."}), 401

    usuario_id = session["id"]

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                id,
                pergunta,
                resposta,
                criado_em
            FROM sugestoes_ia
            WHERE usuario_id = %s
            ORDER BY criado_em DESC
        """, (usuario_id,))

        sugestoes = cursor.fetchall()

        for item in sugestoes:
            item["criado_em"] = formatar_datahora_br(item["criado_em"])

        return jsonify(sugestoes)

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

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