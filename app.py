import os
import secrets
from datetime import datetime, timedelta
from flask import Flask, redirect, render_template, request, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from config_banco import conectar, criar_tabelas



app = Flask(__name__)

# Chave secreta estável (evita invalidar tokens CSRF e sessões ao reiniciar o servidor)
app.secret_key = os.getenv('SECRET_KEY', 'agro_chave_secreta_super_segura_2026')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

criar_tabelas()

def configurar_sistema():
    conexao = conectar()
    try:
        with conexao:
            # 1. Tabela de Usuários com Nível de Acesso (RBAC)
            conexao.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT,
                    usuario TEXT UNIQUE,
                    senha TEXT,
                    nivel_acesso TEXT
                )
            ''')
            if not conexao.execute('SELECT 1 FROM usuarios LIMIT 1').fetchone():
                senha_produtor_raw = os.getenv('SENHA_PRODUTOR_INICIAL', '1234')
                senha_admin_raw = os.getenv('SENHA_ADMIN_INICIAL', 'admin2026')

                conexao.execute(
                    'INSERT INTO usuarios (nome, usuario, senha, nivel_acesso) VALUES (?, ?, ?, ?)',
                    ('Produtor Rural', 'admin', generate_password_hash(senha_produtor_raw), 'comum')
                )
                conexao.execute(
                    'INSERT INTO usuarios (nome, usuario, senha, nivel_acesso) VALUES (?, ?, ?, ?)',
                    ('Tiago Sabaini (SysAdmin)', 'tiago', generate_password_hash(senha_admin_raw), 'sysadmin')
                )

            # 2. Tabela de Cotações
            conexao.execute('''
                CREATE TABLE IF NOT EXISTS cotacoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    frigorifico TEXT UNIQUE,
                    preco REAL
                )
            ''')
            if not conexao.execute('SELECT 1 FROM cotacoes LIMIT 1').fetchone():
                conexao.execute('INSERT INTO cotacoes (frigorifico, preco) VALUES (?, ?)', ('JBS', 275.0))
                conexao.execute('INSERT INTO cotacoes (frigorifico, preco) VALUES (?, ?)', ('Frigon', 278.0))
                conexao.execute('INSERT INTO cotacoes (frigorifico, preco) VALUES (?, ?)', ('Minerva', 274.0))

            # Adição segura de colunas nos Lotes
            try:
                conexao.execute('ALTER TABLE lotes ADD COLUMN frigorifico_comprador TEXT')
            except:
                pass
            try:
                conexao.execute('ALTER TABLE lotes ADD COLUMN qtd_vendida_total INTEGER DEFAULT 0')
            except:
                pass
    finally:
        conexao.close()



# Injeta automaticamente o token CSRF em todos os templates Jinja2
@app.context_processor
def inject_csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)
    return dict(csrf_token=session['csrf_token'])

# --- CONTROLE DE ACESSO, SEGURANÇA E VALIDAÇÃO CSRF ---
@app.before_request
def verificar_seguranca_global():
    # Garante que sempre exista um token na sessão ativa
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)

    # Rotas liberadas sem necessidade de login
    rotas_livres = ['login', 'static', 'api_cotacoes']
    if request.endpoint not in rotas_livres and 'usuario_id' not in session:
        return redirect(url_for('login'))

    # Validação CSRF em requisições POST (exceto endpoint público da API e login)
    if request.method == 'POST' and request.endpoint not in ['api_cotacoes', 'login']:
        token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
        if not token or token != session.get('csrf_token'):
            return "Erro 403: Falha na validação CSRF. Requisição rejeitada por segurança.", 403

# --- AUTENTICAÇÃO COM MITIGAÇÃO DE FORÇA BRUTA ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Bloqueio temporário por tentativas repetidas
        bloqueado_ate = session.get('bloqueado_ate')
        if bloqueado_ate:
            tempo_restante = datetime.fromisoformat(bloqueado_ate) - datetime.now()
            if tempo_restante.total_seconds() > 0:
                minutos = int(tempo_restante.total_seconds() // 60) + 1
                flash(f'Muitas tentativas incorretas. Bloqueado por mais {minutos} minuto(s).', 'erro')
                return render_template('login.html')
            else:
                session.pop('bloqueado_ate', None)
                session['tentativas_login'] = 0

        usuario = (request.form.get('usuario') or '').strip()
        senha = request.form.get('senha') or ''

        conexao = conectar()
        user = conexao.execute('SELECT * FROM usuarios WHERE usuario = ?', (usuario,)).fetchone()
        conexao.close()

        if user and check_password_hash(user['senha'], senha):
            session.clear()
            session['usuario_id'] = user['id']
            session['nome_usuario'] = user['nome']
            session['nivel_acesso'] = user['nivel_acesso']
            session['csrf_token'] = secrets.token_hex(32)
            return redirect(url_for('index'))
        else:
            tentativas = session.get('tentativas_login', 0) + 1
            session['tentativas_login'] = tentativas
            if tentativas >= 5:
                session['bloqueado_ate'] = (datetime.now() + timedelta(minutes=5)).isoformat()
                flash('Limite de 5 tentativas atingido. Bloqueado por 5 minutos.', 'erro')
            else:
                flash(f'Usuário ou senha incorretos! ({5 - tentativas} tentativa(s) restante(s))', 'erro')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- API DE COTAÇÕES E PAINEL ADMIN (SYSADMIN) ---
@app.route('/api/cotacoes')
def api_cotacoes():
    """Endpoint público intencional para integração com balanças e painéis externos."""
    conexao = conectar()
    try:
        cotacoes = conexao.execute('SELECT * FROM cotacoes').fetchall()
        dados = {c['frigorifico']: c['preco'] for c in cotacoes}
        return jsonify(dados)
    finally:
        conexao.close()

@app.route('/admin_cotacoes', methods=['GET', 'POST'])
def admin_cotacoes():
    if session.get('nivel_acesso') != 'sysadmin':
        return "Erro 403: Acesso Proibido. Exclusivo para SysAdmin.", 403

    conexao = conectar()
    try:
        if request.method == 'POST':
            preco_jbs = max(0.0, float(request.form.get('JBS', 0)))
            preco_frigon = max(0.0, float(request.form.get('Frigon', 0)))
            preco_minerva = max(0.0, float(request.form.get('Minerva', 0)))

            with conexao:
                conexao.execute('UPDATE cotacoes SET preco = ? WHERE frigorifico = ?', (preco_jbs, 'JBS'))
                conexao.execute('UPDATE cotacoes SET preco = ? WHERE frigorifico = ?', (preco_frigon, 'Frigon'))
                conexao.execute('UPDATE cotacoes SET preco = ? WHERE frigorifico = ?', (preco_minerva, 'Minerva'))

            flash('Cotações atualizadas com sucesso!', 'sucesso')
            return redirect(url_for('admin_cotacoes'))

        cotacoes = conexao.execute('SELECT * FROM cotacoes').fetchall()
    finally:
        conexao.close()
    return render_template('cotacoes.html', cotacoes=cotacoes)

# --- FILTROS DE TEMPLATE ---
@app.template_filter('data_br')
def data_br(data_iso):
    if not data_iso:
        return "Não informada"
    try:
        return datetime.strptime(data_iso, '%Y-%m-%d').strftime('%d/%m/%Y')
    except:
        return data_iso

# --- ROTAS PRINCIPAIS ---
@app.route('/')
def index():
    return render_template('index.html')

# === CRUD: LOTES ===
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        identificacao = request.form.get('identificacao', '').strip()
        fase_atual = request.form.get('fase_atual')
        categoria_animal = request.form.get('categoria_animal')
        data_inicio = request.form.get('data_inicio') or None
        qtd_cabecas = max(1, int(request.form.get('qtd_cabecas', 0)))
        custo_unitario = max(0.0, float(request.form.get('custo_bezerro_unitario', 0)))
        custo_total = qtd_cabecas * custo_unitario

        conexao = conectar()
        try:
            with conexao:
                conexao.execute('''
                    INSERT INTO lotes (identificacao, fase_atual, categoria_animal, data_inicio, qtd_cabecas, custo_bezerro_unitario, custo_total_compra)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (identificacao, fase_atual, categoria_animal, data_inicio, qtd_cabecas, custo_unitario, custo_total))
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

@app.route('/editar_lote/<int:id>', methods=['GET', 'POST'])
def editar_lote(id):
    conexao = conectar()
    try:
        if request.method == 'POST':
            identificacao = request.form.get('identificacao', '').strip()
            fase = request.form.get('fase_atual')
            categoria = request.form.get('categoria_animal')
            qtd_cabecas = max(0, int(request.form.get('qtd_cabecas', 0)))
            custo_unitario = max(0.0, float(request.form.get('custo_bezerro_unitario', 0)))
            custo_total = qtd_cabecas * custo_unitario

            with conexao:
                conexao.execute('''
                    UPDATE lotes 
                    SET identificacao = ?, fase_atual = ?, categoria_animal = ?, qtd_cabecas = ?, custo_bezerro_unitario = ?, custo_total_compra = ?
                    WHERE id = ?
                ''', (identificacao, fase, categoria, qtd_cabecas, custo_unitario, custo_total, id))
            return redirect(url_for('lotes'))

        lote = conexao.execute('SELECT * FROM lotes WHERE id = ?', (id,)).fetchone()
    finally:
        conexao.close()
    return render_template('editar_lote.html', lote=lote)

@app.route('/excluir_lote/<int:id>', methods=['POST'])
def excluir_lote(id):
    conexao = conectar()
    try:
        with conexao:
            conexao.execute('DELETE FROM lotes WHERE id = ?', (id,))
    finally:
        conexao.close()
    return redirect(url_for('lotes'))

# === CRUD: DESPESAS ===
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
                    valor = max(0.01, float(request.form.get('valor', 0)))
                    obs = request.form.get('observacao', '').strip()
                    conexao.execute(
                        'INSERT INTO despesas (lote_id, categoria, valor, observacao) VALUES (?, ?, ?, ?)',
                        (lote_id, categoria, valor, obs)
                    )
                elif tipo_lancamento == 'pastagem':
                    qtd_bois = max(1, int(request.form.get('qtd_bois', 0)))
                    meses = max(0.1, float(request.form.get('meses', 0)))
                    valor_mes = max(0.0, float(request.form.get('valor_mes_cabeca', 0)))
                    total = qtd_bois * meses * valor_mes
                    obs = f"Pasto: {qtd_bois} cab. x {meses} meses x R$ {valor_mes:.2f}/mês"
                    conexao.execute(
                        'INSERT INTO despesas (lote_id, categoria, valor, observacao) VALUES (?, ?, ?, ?)',
                        (lote_id, 'Pastagem', total, obs)
                    )
                elif tipo_lancamento == 'nutricao':
                    qtd_sacos = max(0.1, float(request.form.get('qtd_sacos', 0)))
                    preco = max(0.0, float(request.form.get('preco_saco', 0)))
                    qtd_bois = max(1, int(request.form.get('qtd_bois_nutricao', 1)))
                    adicional = max(0.0, float(request.form.get('valor_adicional', 0)))
                    total = (qtd_sacos * preco) + adicional
                    por_cabeca = total / qtd_bois
                    obs = f"Sal/Prot: {qtd_sacos} sacos. R$ {por_cabeca:.2f}/cab ({qtd_bois} animais)."
                    conexao.execute(
                        'INSERT INTO despesas (lote_id, categoria, valor, observacao) VALUES (?, ?, ?, ?)',
                        (lote_id, 'Sal/Proteinado', total, obs)
                    )
            return redirect(url_for('despesas'))

        despesas_lista = conexao.execute('''
            SELECT despesas.*, lotes.identificacao 
            FROM despesas JOIN lotes ON despesas.lote_id = lotes.id 
            ORDER BY despesas.id DESC
        ''').fetchall()
        lotes_ativos = conexao.execute('SELECT * FROM lotes WHERE status = "Em Andamento"').fetchall()
    finally:
        conexao.close()
    return render_template('despesas.html', despesas=despesas_lista, lotes=lotes_ativos)

@app.route('/editar_despesa/<int:id>', methods=['GET', 'POST'])
def editar_despesa(id):
    conexao = conectar()
    try:
        if request.method == 'POST':
            categoria = request.form.get('categoria')
            valor = max(0.01, float(request.form.get('valor', 0)))
            obs = request.form.get('observacao', '').strip()
            with conexao:
                conexao.execute('UPDATE despesas SET categoria = ?, valor = ?, observacao = ? WHERE id = ?',
                                (categoria, valor, obs, id))
            return redirect(url_for('despesas'))
        despesa = conexao.execute('SELECT * FROM despesas WHERE id = ?', (id,)).fetchone()
    finally:
        conexao.close()
    return render_template('editar_despesa.html', despesa=despesa)

@app.route('/excluir_despesa/<int:id_despesa>', methods=['POST'])
def excluir_despesa(id_despesa):
    conexao = conectar()
    try:
        with conexao:
            conexao.execute('DELETE FROM despesas WHERE id = ?', (id_despesa,))
    finally:
        conexao.close()
    return redirect(url_for('despesas'))

# === CRUD: PESAGENS ===
@app.route('/pesagem', methods=['GET', 'POST'])
def pesagem():
    conexao = conectar()
    try:
        if request.method == 'POST':
            lote_id = request.form.get('lote_id')
            peso = max(0.0, float(request.form.get('peso', 0)))
            data = request.form.get('data')
            with conexao:
                conexao.execute('INSERT INTO pesagens (lote_id, peso, data) VALUES (?, ?, ?)',
                                (lote_id, peso, data))
            return redirect(url_for('pesagem'))

        registros = conexao.execute('''
            SELECT pesagens.*, lotes.identificacao
            FROM pesagens JOIN lotes ON pesagens.lote_id = lotes.id
        ''').fetchall()
        lotes_ativos = conexao.execute('SELECT * FROM lotes WHERE status = "Em Andamento"').fetchall()
    finally:
        conexao.close()

    registros_ordenados = sorted(registros, key=lambda r: r['data'])
    lista_pesagens = []
    anterior_por_lote = {}

    for r in registros_ordenados:
        anterior = anterior_por_lote.get(r['lote_id'])
        gmd = None
        if anterior is not None:
            try:
                data_atual = datetime.strptime(r['data'], '%Y-%m-%d')
                data_ant = datetime.strptime(anterior['data'], '%Y-%m-%d')
                dias = (data_atual - data_ant).days
                if dias > 0:
                    gmd = (r['peso'] - anterior['peso']) / dias
            except:
                pass
        lista_pesagens.append({
            'id': r['id'],
            'identificacao': r['identificacao'],
            'data': r['data'],
            'peso': r['peso'],
            'gmd': gmd
        })
        anterior_por_lote[r['lote_id']] = r

    lista_pesagens.reverse()
    return render_template('pesagem.html', pesagens=lista_pesagens, lotes=lotes_ativos)

@app.route('/editar_pesagem/<int:id>', methods=['GET', 'POST'])
def editar_pesagem(id):
    conexao = conectar()
    try:
        if request.method == 'POST':
            peso = max(0.0, float(request.form.get('peso', 0)))
            data = request.form.get('data')
            with conexao:
                conexao.execute('UPDATE pesagens SET peso = ?, data = ? WHERE id = ?', (peso, data, id))
            return redirect(url_for('pesagem'))
        pesagem_item = conexao.execute('SELECT * FROM pesagens WHERE id = ?', (id,)).fetchone()
    finally:
        conexao.close()
    return render_template('editar_pesagem.html', pesagem=pesagem_item)

@app.route('/excluir_pesagem/<int:id>', methods=['POST'])
def excluir_pesagem(id):
    conexao = conectar()
    try:
        with conexao:
            conexao.execute('DELETE FROM pesagens WHERE id = ?', (id,))
    finally:
        conexao.close()
    return redirect(url_for('pesagem'))

# === CRUD: CONSUMO DE COCHO ===
@app.route('/consumo_cocho', methods=['GET', 'POST'])
def consumo_cocho():
    conexao = conectar()
    lote_selecionado = None
    historico = []
    try:
        lista_lotes = conexao.execute('SELECT * FROM lotes').fetchall()
        if request.method == 'POST':
            lote_id = request.form.get('lote_id')
            tipo_acao = request.form.get('tipo_acao')

            if tipo_acao == 'registrar':
                qtd_sacos = max(0.0, float(request.form.get('qtd_sacos', 0)))
                peso_saco = max(1.0, float(request.form.get('peso_saco_kg', 25)))
                dias = max(1, int(request.form.get('dias', 1)))
                qtd_bois = max(1, int(request.form.get('qtd_bois', 1)))

                gramas = ((qtd_sacos * peso_saco) * 1000) / (dias * qtd_bois)

                with conexao:
                    conexao.execute('''
                        INSERT INTO consumo_sal (lote_id, qtd_sacos, peso_saco_kg, dias, qtd_bois, gramas_cab_dia)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (lote_id, qtd_sacos, peso_saco, dias, qtd_bois, gramas))

            if lote_id:
                lote_selecionado = conexao.execute('SELECT * FROM lotes WHERE id = ?', (int(lote_id),)).fetchone()
                historico = conexao.execute('SELECT * FROM consumo_sal WHERE lote_id = ? ORDER BY id DESC', (int(lote_id),)).fetchall()
    finally:
        conexao.close()
    return render_template('consumo.html', lotes=lista_lotes, lote_selecionado=lote_selecionado, historico_consumo=historico)

@app.route('/editar_consumo/<int:id>', methods=['GET', 'POST'])
def editar_consumo(id):
    conexao = conectar()
    try:
        if request.method == 'POST':
            qtd_sacos = max(0.0, float(request.form.get('qtd_sacos', 0)))
            peso_saco = max(1.0, float(request.form.get('peso_saco_kg', 25)))
            dias = max(1, int(request.form.get('dias', 1)))
            qtd_bois = max(1, int(request.form.get('qtd_bois', 1)))
            gramas = ((qtd_sacos * peso_saco) * 1000) / (dias * qtd_bois)

            with conexao:
                conexao.execute('''
                    UPDATE consumo_sal 
                    SET qtd_sacos = ?, peso_saco_kg = ?, dias = ?, qtd_bois = ?, gramas_cab_dia = ?
                    WHERE id = ?
                ''', (qtd_sacos, peso_saco, dias, qtd_bois, gramas, id))
            return redirect(url_for('consumo_cocho'))

        item = conexao.execute('SELECT * FROM consumo_sal WHERE id = ?', (id,)).fetchone()
    finally:
        conexao.close()
    return render_template('editar_consumo.html', item=item)

@app.route('/excluir_consumo/<int:id>', methods=['POST'])
def excluir_consumo(id):
    conexao = conectar()
    try:
        with conexao:
            conexao.execute('DELETE FROM consumo_sal WHERE id = ?', (id,))
    finally:
        conexao.close()
    return redirect(url_for('consumo_cocho'))

# === VENDAS E PAINEL FINANCEIRO ===
@app.route('/registrar_venda', methods=['POST'])
def registrar_venda():
    lote_id = request.form.get('lote_id')
    frigorifico = request.form.get('frigorifico_comprador')
    qtd_vendida = max(1, int(request.form.get('qtd_vendida', 0)))
    valor_venda = max(0.0, float(request.form.get('valor_venda_total', 0)))
    arrobas = max(0.0, float(request.form.get('total_arrobas_vendidas', 0)))

    conexao = conectar()
    try:
        with conexao:
            lote = conexao.execute('SELECT qtd_cabecas, valor_venda_total, total_arrobas_vendidas, qtd_vendida_total FROM lotes WHERE id = ?', (lote_id,)).fetchone()
            if lote:
                nova_qtd = max(0, (lote['qtd_cabecas'] or 0) - qtd_vendida)
                novo_valor = (lote['valor_venda_total'] or 0.0) + valor_venda
                novo_arrobas = (lote['total_arrobas_vendidas'] or 0.0) + arrobas
                novo_total_vendidas = (lote['qtd_vendida_total'] or 0) + qtd_vendida
                novo_status = 'Finalizado' if nova_qtd == 0 else 'Em Andamento'

                conexao.execute('''
                    UPDATE lotes 
                    SET qtd_cabecas = ?, valor_venda_total = ?, total_arrobas_vendidas = ?, status = ?, frigorifico_comprador = ?, qtd_vendida_total = ?
                    WHERE id = ?
                ''', (nova_qtd, novo_valor, novo_arrobas, novo_status, frigorifico, novo_total_vendidas, lote_id))
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
        balanco_final = None

        if lote_id:
            lote_selecionado = conexao.execute('SELECT * FROM lotes WHERE id = ?', (lote_id,)).fetchone()
            custo_despesas = conexao.execute('SELECT COALESCE(SUM(valor), 0) as total FROM despesas WHERE lote_id = ?', (lote_id,)).fetchone()['total']

            if lote_selecionado:
                receita = lote_selecionado['valor_venda_total'] or 0.0
                custo_op = (lote_selecionado['custo_total_compra'] or 0.0) + custo_despesas
                balanco_final = {
                    'custo_compra_bezerros': lote_selecionado['custo_total_compra'] or 0.0,
                    'custo_despesas': custo_despesas,
                    'custo_total_operacao': custo_op,
                    'receita_venda': receita,
                    'sobra_liquida': receita - custo_op
                }
    finally:
        conexao.close()
    return render_template('painel.html', lotes=lista_lotes, lote_selecionado=lote_selecionado, balanco=balanco_final)

if __name__ == '__main__':
    # Debug desativado por padrão para atender os requisitos de produção/segurança
    app.run(debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true')

