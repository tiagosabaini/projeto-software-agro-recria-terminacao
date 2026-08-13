from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

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

if __name__ == '__main__':
    app.run(debug=True)