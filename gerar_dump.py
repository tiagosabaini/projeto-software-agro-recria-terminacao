import sqlite3
import io
from datetime import datetime

def gerar_backup():
    data_atual = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    nome_arquivo = f'dump_recria_terminacao_{data_atual}.sql'
    
    conexao = sqlite3.connect('dados.db')
    with io.open(nome_arquivo, 'w', encoding='utf-8') as f:
        for linha in conexao.iterdump():
            f.write('%s\n' % linha)
    
    conexao.close()
    print(f"✅ Backup de segurança gerado: {nome_arquivo}")

if __name__ == '__main__':
    gerar_backup()