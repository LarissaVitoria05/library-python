from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import requests
import json
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'uma_chave_secreta_facil_de_lembrar' 

API_BASE_URL = 'http://127.0.0.1:8000/livros'
FLASK_PORT = 5000

logging.basicConfig(level=logging.INFO)

@app.route('/', methods=('GET', 'POST'))
def index():
    """
    Rota principal HTML:
    - GET: Busca e lista todos os livros via API.
    - POST: Envia os dados do formulário para a API cadastrar um novo livro.
    """
    if request.method == 'POST':
        try:
            is_disponivel = request.form.get('disponivel') == 'on'
            ano_publicacao = int(request.form['ano_publicacao'])
            
            novo_livro = {
                'titulo': request.form['titulo'],
                'autor': request.form['autor'],
                'ano_publicacao': ano_publicacao,
                'disponivel': is_disponivel
            }

            logging.info(f"Enviando POST para API: {novo_livro}")
            response = requests.post(API_BASE_URL, json=novo_livro)

            if response.status_code == 201:
                flash('Livro cadastrado com sucesso!', 'success')
            else:
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

        return redirect(url_for('index'))
    
    livros = []
    try:
        response = requests.get(API_BASE_URL)
        
        if response.status_code == 200:
            livros = response.json()
        else:
            flash(f'Erro ao buscar livros na API (Status {response.status_code}).', 'error')

    except requests.exceptions.ConnectionError:
        flash(f'Erro de conexão: A API do FastAPI não está disponível em http://127.0.0.1:8000.', 'error')
    
    return render_template('index.html', livros=livros)


# ========== ROTAS JSON (API REST) ==========

@app.route('/api/livros', methods=['GET'])
def api_listar_livros():
    """
    Retorna todos os livros em formato JSON
    """
    try:
        response = requests.get(API_BASE_URL)
        
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({
                "erro": "Erro ao buscar livros na API FastAPI",
                "status": response.status_code
            }), response.status_code

    except requests.exceptions.ConnectionError:
        return jsonify({
            "erro": "A API do FastAPI não está disponível",
            "detalhes": "Verifique se está rodando na porta 8000"
        }), 503


@app.route('/api/livros/<int:id>', methods=['GET'])
def api_buscar_livro(id):
    """
    Retorna um livro específico em formato JSON
    """
    try:
        response = requests.get(f"{API_BASE_URL}/{id}")
        
        if response.status_code == 200:
            return jsonify(response.json()), 200
        elif response.status_code == 404:
            return jsonify({
                "erro": f"Livro com ID {id} não encontrado"
            }), 404
        else:
            return jsonify({
                "erro": "Erro ao buscar livro",
                "status": response.status_code
            }), response.status_code

    except requests.exceptions.ConnectionError:
        return jsonify({
            "erro": "A API do FastAPI não está disponível"
        }), 503


@app.route('/api/livros', methods=['POST'])
def api_adicionar_livro():
    """
    Adiciona um novo livro via JSON
    Espera um body JSON com: titulo, autor, ano_publicacao, disponivel
    """
    try:
        dados = request.get_json()
        
        if not dados:
            return jsonify({
                "erro": "Body JSON não fornecido"
            }), 400
        
        response = requests.post(API_BASE_URL, json=dados)
        
        if response.status_code == 201:
            return jsonify(response.json()), 201
        else:
            return jsonify({
                "erro": "Erro ao cadastrar livro",
                "detalhes": response.json(),
                "status": response.status_code
            }), response.status_code

    except requests.exceptions.ConnectionError:
        return jsonify({
            "erro": "A API do FastAPI não está disponível"
        }), 503


@app.route('/api/livros/<int:id>', methods=['PUT'])
def api_atualizar_livro(id):
    """
    Atualiza um livro existente via JSON
    """
    try:
        dados = request.get_json()
        
        if not dados:
            return jsonify({
                "erro": "Body JSON não fornecido"
            }), 400
        
        response = requests.put(f"{API_BASE_URL}/{id}", json=dados)
        
        if response.status_code == 200:
            return jsonify(response.json()), 200
        elif response.status_code == 404:
            return jsonify({
                "erro": f"Livro com ID {id} não encontrado"
            }), 404
        else:
            return jsonify({
                "erro": "Erro ao atualizar livro",
                "status": response.status_code
            }), response.status_code

    except requests.exceptions.ConnectionError:
        return jsonify({
            "erro": "A API do FastAPI não está disponível"
        }), 503


@app.route('/api/livros/<int:id>', methods=['DELETE'])
def api_excluir_livro(id):
    """
    Exclui um livro
    """
    try:
        response = requests.delete(f"{API_BASE_URL}/{id}")
        
        if response.status_code == 200:
            return jsonify(response.json()), 200
        elif response.status_code == 404:
            return jsonify({
                "erro": f"Livro com ID {id} não encontrado"
            }), 404
        else:
            return jsonify({
                "erro": "Erro ao excluir livro",
                "status": response.status_code
            }), response.status_code

    except requests.exceptions.ConnectionError:
        return jsonify({
            "erro": "A API do FastAPI não está disponível"
        }), 503


if __name__ == '__main__':
    logging.info(f"Flask rodando em http://127.0.0.1:{FLASK_PORT}")
    logging.info("Interface HTML: http://127.0.0.1:5000/")
    logging.info("API JSON: http://127.0.0.1:5000/api/livros")
    logging.info("Certifique-se de que a API do FastAPI esteja rodando na porta 8000.")
    app.run(debug=True, port=FLASK_PORT)