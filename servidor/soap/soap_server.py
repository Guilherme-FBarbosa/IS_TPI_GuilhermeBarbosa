import requests
import logging
from spyne import Application, rpc, ServiceBase, Unicode
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from wsgiref.simple_server import make_server
from unidecode import unidecode
from lxml import etree

logging.basicConfig(
	level=logging.INFO,
	format='[%(asctime)s] %(levelname)s - %(message)s',
)

def remover_acento(texto):
	return unidecode(texto)

# Validação usando XSD
XSD_SCHEMA_PATH = "/var/www/biblionline/servidor/soap/livro.xsd"

def validar_xml(xml_str):
    try:
        schema_doc = etree.parse(XSD_SCHEMA_PATH)
        schema = etree.XMLSchema(schema_doc)
        doc = etree.fromstring(xml_str.encode('utf-8'))
        schema.assertValid(doc)
        return True, ""
    except Exception as e:
        return False, str(e)

class BibliotecaService(ServiceBase):

    @rpc(Unicode, _returns=Unicode)
    def buscar_livro(ctx, titulo):
        logging.info(f"Buscando livro via SOAP: {titulo}")

        try:
            response = requests.get("http://api.biblionline.local/livros")
            response.raise_for_status()
            livros = response.json()

            # Constrói um XML temporário baseado na resposta JSON
            root = etree.Element("livros")
            for livro in livros:
                el = etree.SubElement(root, "livro")
                etree.SubElement(el, "id").text = str(livro.get("id", ""))
                etree.SubElement(el, "titulo").text = livro.get("titulo", "")
                etree.SubElement(el, "autor").text = livro.get("autor", "")
                etree.SubElement(el, "ano").text = str(livro.get("ano", ""))

            xml_str = etree.tostring(root, pretty_print=True, encoding='utf-8').decode('utf-8')
            is_valid, error_msg = validar_xml(xml_str)
            if not is_valid:
                logging.error(f"XML inválido: {error_msg}")
                return "Erro de validação dos dados dos livros."

            titulo_normalizado = remover_acento(titulo.strip().lower())
            encontrado = False
            for livro in livros:
                titulo_livro = remover_acento(livro.get("titulo", "").strip().lower())
                logging.info(f"Comparando: '{titulo_normalizado}' com '{titulo_livro}'")
                if titulo_livro == titulo_normalizado:
                    encontrado = True
                    break

            return "Livro disponível" if encontrado else "Livro não encontrado"

        except Exception as e:
            logging.error(f"Erro ao consultar REST: {str(e)}")
            return "Erro ao consultar o sistema de livros."

# Aplicação SOAP
application = Application([
    BibliotecaService
], tns='biblionline.soap',
   in_protocol=Soap11(validator='lxml'),
   out_protocol=Soap11()
)

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
	print("SOAP server online em http://localhost:8105")
	server = make_server('0.0.0.0', 8105, cors_middleware(WsgiApplication(application)))
	server.serve_forever()
