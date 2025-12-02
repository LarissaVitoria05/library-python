import sqlite3

def criar_banco():
    conn = sqlite3.connect('biblioteca.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS livros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            ano_publicacao INTEGER NOT NULL,
            disponivel BOOLEAN NOT NULL DEFAULT 1
        )
    ''')
    
    print("✅ Tabela 'livros' criada com sucesso!")
    
    cursor.execute('SELECT COUNT(*) FROM livros')
    quantidade = cursor.fetchone()[0]
    
    # se vazio, insere dados de exemplo
    if quantidade == 0:
        livros_exemplo = [
            ('1984', 'George Orwell', 1949, 1),
            ('O Senhor dos Anéis', 'J.R.R. Tolkien', 1954, 1),
            ('Dom Casmurro', 'Machado de Assis', 1899, 1),
            ('Harry Potter e a Pedra Filosofal', 'J.K. Rowling', 1997, 0),
            ('Cem Anos de Solidão', 'Gabriel García Márquez', 1967, 1),
            ('O Pequeno Príncipe', 'Antoine de Saint-Exupéry', 1943, 1),
            ('Clean Code', 'Robert C. Martin', 2008, 0),
            ('Python Fluente', 'Luciano Ramalho', 2015, 1)
        ]
        
        cursor.executemany('''
            INSERT INTO livros (titulo, autor, ano_publicacao, disponivel)
            VALUES (?, ?, ?, ?)
        ''', livros_exemplo)
        
        print(f"✅ {len(livros_exemplo)} livros de exemplo inseridos!")
    else:
        print(f"ℹ️  Banco já contém {quantidade} livro(s).")
    
    conn.commit()
    conn.close()
    
    print("\n🎉 Banco de dados pronto para uso!")

def listar_livros():
    conn = sqlite3.connect('biblioteca.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM livros')
    livros = cursor.fetchall()
    
    print("\n📚 LIVROS CADASTRADOS:")
    print("-" * 80)
    for livro in livros:
        disponivel = "Disponível" if livro[4] else "Emprestado"
        print(f"ID: {livro[0]} | {livro[1]} - {livro[2]} ({livro[3]}) | {disponivel}")
    print("-" * 80)
    
    conn.close()

if __name__ == '__main__':
    print("🔧 Inicializando banco de dados da biblioteca...\n")
    criar_banco()
    listar_livros()