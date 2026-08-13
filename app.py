from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

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
        
        print(f"Lote cadastrado: {identificacao} | Fase: {fase_atual} | Data: {data_inicio}")
        return redirect(url_for('cadastro'))

    return render_template('cadastro.html')

# --- Rota de Despesas ---
@app.route('/despesas')
def despesas():
    return render_template('despesas.html')

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

# --- Rota de Pesagem ---
@app.route('/pesagem', methods=['GET', 'POST'])
def pesagem():
    return render_template('pesagem.html')

if __name__ == '__main__':
    app.run(debug=True)