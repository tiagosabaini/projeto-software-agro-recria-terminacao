from datetime import datetime
from flask import Flask, redirect, render_template, request, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from config_banco import conectar, criar_tabelas

app = Flask(__name__)
# Chave de segurança obrigatória para o Flask proteger os cookies de login
app.secret_key = 'chave_secreta_agro_2026' 
criar_tabelas()

def configurar_sistema():
    conexao = conectar()
    
    # 1. Tabela de Usuários com Nível de Acesso
    conexao.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            usuario TEXT UNIQUE,
            senha TEXT,
            nivel_acesso TEXT
        )
    ''')
    usuario_existe = conexao.execute('SELECT * FROM usuarios').fetchone()
    if not usuario_existe:
        # Criptografando as senhas antes de salvar no banco
        senha_produtor = generate_password_hash('1234')
        senha_tiago = generate_password_hash('admin2026')
        
        # Cria o usuário normal (que vai ser avaliado pela professora)
        conexao.execute('INSERT INTO usuarios (nome, usuario, senha, nivel_acesso) VALUES (?, ?, ?, ?)', 
                        ('Produtor Rural', 'admin', senha_produtor, 'comum'))
        
        # Cria o SEU usuário de SysAdmin (Dono do Sistema)
        conexao.execute('INSERT INTO usuarios (nome, usuario, senha, nivel_acesso) VALUES (?, ?, ?, ?)', 
                        ('Tiago Sabaini (SysAdmin)', 'tiago', senha_tiago, 'sysadmin'))
    
    # 2. Tabela da API de Cotações
    conexao.execute('''
        CREATE TABLE IF NOT EXISTS cotacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            frigorifico TEXT UNIQUE,
            preco REAL
        )
    ''')
    if not conexao.execute('SELECT * FROM cotacoes').fetchone():
        conexao.execute('INSERT INTO cotacoes (frigorifico, preco) VALUES (?, ?)', ('JBS', 275.0))
        conexao.execute('INSERT INTO cotacoes (frigorifico, preco) VALUES (?, ?)', ('Frigon', 278.0))
        conexao.execute('INSERT INTO cotacoes (frigorifico, preco) VALUES (?, ?)', ('Minerva', 274.0))
        
    try:
        conexao.execute('ALTER TABLE lotes ADD COLUMN frigorifico_comprador TEXT')
    except:
        pass 

    conexao.commit()
    conexao.close()

configurar_sistema() 
def configurar_sistema():
    conexao = conectar()
    
    # 1. Tabela de Usuários com Nível de Acesso
    conexao.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            usuario TEXT UNIQUE,
            senha TEXT,
            nivel_acesso TEXT
        )
    ''')
    usuario_existe = conexao.execute('SELECT * FROM usuarios').fetchone()
    if not usuario_existe:
        # Criptografando as senhas antes de salvar no banco
        senha_produtor = generate_password_hash('1234')
        senha_tiago = generate_password_hash('admin2026')
        
        # Cria o usuário normal (que vai ser avaliado pela professora)
        conexao.execute('INSERT INTO usuarios (nome, usuario, senha, nivel_acesso) VALUES (?, ?, ?, ?)', 
                        ('Produtor Rural', 'admin', senha_produtor, 'comum'))
        
        # Cria o SEU usuário de SysAdmin (Dono do Sistema)
        conexao.execute('INSERT INTO usuarios (nome, usuario, senha, nivel_acesso) VALUES (?, ?, ?, ?)', 
                        ('Tiago Sabaini (SysAdmin)', 'tiago', senha_tiago, 'sysadmin'))
    
    # 2. Tabela da API de Cotações
    conexao.execute('''
        CREATE TABLE IF NOT EXISTS cotacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            frigorifico TEXT UNIQUE,
            preco REAL
        )
    ''')
    if not conexao.execute('SELECT * FROM cotacoes').fetchone():
        conexao.execute('INSERT INTO cotacoes (frigorifico, preco) VALUES (?, ?)', ('JBS', 275.0))
        conexao.execute('INSERT INTO cotacoes (frigorifico, preco) VALUES (?, ?)', ('Frigon', 278.0))
        conexao.execute('INSERT INTO cotacoes (frigorifico, preco) VALUES (?, ?)', ('Minerva', 274.0))
        
    try:
        conexao.execute('ALTER TABLE lotes ADD COLUMN frigorifico_comprador TEXT')
    except:
        pass 

    conexao.commit()
    conexao.close()

configurar_sistema()

# --- CONTROLE DE ACESSO GLOBAL ---
@app.before_request
def verificar_login():
    # Permite acesso à tela de login, arquivos CSS/JS e consumo da API de Cotações
    rotas_livres = ['login', 'static', 'api_cotacoes']
    if request.endpoint not in rotas_livres and 'usuario_id' not in session:
        return redirect(url_for('login'))

# --- ROTAS DE AUTENTICAÇÃO ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')
        
        conexao = conectar()
        user = conexao.execute('SELECT * FROM usuarios WHERE usuario = ?', (usuario,)).fetchone()
        conexao.close()
        
        # Verifica se o usuário existe E se a senha descriptografada bate com a digitada
        if user and check_password_hash(user['senha'], senha):
            session['usuario_id'] = user['id']
            session['nome_usuario'] = user['nome']
            session['nivel_acesso'] = user['nivel_acesso'] # Guarda o nível na sessão
            return redirect(url_for('index'))
        else:
            flash('Usuário ou senha incorretos!', 'erro')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear() # Limpa os dados do usuário e sai do sistema
    return redirect(url_for('login'))

# --- ROTAS DA API INTERNA E CONFIGURAÇÃO DE PREÇOS ---
@app.route('/api/cotacoes')
def api_cotacoes():
    conexao = conectar()
    try:
        cotacoes = conexao.execute('SELECT * FROM cotacoes').fetchall()
        # Converte para JSON ex: {"JBS": 275.0, "Frigon": 278.0}
        dados = {c['frigorifico']: c['preco'] for c in cotacoes}
        return jsonify(dados)
    finally:
        conexao.close()

@app.route('/admin_cotacoes', methods=['GET', 'POST'])
def admin_cotacoes():
    # BARREIRA DE SEGURANÇA (RBAC): Somente o SysAdmin passa daqui
    if session.get('nivel_acesso') != 'sysadmin':
        return "Erro 403: Acesso Proibido. Você não possui privilégios de SysAdmin para editar a API do sistema.", 403

    conexao = conectar()
    try:
        if request.method == 'POST':
            preco_jbs = float(request.form.get('JBS', 0))
            preco_frigon = float(request.form.get('Frigon', 0))
            preco_minerva = float(request.form.get('Minerva', 0))
            
            with conexao:
                conexao.execute('UPDATE cotacoes SET preco = ? WHERE frigorifico = ?', (preco_jbs, 'JBS'))
                conexao.execute('UPDATE cotacoes SET preco = ? WHERE frigorifico = ?', (preco_frigon, 'Frigon'))
                conexao.execute('UPDATE cotacoes SET preco = ? WHERE frigorifico = ?', (preco_minerva, 'Minerva'))
            
            flash('Cotações da região atualizadas na API com sucesso!', 'sucesso')
            return redirect(url_for('admin_cotacoes'))
            
        cotacoes = conexao.execute('SELECT * FROM cotacoes').fetchall()
    finally:
        conexao.close()
    return render_template('cotacoes.html', cotacoes=cotacoes)

# --- FILTROS DE DATA ---
@app.template_filter('data_br')
def data_br(data_iso):
    if not data_iso:
        return "Não informada"
    try:
        obj_data = datetime.strptime(data_iso, '%Y-%m-%d')
        return obj_data.strftime('%d/%m/%Y')
    except:
        return data_iso

# --- ROTAS DO SISTEMA (CONTEÚDO PRINCIPAL) ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        identificacao = request.form.get('identificacao')
        fase_atual = request.form.get('fase_atual')
        categoria_animal = request.form.get('categoria_animal')
        
        data_inicio = request.form.get('data_inicio') or None
        qtd_cabecas = int(request.form.get('qtd_cabecas', 0))
        custo_bezerro_unitario = float(request.form.get('custo_bezerro_unitario', 0))
        custo_total_compra = qtd_cabecas * custo_bezerro_unitario

        conexao = conectar()
        try:
            with conexao:
                conexao.execute('''
                    INSERT INTO lotes (identificacao, fase_atual, categoria_animal, data_inicio, qtd_cabecas, custo_bezerro_unitario, custo_total_compra)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (identificacao, fase_atual, categoria_animal, data_inicio, qtd_cabecas, custo_bezerro_unitario, custo_total_compra))
        finally:
            conexao.close()
        return redirect(url_for('lotes'))

    return render_template('cadastro.html')

@app.route('/lotes')
def lotes():
    conexao = conectar()
    try:
        lista_lotes = conexao.execute('SELECT * FROM lotes ORDER BY id DESC').fetchall()
    finally:
        conexao.close()
    return render_template('lotes.html', lotes=lista_lotes)

@app.route('/excluir_lote/<int:id>', methods=['POST'])
def excluir_lote(id):
    conexao = conectar()
    try:
        with conexao:
            conexao.execute('DELETE FROM lotes WHERE id = ?', (id,))
    finally:
        conexao.close()
    return redirect(url_for('lotes'))

@app.route('/editar_lote/<int:id>', methods=['GET', 'POST'])
def editar_lote(id):
    conexao = conectar()
    try:
        if request.method == 'POST':
            nova_fase = request.form.get('fase_atual')
            nova_categoria = request.form.get('categoria_animal')
            with conexao:
                conexao.execute('''
                    UPDATE lotes SET fase_atual = ?, categoria_animal = ? WHERE id = ?
                ''', (nova_fase, nova_categoria, id))
            return redirect(url_for('lotes'))
            
        lote = conexao.execute('SELECT * FROM lotes WHERE id = ?', (id,)).fetchone()
    finally:
        conexao.close()
    return render_template('editar_lote.html', lote=lote)

@app.route('/despesas', methods=['GET', 'POST'])
def despesas():
    conexao = conectar()
    try:
        if request.method == 'POST':
            tipo_lancamento = request.form.get('tipo_lancamento')
            lote_id = request.form.get('lote_id')

            with conexao:
                if tipo_lancamento == 'direto':
                    categoria = request.form.get('categoria')
                    valor = float(request.form.get('valor'))
                    obs = request.form.get('observacao', '')
                    conexao.execute(
                        'INSERT INTO despesas (lote_id, categoria, valor, observacao) VALUES (?, ?, ?, ?)',
                        (lote_id, categoria, valor, obs)
                    )

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

                elif tipo_lancamento == 'nutricao':
                    qtd_sacos = float(request.form.get('qtd_sacos', 0))
                    preco_saco = float(request.form.get('preco_saco', 0))
                    qtd_bois = int(request.form.get('qtd_bois_nutricao', 1))
                    valor_adicional = float(request.form.get('valor_adicional', 0))

                    custo_total = (qtd_sacos * preco_saco) + valor_adicional
                    custo_por_cabeca = custo_total / qtd_bois if qtd_bois > 0 else 0
                    obs = f"Compra: {qtd_sacos} saco(s). Custo por cabeça: R$ {custo_por_cabeca:.2f} ({qtd_bois} bois)."
                    
                    conexao.execute(
                        'INSERT INTO despesas (lote_id, categoria, valor, observacao) VALUES (?, ?, ?, ?)',
                        (lote_id, 'Sal/Proteinado', custo_total, obs)
                    )
            return redirect(url_for('despesas'))

        lista_despesas = conexao.execute('''
            SELECT despesas.*, lotes.identificacao
            FROM despesas
            JOIN lotes ON despesas.lote_id = lotes.id
            ORDER BY despesas.id DESC
        ''').fetchall()
        lista_lotes = conexao.execute('SELECT * FROM lotes WHERE status = "Em Andamento"').fetchall()
    finally:
        conexao.close()

    return render_template('despesas.html', despesas=lista_despesas, lotes=lista_lotes)

@app.route('/excluir_despesa/<int:id_despesa>', methods=['POST'])
def excluir_despesa(id_despesa):
    conexao = conectar()
    try:
        with conexao:
            conexao.execute('DELETE FROM despesas WHERE id = ?', (id_despesa,))
    finally:
        conexao.close()
    return redirect(url_for('despesas'))

@app.route('/pesagem', methods=['GET', 'POST'])
def pesagem():
    conexao = conectar()
    try:
        if request.method == 'POST':
            lote_id = request.form.get('lote_id')
            peso = float(request.form.get('peso'))
            data = request.form.get('data')

            with conexao:
                conexao.execute(
                    'INSERT INTO pesagens (lote_id, peso, data) VALUES (?, ?, ?)',
                    (lote_id, peso, data)
                )
            return redirect(url_for('pesagem'))

        registros = conexao.execute('''
            SELECT pesagens.*, lotes.identificacao
            FROM pesagens
            JOIN lotes ON pesagens.lote_id = lotes.id
        ''').fetchall()
        lista_lotes = conexao.execute('SELECT * FROM lotes WHERE status = "Em Andamento"').fetchall()
    finally:
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

    lista_pesagens.reverse()

    return render_template('pesagem.html', pesagens=lista_pesagens, lotes=lista_lotes)

@app.route('/consumo_cocho', methods=['GET', 'POST'])
def consumo_cocho():
    conexao = conectar()
    lote_selecionado = None
    historico_consumo = []
    
    try:
        conexao.execute('''
            CREATE TABLE IF NOT EXISTS consumo_sal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lote_id INTEGER,
                data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                qtd_sacos REAL,
                peso_saco_kg REAL,
                dias INTEGER,
                qtd_bois INTEGER,
                gramas_cab_dia REAL,
                FOREIGN KEY(lote_id) REFERENCES lotes(id) ON DELETE CASCADE
            )
        ''')
        conexao.commit()

        lista_lotes = conexao.execute('SELECT * FROM lotes').fetchall()

        if request.method == 'POST':
            lote_id = request.form.get('lote_id')
            tipo_acao = request.form.get('tipo_acao')

            if tipo_acao == 'registrar':
                qtd_sacos = float(request.form.get('qtd_sacos', 0))
                peso_saco_kg = float(request.form.get('peso_saco_kg', 25))
                dias = int(request.form.get('dias', 1))
                qtd_bois = int(request.form.get('qtd_bois', 1))

                peso_total_kg = qtd_sacos * peso_saco_kg
                gramas_cab_dia = (peso_total_kg * 1000) / (dias * qtd_bois) if (dias > 0 and qtd_bois > 0) else 0

                with conexao:
                    conexao.execute('''
                        INSERT INTO consumo_sal (lote_id, qtd_sacos, peso_saco_kg, dias, qtd_bois, gramas_cab_dia)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (lote_id, qtd_sacos, peso_saco_kg, dias, qtd_bois, gramas_cab_dia))
            
            if lote_id:
                lote_selecionado = conexao.execute('SELECT * FROM lotes WHERE id = ?', (int(lote_id),)).fetchone()
                historico_consumo = conexao.execute('''
                    SELECT * FROM consumo_sal WHERE lote_id = ? ORDER BY id DESC
                ''', (int(lote_id),)).fetchall()
    finally:
        conexao.close()
        
    return render_template('consumo.html', lotes=lista_lotes, lote_selecionado=lote_selecionado, historico_consumo=historico_consumo)

@app.route('/registrar_venda', methods=['POST'])
def registrar_venda():
    lote_id = request.form.get('lote_id')
    frigorifico = request.form.get('frigorifico_comprador') # Pegando quem comprou
    qtd_vendida = int(request.form.get('qtd_vendida', 0))
    valor_venda = float(request.form.get('valor_venda_total', 0))
    arrobas_vendidas = float(request.form.get('total_arrobas_vendidas', 0))

    conexao = conectar()
    try:
        with conexao:
            # Puxa os dados atuais do lote antes da venda
            lote = conexao.execute('SELECT qtd_cabecas, valor_venda_total, total_arrobas_vendidas FROM lotes WHERE id = ?', (lote_id,)).fetchone()
            
            if lote:
                qtd_atual = lote['qtd_cabecas'] or 0
                valor_atual = lote['valor_venda_total'] or 0.0
                arrobas_atual = lote['total_arrobas_vendidas'] or 0.0
                
                # Calcula os novos valores (Deduz as cabeças e Acumula o dinheiro/arrobas)
                nova_qtd = max(0, qtd_atual - qtd_vendida)
                novo_valor_total = valor_atual + valor_venda
                novo_total_arrobas = arrobas_atual + arrobas_vendidas
                
                # Inteligência do Status: Se zerou os bois, finaliza. Senão, continua.
                novo_status = 'Finalizado' if nova_qtd == 0 else 'Em Andamento'
                
                # Atualiza o banco de dados salvando também o frigorífico comprador
                conexao.execute('''
                    UPDATE lotes 
                    SET qtd_cabecas = ?, valor_venda_total = ?, total_arrobas_vendidas = ?, status = ?, frigorifico_comprador = ?
                    WHERE id = ?
                ''', (nova_qtd, novo_valor_total, novo_total_arrobas, novo_status, frigorifico, lote_id))
    finally:
        conexao.close()
        
    return redirect(url_for('painel', lote_id=lote_id))
    
@app.route('/painel')
def painel():
    conexao = conectar()
    try:
        lista_lotes = conexao.execute('SELECT * FROM lotes').fetchall()
        lote_id = request.args.get('lote_id', type=int)
        
        lote_selecionado = None
        custo_despesas = 0
        balanco_final = None

        if lote_id:
            lote_selecionado = conexao.execute('SELECT * FROM lotes WHERE id = ?', (lote_id,)).fetchone()
            custo_despesas = conexao.execute('SELECT COALESCE(SUM(valor), 0) as total FROM despesas WHERE lote_id = ?', (lote_id,)).fetchone()['total']

            if lote_selecionado:
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
    finally:
        conexao.close()

    return render_template('painel.html', lotes=lista_lotes, lote_selecionado=lote_selecionado, balanco=balanco_final)

if __name__ == '__main__':
    app.run(debug=True)