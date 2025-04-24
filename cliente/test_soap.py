import requests
from lxml import etree

# URL onde o SOAP está escutando
SOAP_URL = "http://localhost:8105/"

# Cabeçalhos para a requisição SOAP
HEADERS = {
    "Content-Type": "text/xml; charset=utf-8",
}

def buscar_livro(titulo: str):
    # Monta o envelope SOAP conforme sua implementação
    envelope = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:web="biblionline.soap">
  <soapenv:Header/>
  <soapenv:Body>
    <web:buscar_livro>
      <web:titulo>{titulo}</web:titulo>
    </web:buscar_livro>
  </soapenv:Body>
</soapenv:Envelope>"""

    # Envia a requisição
    resp = requests.post(SOAP_URL, data=envelope.encode('utf‑8'), headers=HEADERS)
    print(f"\nHTTP {resp.status_code}\n")
    print("=== Envelope de Resposta ===")
    print(resp.text)

    # Parseia a resposta para extrair somente o conteúdo de <buscar_livroResult>
    xml = etree.fromstring(resp.content)
    ns = {
        "soapenv": "http://schemas.xmlsoap.org/soap/envelope/",
        "web":      "biblionline.soap"
    }
    # Caminho até o elemento de resultado
    result_el = xml.find(
        ".//soapenv:Body//web:buscar_livroResponse//web:buscar_livroResult",
        namespaces=ns
    )
    if result_el is not None:
        print("\n>>> Resultado da busca:", result_el.text)
    else:
        print("\n>>> Não foi possível localizar o elemento de resultado na resposta.")

if __name__ == "__main__":
    livro = input("Título do livro para buscar: ").strip()
    buscar_livro(livro)
