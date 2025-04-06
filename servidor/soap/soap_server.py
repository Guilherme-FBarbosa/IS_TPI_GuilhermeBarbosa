from wsgiref.simple_server import make_server
from soap_app.service import application

if __name__ == '__main__':
	print("SOAP server online em http://localhost:8000")
	server = make_server('0.0.0.0', 8000, application)
	server.serve_forever()
