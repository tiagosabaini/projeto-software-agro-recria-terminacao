@app.route('/pesagem')
def pesagem():
    # gmd = (peso_atual - peso_anterior) / dias
    return render_template('pesagem.html')