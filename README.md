# MeuBolso Inteligente

## Visão geral

Aplicação web em Flask para ajudar no controle financeiro pessoal com cadastro de receitas, despesas, dashboards, relatórios, feedbacks e análise de IA.

O sistema permite que usuários façam login, registrem entradas e saídas, visualizem o saldo, consultem relatórios por categoria e recebam sugestões financeiras geradas por IA.

## Funcionalidades principais

- Autenticação de usuários (login e cadastro)
- Dashboard com totais de receitas, despesas e saldo
- Cadastro e listagem de receitas
- Cadastro e listagem de despesas
- Relatórios de despesas por categoria
- Feedback do usuário com nota e comentário
- Análises financeiras automáticas usando Groq AI
- Histórico de sugestões de IA

## Estrutura do projeto

- `backend/app.py` - aplicação Flask, rotas e lógica principal
- `backend/db.py` - conexão com MySQL
- `backend/config.py` - configuração de variáveis de ambiente
- `backend/ia.py` - cliente Groq para integração com IA
- `backend/templates/` - páginas HTML
- `backend/static/` - arquivos estáticos CSS/JS
- `database/meubolso.sql` - schema do banco de dados e dados iniciais

## Tecnologias

- Python 3
- Flask
- Flask-CORS
- MySQL
- mysql-connector-python
- python-dotenv
- Groq AI

## Pré-requisitos

- Python 3.11+ (ou compatível)
- MySQL em execução
- Chave de API Groq válida

## Instalação e execução

1. Clone o repositório:

```bash
git clone https://seu-repositorio.git
cd meubolso-inteligente
```

2. Crie e ative um ambiente virtual:

```bash
python -m venv venv
venv\Scripts\activate
```

3. Instale as dependências:

```bash
pip install -r backend/requirements.txt
```

4. Crie um arquivo `.env` na raiz do projeto baseado em `.env.example`.

5. Importe o banco de dados MySQL:

```bash
mysql -u <usuario> -p < database/meubolso.sql
```

6. Execute a aplicação:

```bash
cd backend
python app.py
```

7. Acesse no navegador:

```text
http://127.0.0.1:5000/
```

## Variáveis de ambiente

O arquivo `.env` deve conter:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=meubolso_inteligente
DB_PORT=3306
GROQ_API_KEY=
SECRET_KEY=
```

### Secret Key do Flask

A chave `SECRET_KEY` deve ser gerada pelo desenvolvedor e adicionada ao arquivo `.env`.
O valor é usado em `backend/app.py` para proteger as sessões do Flask e não deve ser enviado a repositórios públicos.

Para gerar uma chave forte, use o Python:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Em seguida, copie o valor gerado para `SECRET_KEY` no `.env`.

## Rotas principais

- `/` - página inicial
- `/login` - login
- `/cadastro` - cadastro de usuário
- `/dashboard` - painel principal
- `/receitas` - cadastro de receitas
- `/despesas` - cadastro de despesas
- `/relatorios` - página de relatórios
- `/feedback` - página de feedback
- `/ia` - página de análise por IA

## APIs internas

- `/dashboard/dados`
- `/dashboard/despesas-categorias/`
- `/receitas/listar`
- `/despesas/listar`
- `/relatorios/despesas-categorias`
- `/feedbacks`
- `/ia/analise-financeira`
- `/ia/sugestoes`

## Banco de dados

O arquivo `database/meubolso.sql` cria as seguintes tabelas:

- `usuarios`
- `categorias`
- `receitas`
- `despesas`
- `metas_financeiras`
- `sugestoes_ia`
- `feedbacks`

Também insere categorias iniciais de receita e despesa.

## Observações

- A chave da API Groq é obrigatória para usar a funcionalidade de IA.
- A aplicação roda em modo de desenvolvimento com `debug=True`.

## Contato

Para dúvidas ou melhorias, abra uma issue no repositório ou entre em contato com o mantenedor.
