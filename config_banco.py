import sqlite3

def conectar():
    conexao = sqlite3.connect('dados.db')
    conexao.row_factory = sqlite3.Row
    # Ativa as Foreign Keys para garantir a exclusão em cascata e integridade
    conexao.execute('PRAGMA foreign_keys = ON;') 
    return conexao

def criar_tabelas():
    conexao = conectar()
    try:
        with conexao: # Garante o commit de todas as tabelas
            # Tabela de Lotes
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
            
            # Tabela de Despesas (com ON DELETE CASCADE)
            conexao.execute('''
                CREATE TABLE IF NOT EXISTS despesas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lote_id INTEGER,
                    categoria TEXT,
                    valor REAL,
                    observacao TEXT,
                    FOREIGN KEY(lote_id) REFERENCES lotes(id) ON DELETE CASCADE
                )
            ''')
            
            # Tabela de Pesagens (com ON DELETE CASCADE)
            conexao.execute('''
                CREATE TABLE IF NOT EXISTS pesagens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lote_id INTEGER,
                    peso REAL,
                    data TEXT,
                    FOREIGN KEY(lote_id) REFERENCES lotes(id) ON DELETE CASCADE
                )
            ''')
            
            # Tabela de Consumo de Sal/Cocho (com ON DELETE CASCADE)
            conexao.execute('''
                CREATE TABLE IF NOT EXISTS consumo_sal (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lote_id INTEGER,
                    data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    qtd_sacos REAL,
                    peso_saco_kg REAL,
                    dias INTEGER,
                    qtd_bois INTEGER,
                    gramas_cab_dia REAL,
                    FOREIGN KEY(lote_id) REFERENCES lotes(id) ON DELETE CASCADE
                )
            ''')
    finally:
        conexao.close()