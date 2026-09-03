from datetime import datetime
from flask import Flask, redirect, render_template, request, url_for
from config_banco import conectar, criar_tabelas

app = Flask(__name__)

# Garante que as tabelas e colunas existam ao iniciar
criar_tabelas()


# --- Rota Principal ---
@app.route('/')
def index():
    return render_template('index.html')


# --- Rota de Cadastro de Lote ---
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        identificacao = request.form.get('identificacao')
        fase_atual = request.form.get('fase_atual')
        data_inicio = request.form.get('data_inicio')

        if identificacao and fase_atual and data_inicio:
            conexao = conectar()
            conexao.execute(
                'INSERT INTO lotes (identificacao, fase_atual, data_inicio)'
                ' VALUES (?, ?, ?)',
                (identificacao, fase_atual, data_inicio),
            )
            conexao.commit()
            conexao.close()

        return redirect(url_for('cadastro'))

    return render_template('cadastro.html')


# --- Rota do Painel ---
@app.route('/painel')
def painel():
    conexao = conectar()

    despesas_recria = conexao.execute(
        "SELECT COALESCE(SUM(valor), 0) as total FROM despesas WHERE fase ="
        " 'Recria'"
    ).fetchone()['total']

    despesas_terminacao = conexao.execute(
        "SELECT COALESCE(SUM(valor), 0) as total FROM despesas WHERE fase ="
        " 'Terminação'"
    ).fetchone()['total']

    pesagens = conexao.execute(
        'SELECT peso FROM pesagens ORDER BY data ASC'
    ).fetchall()
    conexao.close()

    custo_total = despesas_recria + despesas_terminacao
    custo_arroba = None
    custo_recria = None
    custo_terminacao = None
    lucro = None

    if len(pesagens) >= 2:
        ganho_peso_kg = pesagens[-1]['peso'] - pesagens[0]['peso']

        if ganho_peso_kg > 0:
            total_arrobas_ganhas = ganho_peso_kg / 15
            preco_mercado = 245.00

            custo_arroba = round(custo_total / total_arrobas_ganhas, 2)
            custo_recria = round(despesas_recria / total_arrobas_ganhas, 2)
            custo_terminacao = round(
                despesas_terminacao / total_arrobas_ganhas, 2
            )
            lucro = preco_mercado >= custo_arroba

    return render_template(
        'painel.html',
        custo_arroba=custo_arroba,
        lucro=lucro,
        custo_recria=custo_recria,
        custo_terminacao=custo_terminacao,
    )


# --- Rota de Despesas ---
@app.route('/despesas', methods=['GET', 'POST'])
def despesas():
    conexao = conectar()

    if request.method == 'POST':
        categoria = request.form.get('categoria')
        fase = request.form.get('fase')
        valor_raw = request.form.get('valor')

        if categoria and fase and valor_raw:
            try:
                valor = float(valor_raw)
                conexao.execute(
                    'INSERT INTO despesas (categoria, fase, valor) VALUES (?, ?,'
                    ' ?)',
                    (categoria, fase, valor),
                )
                conexao.commit()
            except ValueError:
                pass

        conexao.close()
        return redirect(url_for('despesas'))

    lista_despesas = conexao.execute('SELECT * FROM despesas').fetchall()
    conexao.close()

    return render_template('despesas.html', despesas=lista_despesas)


# --- Rota de Exclusão de Despesa ---
@app.route('/excluir_despesa/<int:id_despesa>', methods=['POST'])
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
        peso_raw = request.form.get('peso')
        data = request.form.get('data')

        if peso_raw and data:
            try:
                peso = float(peso_raw)
                conexao.execute(
                    'INSERT INTO pesagens (peso, data) VALUES (?, ?)',
                    (peso, data),
                )
                conexao.commit()
            except ValueError:
                pass

        conexao.close()
        return redirect(url_for('pesagem'))

    registros = conexao.execute('SELECT * FROM pesagens').fetchall()
    conexao.close()

    registros_ordenados = sorted(registros, key=lambda r: r['data'])

    lista_pesagens = []
    anterior = None

    for r in registros_ordenados:
        gmd = None
        if anterior is not None:
            try:
                data_atual = datetime.strptime(r['data'], '%Y-%m-%d')
                data_anterior = datetime.strptime(anterior['data'], '%Y-%m-%d')
                dias = (data_atual - data_anterior).days
                if dias > 0:
                    gmd = round((r['peso'] - anterior['peso']) / dias, 3)
            except ValueError:
                gmd = None

        lista_pesagens.append({
            'data': r['data'],
            'peso': r['peso'],
            'gmd': gmd,
        })
        anterior = r

    return render_template('pesagem.html', pesagens=lista_pesagens)


if __name__ == '__main__':
    app.run(debug=True)