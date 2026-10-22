import sqlite3

conexao = sqlite3.connect('dados.db')
with open('dump_recria_terminacao.sql', 'w', encoding='utf-8') as f:
    for linha in conexao.iterdump():
        f.write(linha + '\n')
conexao.close()
print('Dump gerado com sucesso!')