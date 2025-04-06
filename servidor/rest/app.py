from flask import Flask
app = Flask(__name__)
@app.route('/')
def home():
	return "Esta é a API executando no Apache!"
if __name__=='__main__':
	app.run()

@app.route('/ping')
def ping():
	return "pong", 200
