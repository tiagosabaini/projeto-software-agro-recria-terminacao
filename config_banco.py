import sqlite3
import os

CAMINHO_BANCO = os.path.join(os.path.dirname(__file__), 'dados.db')


def conectar():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    return conexao


def criar_tabelas():
    conexao = conectar()
    cursor = conexao.cursor()

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

    conexao.commit()
    conexao.close()