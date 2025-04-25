from flask import Flask, request, Response, abort, send_file
from flask_cors import CORS
import json
import os
from jsonschema import validate, ValidationError
from jsonpath_ng import parse

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Caminho para os dados persistentes
DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'dados', 'livros.json'))

# Definição do JSON Schema para um livro
LIVRO_SCHEMA = {
    "type": "object",
    "properties": {
        "titulo": {"type": "string"},
        "autor": {"type": "string"},
        "ano": {"type": "integer"}
    },
    "required": ["titulo", "autor", "ano"],
    "additionalProperties": False
}

# Funções de leitura e gravação de dados

def ler_livros():
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def escrever_livros(livros):
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(livros, f, indent=4, ensure_ascii=False)

# Rotas da API:

# Rota para listar/buscar todos os livros
@app.route('/livros', methods=['GET'])
def listar_livros():
    livros = ler_livros()
    query = request.args.get('query')
    if query:
        try:
            expr = parse(query)
            matches = [match.value for match in expr.find(livros)]
            result = matches
        except Exception as e:
            abort(400, f"Expressão JSONPath inválida: {str(e)}")
    else:
        result = livros
    return Response(json.dumps(result, ensure_ascii=False), mimetype='application/json')

# Rota para buscar um só livro específico
@app.route('/livros/<int:id>', methods=['GET'])
def obter_livro(id):
    livros = ler_livros()
    livro = next((l for l in livros if l.get('id') == id), None)
    if livro:
        return Response(json.dumps(livro, ensure_ascii=False), mimetype='application/json')
    return Response(json.dumps({'erro': 'Livro não encontrado'}), status=404, mimetype='application/json')

# Rota para adicionar um novo livro ao json de livros
@app.route('/livros', methods=['POST'])
def adicionar_livro():
    try:
        novo = request.get_json(force=True)
        validate(instance=novo, schema=LIVRO_SCHEMA)
    except ValidationError as e:
        abort(400, f"Dados inválidos segundo JSON Schema: {e.message}")
    except Exception:
        abort(400, 'Requisição inválida: JSON esperado')

    livros = ler_livros()
    novo['id'] = max((l.get('id', 0) for l in livros), default=0) + 1
    livros.append(novo)
    escrever_livros(livros)
    return Response(json.dumps(novo, ensure_ascii=False), status=201, mimetype='application/json')

# Rota para alterar um livro existente
@app.route('/livros/<int:id>', methods=['PUT'])
def editar_livro(id):
    try:
        dados = request.get_json(force=True)
        validate(instance=dados, schema=LIVRO_SCHEMA)
    except ValidationError as e:
        abort(400, f"Dados inválidos segundo JSON Schema: {e.message}")
    except Exception:
        abort(400, 'Requisição inválida: JSON esperado')

    livros = ler_livros()
    for livro in livros:
        if livro.get('id') == id:
            livro.update(dados)
            escrever_livros(livros)
            return Response(json.dumps(livro, ensure_ascii=False), mimetype='application/json')
    return Response(json.dumps({'erro': 'Livro não encontrado'}), status=404, mimetype='application/json')

# Rota para remover um livro existente
@app.route('/livros/<int:id>', methods=['DELETE'])
def remover_livro(id):
    livros = ler_livros()
    orig = len(livros)
    livros = [l for l in livros if l.get('id') != id]
    if len(livros) == orig:
        return Response(json.dumps({'erro': 'Livro não encontrado'}), status=404, mimetype='application/json')
    escrever_livros(livros)
    return Response('livro excluído com sucesso!', status=204, mimetype='text/plain')

# Rota de ping para verificar se o servidor REST está funcionando
@app.route('/ping')
def ping():
    return Response('pong - o REST está funcionando!', mimetype='text/plain')

# Rota para exportar livros em JSON
@app.route("/exportar/json", methods=["GET"])
def exportar_json():
    return send_file(DATA_PATH, as_attachment=True)

# Rota para importar livros em JSON
@app.route("/importar/json", methods=["POST"])
def importar_json():
    try:
        novos_livros = request.get_json(force=True)

        if not isinstance(novos_livros, list):
            abort(400, "Formato inválido: esperado um array de livros")

        for livro in novos_livros:
            validate(instance=livro, schema=LIVRO_SCHEMA)

        livros_existentes = ler_livros()
        ultimo_id = max((l.get('id', 0) for l in livros_existentes), default=0)

        # Atribui novos IDs aos livros importados
        for i, livro in enumerate(novos_livros, start=1):
            livro['id'] = ultimo_id + i

        livros_existentes.extend(novos_livros)
        escrever_livros(livros_existentes)

        return Response(json.dumps({"mensagem": "Livros importados com sucesso!"}, ensure_ascii=False),
                        mimetype='application/json')

    except ValidationError as e:
        abort(400, f"Erro de validação: {e.message}")

    except Exception as e:
        abort(400, f"Erro ao importar dados: {str(e)}")

