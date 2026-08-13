from flask import Flask, render_template

app = Flask(__name__)

@app.route('/painel')
def painel():
    # Simulando os dados que seriam puxados do banco de dados (brModelo/ORM)
    custo_total = 12500.00
    total_arrobas_ganhas = 50.0
    
    # A sua fórmula matemática
    custo_arroba = custo_total / total_arrobas_ganhas
    
    return render_template('painel.html', custo_arroba=custo_arroba)

if __name__ == '__main__':
    app.run(debug=True)