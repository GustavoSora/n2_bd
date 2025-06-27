from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from pymongo.server_api import ServerApi

app = Flask(__name__)
app.secret_key = 'chave_super_secreta'

uri = "mongodb+srv://Sora:Q%21W%40E%23R%2412qwaszx@cluster0.lqogubf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(uri, server_api=ServerApi('1'))

db = client['meu_app']
usuarios_col = db['usuarios']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['senha']
        filho = request.form['filho']
        rua = request.form['rua']

        if usuarios_col.find_one({'nome': nome}):
            return "Usuário já existe!"

        usuarios_col.insert_one({
            'nome': nome,
            'senha': senha,
            'filho': filho,
            'rua': rua
        })
        return redirect(url_for('login'))
    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['senha']
        user = usuarios_col.find_one({'nome': nome, 'senha': senha})
        if user:
            session['usuario'] = nome
            return redirect(url_for('painel'))
        return "Usuário ou senha incorretos!"
    return render_template('login.html')

@app.route('/painel')
def painel():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    user = usuarios_col.find_one({'nome': session['usuario']})
    return render_template('painel.html', nome=user['nome'], filho=user['filho'], rua=user['rua'])

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('/login'))

@app.route('/pesquisar', methods=['GET', 'POST'])
def pesquisar():
    resultado = []
    if request.method == 'POST':
        busca = request.form['busca'].lower()
        resultado = list(usuarios_col.find({'nome': {'$regex': busca, '$options': 'i'}}))
    return render_template('pesquisar.html', resultado=resultado)

@app.route('/documento', methods=['GET', 'POST'])
def documento():
    if request.method == 'POST':
        doc = {
            'campo1': request.form['campo1'],
        }
        db.documentos.insert_one(doc)

        return "Documento cadastrado com sucesso!"
    return render_template('documento.html')


if __name__ == '__main__':
    app.run(debug=True, port=5009)