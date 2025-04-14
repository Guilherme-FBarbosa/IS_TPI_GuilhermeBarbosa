from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'livros.json')

def ler_livros():
	with open(DATA_PATH, 'r', encoding='utf-8') as f:
		return json.load(f)

def escrever_livros(livros):
	with open(DATA_PATH, 'w', encoding='utf-8') as f:
		json.dump(livros, f, indent=4, ensure_ascii=False)

@app.route("/livros", methods=["GET"])
def listar_livros():
	return jsonify(ler_livros())

@app.route("/livros/<int:id>", methods=["GET"])
def obter_livro(id):
	livros = ler_livros()
	livro = next((livro for livro in livros if livro["id"] == id), None)
	return jsonify(livro) if livro else ('Livro não encontrado', 404)

@app.route("/livros", methods=["POST"])
def adicionar_livro():
	livros = ler_livros()
	novo = request.json
	novo["id"] = (max(l["id"] for l in livros) + 1) if livros else 1
	livros.append(novo)
	escrever_livros(livros)
	return jsonify(novo), 201

@app.route("/livros/<int:id>", methods=["PUT"])
def editar_livro(id):
	livros = ler_livros()
	dados = request.json
	for livro in livros:
		if livro["id"] == id:
			livro.update(dados)
			escrever_livros(livros)
			return jsonify(livro)
	return ('Livro não encontrado', 404)

@app.route("/livros/<int:id>", methods=["DELETE"])
def remover_livro(id):
	livros = ler_livros()
	livros_novos = [livro for livro in livros if livro["id"] != id]
	if len(livros) == len(livros_novos):
		return ('Livro não encontrado', 404)
	escrever_livros(livros_novos)
	return ('', 204)

@app.route('/ping')
def ping():
	return "pong", 200
