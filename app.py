from flask from flask import Flask, render_template

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)