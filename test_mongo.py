from pymongo import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://Sora:Q!W@E#R$12qwaszx@cluster0.lqogubf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Conexão bem sucedida!")
except Exception as e:
    print("Erro:", e)
