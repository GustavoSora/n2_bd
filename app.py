from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import json

app = Flask(__name__)
app.secret_key = 'chave_super_secreta'


exercicios = [
  {
    "_id": "1",
    "titulo": "Contar quantos discos de cada artista existem na coleção",
    "resposta": "[\n{ $group: { _id: \"$artista\", totalDiscos: { $sum: 1 } } }\n]"
  },
  {
    "_id": "2",
    "titulo": "Corrigir o ano de lançamento de um álbum específico",
    "resposta": "[\n{ $match: { titulo: \"The Dark Side of the Moon\" } },\n{ $set: { anoLancamento: 1974 } }\n]"
  },
  {
    "_id": "3",
    "titulo": "Remover o campo numeroCatalogo de todos os documentos",
    "resposta": "[\n{ $unset: { numeroCatalogo: \"\" } }\n]"
  },
  {
    "_id": "4",
    "titulo": "Calcular a duração total (em minutos) de cada álbum",
    "resposta": "[\n{ $project: { titulo: 1, duracaoTotalMinutos: { $divide: [ { $sum: \"$faixas.duracao_segundos\" }, 60 ] } } }\n]"
  },
  {
    "_id": "5",
    "titulo": "Adicionar um novo gênero a um álbum",
    "resposta": "[\n{ $addToSet: { generos: \"Rock Alternativo\" } }\n]"
  },
  {
    "_id": "6",
    "titulo": "Listar todas as músicas nas quais um dos compositores é 'Roger Waters'",
    "resposta": "[\n{ $unwind: \"$faixas\" },\n{ $match: { \"faixas.compositores\": \"Roger Waters\" } },\n{ $project: { titulo: \"$faixas.titulo\" } }\n]"
  },
  {
    "_id": "7",
    "titulo": "Listar as músicas compostas SOMENTE por 'Roger Waters', excluindo as músicas compostas juntamente com outros compositores",
    "resposta": "[\n{ $unwind: \"$faixas\" },\n{ $match: { \"faixas.compositores\": { $eq: [\"Roger Waters\"] } } },\n{ $project: { titulo: \"$faixas.titulo\" } }\n]"
  },
  {
    "_id": "8",
    "titulo": "Alterar o nome de um dos compositores (digamos que foi digitado errado, ex.: 'Joés' ao invés de 'José')",
    "resposta": "[\n{ $updateMany: { \"faixas.compositores\": \"Joés\" },\n{ $set: { \"faixas.$.compositores.$\": \"José\" } }\n}"
  },
  {
    "_id": "9",
    "titulo": "Encontrar a música mais longa de toda a coleção",
    "resposta": "[\n{ $unwind: \"$faixas\" },\n{ $sort: { \"faixas.duracao_segundos\": -1 } },\n{ $limit: 1 },\n{ $project: { titulo: \"$faixas.titulo\", duracao: \"$faixas.duracao_segundos\" } }\n]"
  },
  {
    "_id": "10",
    "titulo": "Remover um disco inteiro da coleção com base no nome de um dos compositores",
    "resposta": "[\n{ $deleteMany: { \"faixas.compositores\": \"Roger Waters\" } }\n]"
  },
  {
    "_id": "11",
    "titulo": "Calcular o número médio de faixas por disco para cada artista",
    "resposta": "[\n{ $project: { artista: 1, numeroFaixas: { $size: \"$faixas\" } } },\n{ $group: { _id: \"$artista\", mediaFaixas: { $avg: \"$numeroFaixas\" } } }\n]"
  },
  {
    "_id": "12",
    "titulo": "Remover a última faixa do disco quando o nome do compositor for igual ao enviado por parâmetro",
    "resposta": "[\n{ $updateMany: { \"faixas.compositores\": \"Roger Waters\" },\n{ $pop: { faixas: 1 } }\n]"
  }
]




#config mongoDB
uri = "mongodb+srv://leticia:123@clusteraula.8yd0csp.mongodb.net/?retryWrites=true&w=majority&appName=ClusterAula"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

uri = "mongodb+srv://Sora:Q%21W%40E%23R%2412qwaszx@cluster0.lqogubf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(uri, server_api=ServerApi('1'))

db = client['meu_app']
usuarios_col = db['usuarios']

# pega json dos exercicios
path_exercicios = 'JSON/n3perguntas.json'

with open(path_exercicios, 'r') as jsonEx:
    dataEx = json.load(jsonEx)

@app.route('/')
def index():
    return render_template('index.html', dataEx=dataEx)

@app.route('/ex/<int:id>', methods=['GET', 'POST'])
def mostrarExercicio(id=None):
    if request.method == 'POST':
        selected_id = request.form.get('exercicio_id')
        if selected_id:
            return redirect(url_for('/ex', id=selected_id))

    # busca exercicio pelo ID
    exercicio = dataEx[id-1]
    # caso exercicio nao exista volta para o /
    if id <= 0 or id > len(dataEx):
        return redirect(url_for('home'))

    return render_template('exercicio.html', htmlId=exercicio['_id'], htmlTitulo=exercicio['titulo'], htmlResposta=exercicio['resposta'])

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

@app.route('/escolher', methods=['GET', 'POST'])
def escolher():
    if request.method == 'POST':
        selected_id = request.form.get('exercicio_id')
        if selected_id and selected_id.isdigit():
            return redirect(url_for('mostrarExercicio', id=int(selected_id)))
    return render_template('selecionar_exercicio.html', exercicios=dataEx)



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
