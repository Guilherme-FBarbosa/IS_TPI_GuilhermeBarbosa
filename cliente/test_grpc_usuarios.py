import sys
sys.path.append('/var/www/biblionline/servidor/grpc')

import grpc
import usuarios_pb2
import usuarios_pb2_grpc

def run():
    channel = grpc.insecure_channel('192.168.246.26:50054')
    stub = usuarios_pb2_grpc.GestaoUsuariosStub(channel)

    # Teste de cadastro
    novo = usuarios_pb2.Usuario(nome="Felipe Madeira", email="filipe.madeira@esg.ipsantarem.pt", senha="1234", tipo="bibliotecario")
    cadastro_response = stub.CadastrarUsuario(usuarios_pb2.CadastroRequest(usuario=novo))
    print("Cadastro:", cadastro_response.mensagem)

    # Teste de login
    login_response = stub.Login(usuarios_pb2.LoginRequest(email="filipe.madeira@esg.ipsantarem.pt", senha="1234"))
    print("Login:", login_response.mensagem, "Sucesso:", login_response.sucesso)

if __name__ == '__main__':
    run()
