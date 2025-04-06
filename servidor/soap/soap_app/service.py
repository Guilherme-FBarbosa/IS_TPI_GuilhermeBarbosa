from spyne import Application, rpc, ServiceBase, Integer, Unicode
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication

class BibliotecaService(ServiceBase):

	@rpc(Unicode, _returns=Unicode)
	def buscar_livro(ctx, titulo):
		# Exemplo estático: em um projeto real, aqui faria busca na base de dados
		if titulo.lower() == "o senhor dos anéis":
			return "Livro disponível"
		return "Livro não encontrado"

	@rpc(Integer, Integer, _returns=Integer)
	def somar(ctx, a, b):
		return a + b

# Criando a aplicação SOAP
soap_app = Application(
	[BibliotecaService],
	tns='biblionline.soap',
	in_protocol=Soap11(validator='lxml'),
	out_protocol=Soap11()
)

# WSGI application para Apache ou standalone
application = WsgiApplication(soap_app)
