// ===========================================================
// Função para testar a API REST (/ping)
// ===========================================================
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

// ===========================================================
// Funções para CRUD de Livros via API REST
// ===========================================================

const restBaseUrl = "http://api.biblionline.local";

// Carregar a lista de livros
function carregarLivros() {
  fetch(`${restBaseUrl}/livros`)
    .then(response => response.json())
    .then(data => {
      const lista = document.getElementById('listaLivros');
      lista.innerHTML = "";
      data.forEach(livro => {
        const li = document.createElement('li');
        li.innerHTML = `
          <strong>${livro.titulo}</strong> - ${livro.autor} (${livro.ano})
          <button onclick="editarLivro(${livro.id})">Editar</button>
          <button onclick="removerLivro(${livro.id})">Remover</button>
        `;
        lista.appendChild(li);
      });
    })
    .catch(error => console.error("Erro ao carregar livros:", error));
}

// Adicionar ou atualizar um livro
document.getElementById('livroForm').addEventListener('submit', function (e) {
  e.preventDefault();

  const id = document.getElementById('livroId').value;
  const titulo = document.getElementById('titulo').value;
  const autor = document.getElementById('autor').value;
  const ano = document.getElementById('ano').value;

  const livro = { titulo, autor, ano: parseInt(ano) };

  if (id) {
    // Atualizar livro existente
    fetch(`${restBaseUrl}/livros/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(livro)
    })
      .then(response => response.json())
      .then(data => {
        limparForm();
        carregarLivros();
      })
      .catch(error => console.error("Erro ao editar livro:", error));
  } else {
    // Adicionar novo livro
    fetch(`${restBaseUrl}/livros`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(livro)
    })
      .then(response => response.json())
      .then(data => {
        limparForm();
        carregarLivros();
      })
      .catch(error => console.error("Erro ao adicionar livro:", error));
  }
});

// Função para preencher o formulário ao editar um livro
function editarLivro(id) {
  fetch(`${restBaseUrl}/livros/${id}`)
    .then(response => response.json())
    .then(livro => {
      document.getElementById('livroId').value = livro.id;
      document.getElementById('titulo').value = livro.titulo;
      document.getElementById('autor').value = livro.autor;
      document.getElementById('ano').value = livro.ano;
    })
    .catch(error => console.error("Erro ao buscar livro para edição:", error));
}

// Função para remover um livro
function removerLivro(id) {
  if (confirm("Tem certeza de que deseja remover este livro?")) {
    fetch(`${restBaseUrl}/livros/${id}`, { method: 'DELETE' })
      .then(() => carregarLivros())
      .catch(error => console.error("Erro ao remover livro:", error));
  }
}

function limparForm() {
  document.getElementById('livroId').value = "";
  document.getElementById('titulo').value = "";
  document.getElementById('autor').value = "";
  document.getElementById('ano').value = "";
}

// Carregar livros ao abrir a página
carregarLivros();

// ===========================================================
// Função para testar a API GraphQL
// ===========================================================
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

// ===========================================================
// Função para testar a API SOAP com input do usuário
// ===========================================================
document.getElementById('soapCall').addEventListener('click', function () {
  // Obtem o título digitado pelo usuário
  const bookTitle = document.getElementById('soap-book-title').value.trim();
  if (!bookTitle) {
    alert('Por favor, digite o título de livro.');
    return;
  }

  const soapMessage = `
  <?xml version="1.0" encoding="UTF-8"?>
  <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:web="biblionline.soap">
    <soapenv:Header/>
    <soapenv:Body>
      <web:buscar_livro>
        <web:titulo>${bookTitle}</web:titulo>
      </web:buscar_livro>
    </soapenv:Body>
  </soapenv:Envelope>
  `.trim();

  fetch('http://192.168.246.26:8005/', {
    method: 'POST',
    headers: { 'Content-Type': 'text/xml' },
    body: soapMessage,
  })
    .then(response => response.text())
    .then(data => {
      const parser = new DOMParser();
      const xmlDoc = parser.parseFromString(data, 'text/xml');
      let result = "Não foi possível extrair o resultado";
      if (xmlDoc.getElementsByTagName("tns:buscar_livroResult").length > 0) {
        result = xmlDoc.getElementsByTagName("tns:buscar_livroResult")[0].textContent;
      } else if (xmlDoc.getElementsByTagName("buscar_livroResult").length > 0) {
        result = xmlDoc.getElementsByTagName("buscar_livroResult")[0].textContent;
      }
      document.getElementById('soapResult').textContent = result;
    })
    .catch(error => {
      document.getElementById('soapResult').textContent = error;
    });
});
