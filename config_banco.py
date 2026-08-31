import sqlite3

def conectar():
    conexao = sqlite3.connect('dados.db')
    conexao.row_factory = sqlite3.Row
    return conexao

def criar_tabelas():
    conexao = conectar()
    
    # Cria a tabela de Lotes com a nova coluna categoria_animal
    conexao.execute('''
        CREATE TABLE IF NOT EXISTS lotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            identificacao TEXT NOT NULL,
            fase_atual TEXT NOT NULL,
            categoria_animal TEXT,
            data_inicio TEXT,
            qtd_cabecas INTEGER,
            custo_bezerro_unitario REAL,
            custo_total_compra REAL,
            valor_venda_total REAL,
            total_arrobas_vendidas REAL,
            status TEXT DEFAULT 'Em Andamento'
        )
    ''')
    
    # Cria a tabela de Despesas
    conexao.execute('''
        CREATE TABLE IF NOT EXISTS despesas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lote_id INTEGER,
            categoria TEXT,
            valor REAL,
            observacao TEXT,
            FOREIGN KEY(lote_id) REFERENCES lotes(id)
        )
    ''')
    
    # Cria a tabela de Pesagens
    conexao.execute('''
        CREATE TABLE IF NOT EXISTS pesagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lote_id INTEGER,
            peso REAL,
            data TEXT,
            FOREIGN KEY(lote_id) REFERENCES lotes(id)
        )
    ''')
    
    conexao.commit()
    conexao.close()