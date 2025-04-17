from concurrent import futures
import grpc
import os
from lxml import etree
import json
from jsonschema import validate as json_validate, ValidationError
import usuarios_pb2
import usuarios_pb2_grpc
from google.protobuf import empty_pb2

XML_FILE = "dados/usuarios.xml"
XSD_FILE = "dados/usuarios.xsd"
JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "nome": {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "senha": {"type": "string"},
        "tipo": {"type": "string", "enum": ["cliente", "bibliotecario"]}
    },
    "required": ["nome", "email", "senha", "tipo"],
    "additionalProperties": False
}

def init_xsd():
    if not os.path.exists(XSD_FILE):
        xsd_content = '''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">

  <xs:element name="usuarios">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="usuario" maxOccurs="unbounded" minOccurs="0">
          <xs:complexType>
            <xs:sequence>
              <xs:element name="id" type="xs:int"/>
              <xs:element name="nome" type="xs:string"/>
              <xs:element name="email" type="xs:string"/>
              <xs:element name="senha" type="xs:string"/>
              <xs:element name="tipo" type="xs:string"/>
            </xs:sequence>
          </xs:complexType>
        </xs:element>
      </xs:sequence>
    </xs:complexType>
  </xs:element>

</xs:schema>
'''
        with open(XSD_FILE, "w", encoding="utf-8") as f:
            f.write(xsd_content)

def init_xml():
    if not os.path.exists(XML_FILE):
        root = etree.Element('usuarios')
        tree = etree.ElementTree(root)
        tree.write(XML_FILE, pretty_print=True, xml_declaration=True, encoding='utf-8')

def validar_xml():
    xml_doc = etree.parse(XML_FILE)
    xmlschema_doc = etree.parse(XSD_FILE)
    xmlschema = etree.XMLSchema(xmlschema_doc)
    if not xmlschema.validate(xml_doc):
        raise ValueError("XML não é válido conforme o XSD.")

def adicionar_usuario(nome, email, senha, tipo):
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(XML_FILE, parser)
    root = tree.getroot()

    novo_id = str(len(root.findall('usuario')) + 1)

    usuario_el = etree.SubElement(root, 'usuario')
    etree.SubElement(usuario_el, 'id').text = novo_id
    etree.SubElement(usuario_el, 'nome').text = nome
    etree.SubElement(usuario_el, 'email').text = email
    etree.SubElement(usuario_el, 'senha').text = senha
    etree.SubElement(usuario_el, 'tipo').text = tipo

    tree.write(XML_FILE, pretty_print=True, xml_declaration=True,  encoding='utf-8')
    validar_xml()

def verificar_login(email, senha):
    tree = etree.parse(XML_FILE)
    root = tree.getroot()

    for usuario in root.findall('usuario'):
        if (usuario.find('email').text == email and
            usuario.find('senha').text == senha):
            return True
    return False

def json_para_xml(json_data):
    usuario_el = etree.Element('usuario')
    for key, value in json_data.items():
        etree.SubElement(usuario_el, key).text = str(value)
    return etree.tostring(usuario_el, pretty_print=True, encoding='unicode')

def xml_para_json(xml_string):
    root = etree.fromstring(xml_string)
    return {elem.tag: elem.text for elem in root}

class GestaoUsuariosService(usuarios_pb2_grpc.GestaoUsuariosServicer):
    def CadastrarUsuario(self, request, context):
        usuario = request.usuario
        json_data = {
            "nome": usuario.nome,
            "email": usuario.email,
            "senha": usuario.senha,
            "tipo": usuario.tipo
        }
        try:
            json_validate(instance=json_data, schema=JSON_SCHEMA)
            adicionar_usuario(**json_data)
            return usuarios_pb2.CadastroResponse(mensagem="Usuário cadastrado com sucesso.")
        except ValidationError as e:
            return usuarios_pb2.CadastroResponse(mensagem=f"Erro de validação JSON: {e.message}")
        except Exception as e:
            return usuarios_pb2.CadastroResponse(mensagem=f"Erro: {str(e)}")

    def Login(self, request, context):
        sucesso = verificar_login(request.email, request.senha)
        if sucesso:
            return usuarios_pb2.LoginResponse(sucesso=True, mensagem="Login realizado com sucesso.")
        else:
            return usuarios_pb2.LoginResponse(sucesso=False, mensagem="Email ou senha incorretos.")

    def ListarUsuarios(self, request: empty_pb2.Empty, context):
        # Lê o XML e converte para lista de dicts
        tree = etree.parse(XML_FILE)
        root = tree.getroot()
        usuarios = []
        for u in root.findall('usuario'):
            usuarios.append({
                'id':    int(u.findtext('id')),
                'nome':  u.findtext('nome'),
                'email': u.findtext('email'),
                'senha': u.findtext('senha'),
                'tipo':  u.findtext('tipo'),
            })
        # Empacota na mensagem de saída
        return usuarios_pb2.ListarUsuariosResponse(
            usuarios=[usuarios_pb2.Usuario(**u) for u in usuarios]
        )

def serve():
    init_xml()
    init_xsd()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    usuarios_pb2_grpc.add_GestaoUsuariosServicer_to_server(GestaoUsuariosService(), server)
    server.add_insecure_port('[::]:50052')
    print("gRPC de gestão de utilizadores rodando na porta 50052...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()

