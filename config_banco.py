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

    # 1. Criação das tabelas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            identificacao TEXT NOT NULL,
            fase_atual TEXT NOT NULL,
            data_inicio TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS despesas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria TEXT NOT NULL,
            valor REAL NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pesagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            peso REAL NOT NULL,
            data TEXT NOT NULL
        )
    ''')

    # 2. Adição da nova coluna na tabela existente
    try:
        cursor.execute(
            "ALTER TABLE despesas ADD COLUMN fase TEXT NOT NULL DEFAULT"
            " 'Recria';"
        )
    except sqlite3.OperationalError:
        # A coluna já existe, ignora o erro
        pass

    conexao.commit()
    conexao.close()


# Executa a função para criar/atualizar o banco
if __name__ == '__main__':
    criar_tabelas()