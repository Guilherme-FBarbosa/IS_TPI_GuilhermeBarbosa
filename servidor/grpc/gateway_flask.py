from flask import Flask, request, jsonify
from flask_cors import CORS
from google.protobuf import empty_pb2
import grpc
import usuarios_pb2
import usuarios_pb2_grpc

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

GRPC_SERVER = 'localhost:50052'

def get_stub():
    # Cria um canal e retorna o stub para a comunicação gRPC
    channel = grpc.insecure_channel(GRPC_SERVER)
    stub = usuarios_pb2_grpc.GestaoUsuariosStub(channel)
    return stub

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"erro": "Dados inválidos"}), 400

    usuario = usuarios_pb2.Usuario(
        nome = data.get("nome"),
        email = data.get("email"),
        senha = data.get("senha"),
        tipo = data.get("tipo", "cliente")  # fica por padrão "cliente" se não for especificado
    )

    try:
        stub = get_stub()
        # Cria a requisição de cadastro
        cadastro_request = usuarios_pb2.CadastroRequest(usuario=usuario)
        response = stub.CadastrarUsuario(cadastro_request)
        return jsonify({"mensagem": response.mensagem})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"erro": "Dados inválidos"}), 400

    try:
        stub = get_stub()
        login_request = usuarios_pb2.LoginRequest(
            email = data.get("email"),
            senha = data.get("senha")
        )
        response = stub.Login(login_request)
        return jsonify({
            "sucesso": response.sucesso,
            "mensagem": response.mensagem
        })
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/usuarios", methods=["GET"])
def listar_usuarios():
    try:
        stub = get_stub()
        resp = stub.ListarUsuarios(empty_pb2.Empty())
        # transforma em lista de dicts
        usuarios = [
            {
              "id": u.id,
              "nome": u.nome,
              "email": u.email,
              "senha": u.senha,
              "tipo": u.tipo
            }
            for u in resp.usuarios
        ]
        return jsonify(usuarios)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
