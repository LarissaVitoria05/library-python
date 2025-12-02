from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
import sqlite3

app = FastAPI(
    title="API Biblioteca",
    description="API REST para gerenciamento de livros de uma biblioteca",
    version="1.0.0"
)

class Livro(BaseModel):
    titulo: str = Field(..., min_length=1, description="Título do livro")
    autor: str = Field(..., min_length=1, description="Autor do livro")
    ano_publicacao: int = Field(..., gt=0, le=2025, description="Ano de publicação")
    disponivel: bool = Field(default=True, description="Se o livro está disponível")
    
    class Config:
        json_schema_extra = {
            "example": {
                "titulo": "O Hobbit",
                "autor": "J.R.R. Tolkien",
                "ano_publicacao": 1937,
                "disponivel": True
            }
        }

class LivroResponse(Livro):
    id: int

def get_db_connection():
    conn = sqlite3.connect('biblioteca.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/", tags=["Root"])
def read_root():
    return {
        "mensagem": "API da Biblioteca - Sistema de Gerenciamento de Livros",
        "documentacao": "/docs",
        "endpoints": {
            "listar_livros": "GET /livros",
            "buscar_livro": "GET /livros/{id}",
            "adicionar_livro": "POST /livros",
            "atualizar_livro": "PUT /livros/{id}",
            "excluir_livro": "DELETE /livros/{id}"
        }
    }

@app.get("/livros", response_model=list[LivroResponse], tags=["Livros"])
def listar_livros():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM livros')
    livros = cursor.fetchall()
    conn.close()
    
    livros_list = [dict(livro) for livro in livros]
    return livros_list

@app.get("/livros/{id}", response_model=LivroResponse, tags=["Livros"])
def buscar_livro(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM livros WHERE id = ?', (id,))
    livro = cursor.fetchone()
    conn.close()
    
    if livro is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Livro com ID {id} não encontrado"
        )
    
    return dict(livro)

@app.post("/livros", response_model=LivroResponse, status_code=status.HTTP_201_CREATED, tags=["Livros"])
def adicionar_livro(livro: Livro):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO livros (titulo, autor, ano_publicacao, disponivel)
        VALUES (?, ?, ?, ?)
    ''', (livro.titulo, livro.autor, livro.ano_publicacao, livro.disponivel))
    
    conn.commit()
    livro_id = cursor.lastrowid
    conn.close()
    
    return {
        "id": livro_id,
        "titulo": livro.titulo,
        "autor": livro.autor,
        "ano_publicacao": livro.ano_publicacao,
        "disponivel": livro.disponivel
    }

@app.put("/livros/{id}", response_model=LivroResponse, tags=["Livros"])
def atualizar_livro(id: int, livro: Livro):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM livros WHERE id = ?', (id,))
    livro_existente = cursor.fetchone()
    
    if livro_existente is None:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Livro com ID {id} não encontrado"
        )
    
    cursor.execute('''
        UPDATE livros
        SET titulo = ?, autor = ?, ano_publicacao = ?, disponivel = ?
        WHERE id = ?
    ''', (livro.titulo, livro.autor, livro.ano_publicacao, livro.disponivel, id))
    
    conn.commit()
    conn.close()
    
    return {
        "id": id,
        "titulo": livro.titulo,
        "autor": livro.autor,
        "ano_publicacao": livro.ano_publicacao,
        "disponivel": livro.disponivel
    }

@app.delete("/livros/{id}", status_code=status.HTTP_200_OK, tags=["Livros"])
def excluir_livro(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM livros WHERE id = ?', (id,))
    livro = cursor.fetchone()
    
    if livro is None:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Livro com ID {id} não encontrado"
        )
    
    cursor.execute('DELETE FROM livros WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    return {
        "mensagem": f"Livro '{dict(livro)['titulo']}' excluído com sucesso",
        "id": id
    }

# para rodar: uvicorn api_fast:app --reload --port 8000