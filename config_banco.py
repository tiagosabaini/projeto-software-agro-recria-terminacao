import os
import sqlite3

CAMINHO_BANCO = os.path.join(os.path.dirname(__file__), 'dados.db')


def conectar():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    return conexao


def criar_tabelas():
    conexao = conectar()
    cursor = conexao.cursor()

    # Tabela de Lotes com dados de compra e venda
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            identificacao TEXT NOT NULL,
            fase_atual TEXT NOT NULL,
            data_inicio TEXT NOT NULL,
            qtd_cabecas INTEGER DEFAULT 0,
            custo_bezerro_unitario REAL DEFAULT 0,
            custo_total_compra REAL DEFAULT 0,
            valor_venda_total REAL DEFAULT 0,
            total_arrobas_vendidas REAL DEFAULT 0,
            status TEXT DEFAULT 'Em Andamento'
        )
    ''')

    # Tabela de Despesas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS despesas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lote_id INTEGER NOT NULL,
            categoria TEXT NOT NULL,
            valor REAL NOT NULL,
            observacao TEXT,
            FOREIGN KEY (lote_id) REFERENCES lotes(id)
        )
    ''')

    # Tabela de Pesagens
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pesagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lote_id INTEGER NOT NULL,
            peso REAL NOT NULL,
            data TEXT NOT NULL,
            FOREIGN KEY (lote_id) REFERENCES lotes(id)
        )
    ''')

    # Migrações de colunas para bancos existentes
    colunas_lotes = [
        ("qtd_cabecas", "INTEGER DEFAULT 0"),
        ("custo_bezerro_unitario", "REAL DEFAULT 0"),
        ("custo_total_compra", "REAL DEFAULT 0"),
        ("valor_venda_total", "REAL DEFAULT 0"),
        ("total_arrobas_vendidas", "REAL DEFAULT 0"),
        ("status", "TEXT DEFAULT 'Em Andamento'")
    ]
    for col, tipo in colunas_lotes:
        try:
            cursor.execute(f"ALTER TABLE lotes ADD COLUMN {col} {tipo};")
        except sqlite3.OperationalError:
            pass

    conexao.commit()
    conexao.close()


if __name__ == '__main__':
    criar_tabelas()