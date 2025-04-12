// Função para testar a API REST
document.getElementById('restPing').addEventListener('click', function () {
    fetch('http://api.biblionline.local/ping')
      .then(response => response.text())
      .then(data => {
        document.getElementById('restResult').textContent = data;
      })
      .catch(error => {
        document.getElementById('restResult').textContent = error;
      });
  });
  
  // Função para testar a API GraphQL
  document.getElementById('graphqlHello').addEventListener('click', function () {
    const url = 'http://192.168.246.26:8003/graphql';
    const query = JSON.stringify({
      query: "{ hello }"
    });
    
    fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: query,
    })
      .then(response => response.json())
      .then(data => {
        document.getElementById('graphqlResult').textContent = JSON.stringify(data);
      })
      .catch(error => {
        document.getElementById('graphqlResult').textContent = error;
      });
  });
  
  // Função para testar a API SOAP
  document.getElementById('soapCall').addEventListener('click', function () {
    // Exemplo de mensagem SOAP para operação buscar_livro
    const soapMessage = `
      <?xml version="1.0" encoding="UTF-8"?>
      <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:web="biblionline.soap">
         <soapenv:Header/>
         <soapenv:Body>
            <web:buscar_livro>
               <web:titulo>O Senhor dos Anéis</web:titulo>
            </web:buscar_livro>
         </soapenv:Body>
      </soapenv:Envelope>`;
    
    fetch('http://192.168.246.26:8000/', {
      method: 'POST',
      headers: { 'Content-Type': 'text/xml' },
      body: soapMessage,
    })
      .then(response => response.text())
      .then(data => {
        document.getElementById('soapResult').textContent = data;
      })
      .catch(error => {
        document.getElementById('soapResult').textContent = error;
      });
  });
  