# 📚 Biblionline - Trabalho Prático Individual de Integração de Sistemas

## 🧩 Descrição Geral

O projeto consiste em um sistema de biblioteca online chamado **Biblionline**, que demonstra a integração de múltiplos serviços web utilizando diferentes arquiteturas e tecnologias: REST, SOAP, GraphQL e gRPC.
O objetivo é criar um ambiente cliente-servidor onde os utilizadores possam gerenciar (inserir, visualizar, editar e excluir) livros e, adicionalmente, consultar a disponibilidade dos livros via um serviço SOAP que interage com a API REST — demais funcionalidades serão implementadas posteriormente. 
Conta também com um site que serve como uma interface central para interagir com todos esses serviços.

## 🛠 Tecnologias Utilizadas

- **Frontend**: HTML5, CSS3 e JavaScript puro
- **Backend REST**: Flask + JSON (persistência em ficheiro)
- **Backend SOAP**: Spyne + integração com REST via JSONPath
- **Backend GraphQL**: FastAPI + Strawberry
- **gRPC**: Em desenvolvimento
- **Apache2**: Para servir REST e site
- **Python 3.12**
- **Servidor Ubuntu (via SSH)**

---

## 🔗 Funcionalidades por Serviço

### ✅ API REST
- Endpoint `/ping` para teste básico de conectividade;
- Endpoints CRUD completos em `/livros` que permite listar, buscar, criar, editar e remover livros;
- Armazenamento de dados em JSON;
- API acessível em `http://api.biblionline.local/livros`.

### ✅ API SOAP
- Serviço de busca de livros: `<buscar_livro>`
- Consulta se o livro está disponível, integrando com a API REST (faz uma chamada à ela e verifica se o livro existe no arquivo `livros.json`);
- Normalização do texto (sem acentos, case-insensitive);
- Suporte a CORS.

### ✅ API GraphQL
- Estrutura inicial desenvolvida com FastAPI + Strawberry para permitir consultas flexíveis (exemplo: query `{ hello }`).

### ⚙️ gRPC
- A estrutura inicial está criada, mais testes e definição de métodos ainda serão feitas;
- No momento, há um teste do serviço gRPC definido no arquivo `helloworld.proto`.

---

## 💻 Funcionalidades no Site/Front-end (Cliente)

- Interface construída em HTML, CSS e JavaScript para testar a integração com os serviços, que permite:
    - Testar a API REST (/ping) e exibir os resultados;
    - Realizar operações CRUD de livros via API REST;
    - Consultar a disponibilidade de livros através do serviço SOAP (input dinâmico);
    - Testar a API GraphQL;
    - (Por enquanto, o gRPC é testado por meio de scripts de cliente).
- Possui um ícone de aba personalizado definido em `biblionline_icon.ico`.

---

## Instruções de Execução

### API REST
1. Acesse o diretório do REST:
    ```bash
    cd /var/www/biblionline/servidor/rest
    ```
2. Ative o ambiente virtual:
    ```bash
    source venv/bin/activate
    ```
3. O serviço está integrado ao Apache (VirtualHost configurado para `api.biblionline.local`). Certifique-se de que o Apache esteja rodando.  
4. Para testes isolados, você pode rodar:
    ```bash
    python app.py
    ```

### API SOAP
1. Acesse o diretório do SOAP:
    ```bash
    cd /var/www/biblionline/servidor/soap
    ```
2. Ative o ambiente virtual (Python 3.10):
    ```bash
    source venv310/bin/activate
    ```
3. Reinicie o serviço:
    ```bash
    python soap_server.py
    ```
4. O serviço SOAP está disponível na porta 8005. As chamadas SOAP fazem consulta à API REST para verificar a disponibilidade do livro.

### Frontend (Cliente)
1. Acesse o diretório do cliente:
    ```bash
    cd /var/www/biblionline/cliente
    ```
2. Para testes, você pode iniciar um servidor HTTP simples:
    ```bash
    python3 -m http.server 8085
    ```
3. Utilizando a VPN da escola ou ligado à rede eduroam, acesse no navegador (ex.: `http://192.168.246.26:8085` ou configure o VirtualHost do Apache para servir essa pasta).

### Observação: defini meus serviços como fazendo parte do systemd, assim, eles ficam rodando direto, sem a necessidade de ter que ativá-los toda vez que forem ser usados. Caso o servidor reinicie, eles serão iniciados automaticamente assim como o Apache.
### Também configurei meu VirtualHost do Apache para servir ao diretório onde fiz o site, assim, ao buscar `http://biblionline.local/` no navegador da máquina física, ele já vai direto para a interface desenvolvida. Não havendo assim a necessidade de executar o comando `python3 -m http.server 8085` no diretório do cliente toda vez que for querer utilizar o site.

---

## 👨‍💻 Autor
- **Guilherme Barbosa**, Nº 230000002 
- `Email:` 230000002@esg.ipsantarem.pt 
- `Curso:` Licenciatura em Informática - 2º Ano  
- Escola Superior de Gestão e Tecnologia de Santarém (ESGTS)
