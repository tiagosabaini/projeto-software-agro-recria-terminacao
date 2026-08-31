from datetime import datetime
from flask import Flask, redirect, render_template, request, url_for
from config_banco import conectar, criar_tabelas

app = Flask(__name__)
criar_tabelas()

# Filtro para converter data do formato do banco para o padrão brasileiro
@app.template_filter('data_br')
def data_br(data_iso):
    if not data_iso:
        return "Não informada"
    try:
        obj_data = datetime.strptime(data_iso, '%Y-%m-%d')
        return obj_data.strftime('%d/%m/%Y')
    except:
        return data_iso


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        identificacao = request.form.get('identificacao')
        fase_atual = request.form.get('fase_atual')
        categoria_animal = request.form.get('categoria_animal')
        
        # Pega a data, mas se vier vazia, salva como None
        data_inicio = request.form.get('data_inicio')
        if not data_inicio:
            data_inicio = None
            
        qtd_cabecas = int(request.form.get('qtd_cabecas', 0))
        custo_bezerro_unitario = float(request.form.get('custo_bezerro_unitario', 0))
        
        custo_total_compra = qtd_cabecas * custo_bezerro_unitario

        conexao = conectar()
        conexao.execute('''
            INSERT INTO lotes (identificacao, fase_atual, categoria_animal, data_inicio, qtd_cabecas, custo_bezerro_unitario, custo_total_compra)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (identificacao, fase_atual, categoria_animal, data_inicio, qtd_cabecas, custo_bezerro_unitario, custo_total_compra))
        conexao.commit()
        conexao.close()
        return redirect(url_for('lotes'))

    return render_template('cadastro.html')


@app.route('/lotes')
def lotes():
    conexao = conectar()
    lista_lotes = conexao.execute('SELECT * FROM lotes ORDER BY id DESC').fetchall()
    conexao.close()
    return render_template('lotes.html', lotes=lista_lotes)


@app.route('/editar_lote/<int:id>', methods=['GET', 'POST'])
def editar_lote(id):
    conexao = conectar()
    if request.method == 'POST':
        nova_fase = request.form.get('fase_atual')
        nova_categoria = request.form.get('categoria_animal')
        
        conexao.execute('''
            UPDATE lotes SET fase_atual = ?, categoria_animal = ? WHERE id = ?
        ''', (nova_fase, nova_categoria, id))
        conexao.commit()
        conexao.close()
        return redirect(url_for('lotes'))
        
    lote = conexao.execute('SELECT * FROM lotes WHERE id = ?', (id,)).fetchone()
    conexao.close()
    return render_template('editar_lote.html', lote=lote)


@app.route('/despesas', methods=['GET', 'POST'])
def despesas():
    conexao = conectar()

    if request.method == 'POST':
        tipo_lancamento = request.form.get('tipo_lancamento')
        lote_id = request.form.get('lote_id')

        # Lançamento Simples
        if tipo_lancamento == 'direto':
            categoria = request.form.get('categoria')
            valor = float(request.form.get('valor'))
            obs = request.form.get('observacao', '')
            conexao.execute(
                'INSERT INTO despesas (lote_id, categoria, valor, observacao) VALUES (?, ?, ?, ?)',
                (lote_id, categoria, valor, obs)
            )

        # Lançamento de Pastagem (Qtd Bois x Meses x Valor Mensal)
        elif tipo_lancamento == 'pastagem':
            qtd_bois = int(request.form.get('qtd_bois', 0))
            meses = float(request.form.get('meses', 0))
            valor_mes_cabeca = float(request.form.get('valor_mes_cabeca', 0))
            valor_total = qtd_bois * meses * valor_mes_cabeca
            obs = f"Pasto: {qtd_bois} cab. x {meses} meses x R$ {valor_mes_cabeca:.2f}/mês"
            conexao.execute(
                'INSERT INTO despesas (lote_id, categoria, valor, observacao) VALUES (?, ?, ?, ?)',
                (lote_id, 'Pastagem', valor_total, obs)
            )

        # Lançamento Nutrição/Sal (Fórmula exata do caderno do pai)
        elif tipo_lancamento == 'nutricao':
            gramas_dia = float(request.form.get('gramas_dia', 0))
            meses = float(request.form.get('meses_nutricao', 0))
            peso_saco_kg = float(request.form.get('peso_saco_kg', 25))
            preco_saco = float(request.form.get('preco_saco', 0))
            qtd_bois = int(request.form.get('qtd_bois_nutricao', 0))
            valor_adicional = float(request.form.get('valor_adicional', 0)) # Ex: SuperGold

            # Cálculo: (g/dia * 30 dias * meses) / (peso_saco_kg * 1000)
            gramas_total_por_boi = gramas_dia * 30 * meses
            sacos_por_boi = gramas_total_por_boi / (peso_saco_kg * 1000)
            custo_sal_por_boi = sacos_por_boi * preco_saco
            custo_sal_total = (custo_sal_por_boi * qtd_bois) + valor_adicional

            obs = f"Sal/Proteinado: {gramas_dia}g/dia em {meses}m ({qtd_bois} bois) + Adicional"
            conexao.execute(
                'INSERT INTO despesas (lote_id, categoria, valor, observacao) VALUES (?, ?, ?, ?)',
                (lote_id, 'Sal/Proteinado', custo_sal_total, obs)
            )

        conexao.commit()
        conexao.close()
        return redirect(url_for('despesas'))

    lista_despesas = conexao.execute('''
        SELECT despesas.*, lotes.identificacao
        FROM despesas
        JOIN lotes ON despesas.lote_id = lotes.id
        ORDER BY despesas.id DESC
    ''').fetchall()
    lista_lotes = conexao.execute('SELECT * FROM lotes WHERE status = "Em Andamento"').fetchall()
    conexao.close()

    return render_template('despesas.html', despesas=lista_despesas, lotes=lista_lotes)


@app.route('/excluir_despesa/<int:id_despesa>', methods=['POST'])
def excluir_despesa(id_despesa):
    conexao = conectar()
    conexao.execute('DELETE FROM despesas WHERE id = ?', (id_despesa,))
    conexao.commit()
    conexao.close()
    return redirect(url_for('despesas'))


@app.route('/pesagem', methods=['GET', 'POST'])
def pesagem():
    conexao = conectar()

    if request.method == 'POST':
        lote_id = request.form.get('lote_id')
        peso = float(request.form.get('peso'))
        data = request.form.get('data')

        conexao.execute(
            'INSERT INTO pesagens (lote_id, peso, data) VALUES (?, ?, ?)',
            (lote_id, peso, data)
        )
        conexao.commit()
        conexao.close()
        return redirect(url_for('pesagem'))

    registros = conexao.execute('''
        SELECT pesagens.*, lotes.identificacao
        FROM pesagens
        JOIN lotes ON pesagens.lote_id = lotes.id
    ''').fetchall()
    lista_lotes = conexao.execute('SELECT * FROM lotes WHERE status = "Em Andamento"').fetchall()
    conexao.close()

    registros_ordenados = sorted(registros, key=lambda r: r['data'])
    lista_pesagens = []
    anterior_por_lote = {}

    for r in registros_ordenados:
        anterior = anterior_por_lote.get(r['lote_id'])
        gmd = None
        if anterior is not None:
            data_atual = datetime.strptime(r['data'], '%Y-%m-%d')
            data_anterior = datetime.strptime(anterior['data'], '%Y-%m-%d')
            dias = (data_atual - data_anterior).days
            if dias > 0:
                gmd = (r['peso'] - anterior['peso']) / dias

        lista_pesagens.append({
            'identificacao': r['identificacao'],
            'data': r['data'],
            'peso': r['peso'],
            'gmd': gmd
        })
        anterior_por_lote[r['lote_id']] = r

    return render_template('pesagem.html', pesagens=lista_pesagens, lotes=lista_lotes)


@app.route('/registrar_venda', methods=['POST'])
def registrar_venda():
    lote_id = request.form.get('lote_id')
    valor_venda_total = float(request.form.get('valor_venda_total', 0))
    total_arrobas_vendidas = float(request.form.get('total_arrobas_vendidas', 0))

    conexao = conectar()
    conexao.execute('''
        UPDATE lotes 
        SET valor_venda_total = ?, total_arrobas_vendidas = ?, status = 'Finalizado'
        WHERE id = ?
    ''', (valor_venda_total, total_arrobas_vendidas, lote_id))
    conexao.commit()
    conexao.close()
    return redirect(url_for('painel', lote_id=lote_id))


@app.route('/painel')
def painel():
    conexao = conectar()
    lista_lotes = conexao.execute('SELECT * FROM lotes').fetchall()

    lote_id = request.args.get('lote_id', type=int)
    lote_selecionado = None
    custo_despesas = 0
    balanco_final = None

    if lote_id:
        lote_selecionado = conexao.execute(
            'SELECT * FROM lotes WHERE id = ?', (lote_id,)
        ).fetchone()

        custo_despesas = conexao.execute(
            'SELECT COALESCE(SUM(valor), 0) as total FROM despesas WHERE lote_id = ?',
            (lote_id,)
        ).fetchone()['total']

        if lote_selecionado:
            # Cálculo de fechamento do lote (Venda do Frigorífico - Compra Bezerros - Despesas)
            receita_venda = lote_selecionado['valor_venda_total'] or 0.0
            
            custo_total_operacao = lote_selecionado['custo_total_compra'] + custo_despesas
            sobra_liquida = receita_venda - custo_total_operacao

            balanco_final = {
                'custo_compra_bezerros': lote_selecionado['custo_total_compra'],
                'custo_despesas': custo_despesas,
                'custo_total_operacao': custo_total_operacao,
                'receita_venda': receita_venda,
                'sobra_liquida': sobra_liquida
            }

    conexao.close()

    return render_template(
        'painel.html',
        lotes=lista_lotes,
        lote_selecionado=lote_selecionado,
        balanco=balanco_final
    )


if __name__ == '__main__':
    app.run(debug=True)