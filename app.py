from flask import Flask, render_template, request, redirect, url_for
from config_banco import conectar, criar_tabelas
from datetime import datetime

app = Flask(__name__)

criar_tabelas()

# --- Rota Principal ---
@app.route('/')
def index():
    return render_template('index.html')

# --- Rota de Cadastro ---
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        identificacao = request.form.get('identificacao')
        fase_atual = request.form.get('fase_atual')
        data_inicio = request.form.get('data_inicio')

        conexao = conectar()
        conexao.execute(
            'INSERT INTO lotes (identificacao, fase_atual, data_inicio) VALUES (?, ?, ?)',
            (identificacao, fase_atual, data_inicio)
        )
        conexao.commit()
        conexao.close()

        return redirect(url_for('cadastro'))

    return render_template('cadastro.html')

# --- Rota do Painel ---
@app.route('/painel')
def painel():
    custo_total = 12500.00
    total_arrobas_ganhas = 50.0
    preco_mercado = 245.00
    custo_recria = 190.00
    custo_terminacao = 270.00

    custo_arroba = custo_total / total_arrobas_ganhas
    lucro = True if preco_mercado >= custo_arroba else False

    return render_template(
        'painel.html',
        custo_arroba=custo_arroba,
        lucro=lucro,
        custo_recria=custo_recria,
        custo_terminacao=custo_terminacao
    )

# --- Rota de Despesas ---
@app.route('/despesas', methods=['GET', 'POST'])
def despesas():
    conexao = conectar()

    if request.method == 'POST':
        categoria = request.form.get('categoria')
        valor = request.form.get('valor')

        conexao.execute(
            'INSERT INTO despesas (categoria, valor) VALUES (?, ?)',
            (categoria, valor)
        )
        conexao.commit()
        conexao.close()

        return redirect(url_for('despesas'))

    lista_despesas = conexao.execute('SELECT * FROM despesas').fetchall()
    conexao.close()

    return render_template('despesas.html', despesas=lista_despesas)

@app.route('/despesas/excluir/<int:id_despesa>', methods=['POST'])
def excluir_despesa(id_despesa):
    conexao = conectar()
    conexao.execute('DELETE FROM despesas WHERE id = ?', (id_despesa,))
    conexao.commit()
    conexao.close()

    return redirect(url_for('despesas'))

# --- Rota de Pesagem ---
@app.route('/pesagem', methods=['GET', 'POST'])
def pesagem():
    conexao = conectar()

    if request.method == 'POST':
        peso = request.form.get('peso')
        data = request.form.get('data')

        conexao.execute(
            'INSERT INTO pesagens (peso, data) VALUES (?, ?)',
            (peso, data)
        )
        conexao.commit()
        conexao.close()

        return redirect(url_for('pesagem'))

    registros = conexao.execute('SELECT * FROM pesagens').fetchall()
    conexao.close()

    # Ordena por data para calcular o GMD (Ganho Médio Diário) entre pesagens
    registros_ordenados = sorted(registros, key=lambda r: r['data'])

    lista_pesagens = []
    anterior = None

    for r in registros_ordenados:
        gmd = None
        if anterior is not None:
            data_atual = datetime.strptime(r['data'], '%Y-%m-%d')
            data_anterior = datetime.strptime(anterior['data'], '%Y-%m-%d')
            dias = (data_atual - data_anterior).days
            if dias > 0:
                gmd = (r['peso'] - anterior['peso']) / dias

        lista_pesagens.append({
            'data': r['data'],
            'peso': r['peso'],
            'gmd': gmd
        })
        anterior = r

    return render_template('pesagem.html', pesagens=lista_pesagens)

if __name__ == '__main__':
    app.run(debug=True)