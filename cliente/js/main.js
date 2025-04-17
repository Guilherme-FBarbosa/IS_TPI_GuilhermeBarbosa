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
  const url = 'http://biblionline.local/graphql';
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
// Função consultar um livro com parâmetros pelo GraphQL
// ===========================================================
document.getElementById('graphqlSearch').addEventListener('click', function () {
  const title = document.getElementById('graphql-title').value.trim();
  const author = document.getElementById('graphql-author').value.trim();
  const year   = document.getElementById('graphql-year').value.trim();

  let args = [];
  if (title)  args.push(`titulo: "${title}"`);
  if (author) args.push(`autor:  "${author}"`);
  if (year)   args.push(`ano: ${parseInt(year, 10)}`);

  let argsStr = args.length ? `(${args.join(", ")})` : "";
  const query = `{ livros${argsStr} { titulo, autor, ano } }`;

  fetch('/graphql', { 
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query })
  })
    .then(r => r.json())
    .then(payload => {
      const livros = payload.data?.livros || [];
      const pre = document.getElementById('graphqlResult');
      if (livros.length) {
        pre.textContent = livros.map(l => `${l.titulo} — ${l.autor} (${l.ano})`).join("\n");
      } else {
        pre.textContent = "Nenhum livro encontrado.";
      }
    })
    .catch(err => {
      document.getElementById('graphqlResult').textContent = "Erro: " + err.message;
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

// ===========================================================
// Função registrar um novo usuário com o gRPC
// ===========================================================
document.getElementById('btnRegistrar').addEventListener('click', function() {
  const nome = document.getElementById('reg-nome').value.trim();
  const email = document.getElementById('reg-email').value.trim();
  const senha = document.getElementById('reg-senha').value.trim();
  const tipo = document.getElementById('reg-tipo').value;

  const payload = { nome, email, senha, tipo };

  fetch('http://biblionline.local/grpc/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
    .then(response => response.json())
    .then(data => {
      document.getElementById('resultadoRegistro').textContent = JSON.stringify(data);
    })
    .catch(error => {
      document.getElementById('resultadoRegistro').textContent = error;
    });
});

// ===========================================================
// Função para fazer login com o gRPC
// ===========================================================
document.getElementById('btnLogin').addEventListener('click', function() {
  const email = document.getElementById('login-email').value.trim();
  const senha = document.getElementById('login-senha').value.trim();

  const payload = { email, senha };

  fetch('http://biblionline.local/grpc/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
    .then(response => response.json())
    .then(data => {
      document.getElementById('resultadoLogin').textContent = JSON.stringify(data);
    })
    .catch(error => {
      document.getElementById('resultadoLogin').textContent = error;
    });
});

// ===========================================================
// Função para listar os usuários com o gRPC
// ===========================================================
function listarUsuarios() {
  fetch('http://biblionline.local/usuarios')
    .then(res => res.json())
    .then(data => {
      const div = document.getElementById('usuariosResult');
      div.textContent = JSON.stringify(data, null, 2);
    })
    .catch(err => {
      document.getElementById('usuariosResult').textContent = err;
    });
}

// Vincular a um botão no HTML
document.getElementById('usuariosBtn').addEventListener('click', listarUsuarios);