@app.route('/pesagem', methods=['GET', 'POST'])
def pesagem():
    # Exemplo da lógica de verificação
    meta_gmd = 0.8  # Ex: 800g por dia
    # gmd = (peso_atual - peso_anterior) / dias
    # atingiu_meta = gmd >= meta_gmd
    return render_template('pesagem.html')