# app_flask.py

from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import json
import logging

# configuração do Flask
app = Flask(__name__)
# chave secreta é necessária para usar flash messages (para exibir erros no HTML)
app.config['SECRET_KEY'] = 'uma_chave_secreta_facil_de_lembrar' 

# configuração da URL da API do FastAPI (Porta 8000)
API_BASE_URL = 'http://127.0.0.1:8000/livros'
FLASK_PORT = 5000

# configuração básica de logging
logging.basicConfig(level=logging.INFO)

@app.route('/', methods=('GET', 'POST'))
def index():
    """
    Rota principal:
    - GET: Busca e lista todos os livros via API.
    - POST: Envia os dados do formulário para a API cadastrar um novo livro.
    """
    if request.method == 'POST':
        # --- 1. coleta e preparação dos dados do formulário para cadastrar novos livros ---
        try:
            # o checkbox 'disponivel' é 'on' se marcado, senão é none
            is_disponivel = request.form.get('disponivel') == 'on'
            ano_publicacao = int(request.form['ano_publicacao'])
            
            # corpo da requisição no formato JSON, conforme exigido pela API Pydantic
            novo_livro = {
                'titulo': request.form['titulo'],
                'autor': request.form['autor'],
                'ano_publicacao': ano_publicacao,
                'disponivel': is_disponivel
            }

            # --- 2. Chamada POST para a API FastAPI ---
            logging.info(f"Enviando POST para API: {novo_livro}")
            response = requests.post(API_BASE_URL, json=novo_livro)

            # --- 3. tratamento da resposta da API ---
            if response.status_code == 201:
                flash('Livro cadastrado com sucesso!', 'success')
            else:
                # se a API retornar algum erro (ex: 422 Unprocessable Entity por validação utilizando o Pydantic)
                try:
                    erro_api = response.json()
                    mensagem_erro = f"Erro ao cadastrar (Status {response.status_code}): {erro_api.get('detail', 'Erro desconhecido da API')}"
                except json.JSONDecodeError:
                    mensagem_erro = f"Erro desconhecido (Status {response.status_code}). Verifique a API."
                    
                flash(mensagem_erro, 'error')
            
        except ValueError:
            flash('Erro: O ano de publicação deve ser um número inteiro válido.', 'error')
        except requests.exceptions.ConnectionError:
            flash(f'Erro de conexão: Verifique se a API do FastAPI está rodando na porta 8000.', 'error')
        except Exception as e:
            flash(f'Ocorreu um erro inesperado: {e}', 'error')

        # faz o redirecionamento para o GET após o POST
        return redirect(url_for('index'))
    
    # --- processamento GET: listagem dos Livros ---
    livros = []
    try:
        # aqui está chamando o GET para a API FastAPI!
        response = requests.get(API_BASE_URL)
        
        if response.status_code == 200:
            livros = response.json()
        else:
            flash(f'Erro ao buscar livros na API (Status {response.status_code}).', 'error')

    except requests.exceptions.ConnectionError:
        flash(f'Erro de conexão: A API do FastAPI não está disponível em http://127.0.0.1:8000.', 'error')
    
    # renderiza o template, passando a lista de livros (vazia em caso de erro)
    return render_template('index.html', livros=livros)

# execução do aplicativo que deve estar rodando na porta 8000
if __name__ == '__main__':
    logging.info(f"Flask rodando em http://127.0.0.1:{FLASK_PORT}")
    logging.info("Certifique-se de que a API do FastAPI esteja rodando na porta 8000.")
    app.run(debug=True, port=FLASK_PORT)