from flask import Flask, render_template, request, redirect, url_for

# 1. Inicializa o aplicativo UMA única vez
app = Flask(__name__)

# --- Rota Principal ---
@app.route('/')
def index():
    return render_template('index.html')

# --- Rota de Cadastro ---
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        # Captura os dados enviados pelo formulário
        identificacao = request.form.get('identificacao')
        fase_atual = request.form.get('fase_atual')
        data_inicio = request.form.get('data_inicio')
        
        # Exibe no terminal para confirmação de recebimento dos dados
        print(f"Lote cadastrado: {identificacao} | Fase: {fase_atual} | Data: {data_inicio}")
        
        # Redireciona de volta após o envio via POST
        return redirect(url_for('cadastro'))

    # Se a requisição for GET, apenas renderiza a página do formulário
    return render_template('cadastro.html')

# --- Rota do Painel ---
@app.route('/painel')
def painel():
    # Dados extraídos via ORM
    custo_total = 12500.00
    total_arrobas_ganhas = 50.0
    
    # Preço mínimo de venda recomendado (Cotação do frigorífico)
    preco_mercado = 245.00 
    
    # Histórico de custos por fase
    custo_recria = 190.00
    custo_terminacao = 270.00

    # Fórmulas
    custo_arroba = custo_total / total_arrobas_ganhas
    
    # Regra de Negócio: Indicação de Lucro/Prejuízo (Ponto de Equilíbrio)
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
    # Exemplo da lógica de verificação
    meta_gmd = 0.8  # Ex: 800g por dia
    # gmd = (peso_atual - peso_anterior) / dias
    # atingiu_meta = gmd >= meta_gmd
    return render_template('pesagem.html')

# 2. Executa o aplicativo no final do arquivo
if __name__ == '__main__':
    app.run(debug=True)