import requests
import json
import jsonpath_ng
from unidecode import unidecode
from jsonpath_ng import parse
from spyne.server.wsgi import WsgiApplication
from spyne import Application, rpc, ServiceBase, Unicode
from spyne.protocol.soap import Soap11
from wsgiref.simple_server import make_server

def remover_acento(texto):
	return unidecode(texto)

class BibliotecaService(ServiceBase):

	@rpc(Unicode, _returns=Unicode)
	def buscar_livro(ctx, titulo):
		print("Buscando livro via SOAP:", titulo)

		try:
			# Consulta a API REST
			response = requests.get("http://api.biblionline.local/livros")
			print("Status da resposta REST:", response.status_code)
			print("Resposta REST:", response.text)
			response.raise_for_status()
			livros = response.json()
			print("Livros carregados:", livros)

			titulo_normalizado = remover_acento(titulo.strip().lower())

			encontrado = False
			for livro in livros:
				titulo_livro = remover_acento(livro.get("titulo", "").strip().lower())
				print(f"Comparando: '{titulo_normalizado}' com '{titulo_livro}'")
				if titulo_livro == titulo_normalizado:
					encontrado = True
					break

			if encontrado:
				return "Livro disponível"
			else:
				return "Livro não encontrado"

		except Exception as e:
			print("Erro ao consultar o REST:", str(e))
			return "Erro ao consultar o sistema de livros."

application = Application([BibliotecaService], 'biblionline.soap',
			in_protocol=Soap11(), out_protocol=Soap11())

def cors_middleware(app):
	def new_app(environ, start_response):
		def new_start_response(status, headers, exc_info=None):
			headers.append(('Access-Control-Allow-Origin', '*'))
			headers.append(('Access-Control-Allow-Methods', 'POST, GET, OPTIONS'))
			headers.append(('Access-Control-Allow-Headers', '*'))
			return start_response(status, headers, exc_info)
		if environ['REQUEST_METHOD'] == 'OPTIONS':
			start_response('200 OK', [
				('Content-Type', 'text/plain'),
				('Access-Control-Allow-Origin', '*'),
				('Access-Control-Allow-Methods', 'POST, GET, OPTIONS'),
				('Access-Control-Allow-Headers', '*'),
				('Content-Length', '0')
			])
			return [b'']
		return app(environ, new_start_response)
	return new_app

if __name__ == '__main__':
	print("SOAP server online em http://localhost:8005")
	server = make_server('0.0.0.0', 8005, cors_middleware(WsgiApplication(application)))
	server.serve_forever()
