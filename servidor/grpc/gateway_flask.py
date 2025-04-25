from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from google.protobuf import empty_pb2
from werkzeug.utils import secure_filename
from lxml import etree
import os
import grpc
import usuarios_pb2
import usuarios_pb2_grpc

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

GRPC_SERVER = 'localhost:50052'

UPLOAD_DIR = "/var/www/biblionline/servidor/dados"
XML_FILE = os.path.join(UPLOAD_DIR, "usuarios.xml")
XSD_FILE = os.path.join(UPLOAD_DIR, "usuarios.xsd")

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

# Rota para exportar usuários em XML
@app.route("/exportar/xml", methods=["GET"])
def exportar_usuarios_xml():
    xml_path = "/var/www/biblionline/servidor/dados/usuarios.xml"
    if not os.path.exists(xml_path):
        return jsonify({"erro": "Arquivo XML não encontrado."}), 404
    return send_file(xml_path, as_attachment=True)

# Rota para importar usuários em XML
@app.route("/importar/xml", methods=["POST"])
def importar_usuarios_xml():
    if 'arquivo' not in request.files:
        return jsonify({"erro": "Nenhum arquivo enviado."}), 400

    uploaded_file = request.files['arquivo']
    try:
        # Lê o XML enviado
        uploaded_tree = etree.parse(uploaded_file)
        uploaded_root = uploaded_tree.getroot()

        # Valida com o XSD
        schema = etree.XMLSchema(etree.parse(XSD_FILE))
        if not schema.validate(uploaded_tree):
            return jsonify({"erro": "XML inválido segundo o XSD."}), 400

        # Cria o stub gRPC, que é o cliente para comunicação com o servidor gRPC
        stub = get_stub()

        # Itera sobre os usuários no XML e envia para o servidor gRPC
        mensagens = []
        for usuario_el in uploaded_root.findall('usuario'):
            nome = usuario_el.findtext('nome')
            email = usuario_el.findtext('email')
            senha = usuario_el.findtext('senha')
            tipo = usuario_el.findtext('tipo')

            # Cria objeto protobuf Usuario
            usuario = usuarios_pb2.Usuario(
                nome=nome,
                email=email,
                senha=senha,
                tipo=tipo
            )

            # Cria a requisição de cadastro e envia para o servidor gRPC
            cadastro_request = usuarios_pb2.CadastroRequest(usuario=usuario)
            response = stub.CadastrarUsuario(cadastro_request)
            mensagens.append(response.mensagem)

        return jsonify({"mensagem": "Importação concluída.", "detalhes": mensagens})

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
