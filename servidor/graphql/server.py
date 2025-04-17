import json
import os
import strawberry
from strawberry.fastapi import GraphQLRouter
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from jsonschema import validate, ValidationError
from jsonpath_ng import parse

DADOS_PATH = "dados/livros.json"
SCHEMA_PATH = "schemas/livro_schema.json"

if not os.path.exists(DADOS_PATH):
    with open(DADOS_PATH, "w", encoding="utf-8") as f:
        json.dump([], f, indent=2)

with open(SCHEMA_PATH, encoding="utf-8") as f:
    LIVRO_SCHEMA = json.load(f)

def carregar_livros():
    with open(DADOS_PATH, encoding="utf-8") as f:
        return json.load(f)

def salvar_livros(livros):
    with open(DADOS_PATH, "w", encoding="utf-8") as f:
        json.dump(livros, f, indent=2, ensure_ascii=False)

@strawberry.type
class Livro:
	id: int
	titulo: str
	autor: str
	ano: int

@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello from GraphQL (Strawberry)!"

    @strawberry.field
    def livros(
        self,
        titulo: Optional[str] = None,
        autor: Optional[str] = None,
        ano: Optional[int] = None
    ) -> List[Livro]:
        livros = carregar_livros()
        if titulo:
            tl = titulo.strip().lower()
            livros = [l for l in livros if tl in l["titulo"].lower()]
        if autor:
            au = autor.strip().lower()
            livros = [l for l in livros if au in l["autor"].lower()]
        if ano is not None:
            livros = [l for l in livros if l["ano"] == ano]
        return [Livro(**l) for l in livros]

    @strawberry.field
    def buscar_por_jsonpath(self, caminho: str) -> List[Livro]:
        livros = carregar_livros()
        jsonpath_expr = parse(caminho)
        results = [match.value for match in jsonpath_expr.find(livros)]
        return [Livro(**livro) for livro in results if isinstance(livro, dict)]

@strawberry.type
class Mutation:
    @strawberry.mutation
    def adicionar_livro(self, id: int, titulo: str, autor: str, ano: int) -> str:
        novo_livro = {"id": id, "titulo": titulo, "autor": autor, "ano": ano}
        try:
            validate(novo_livro, LIVRO_SCHEMA)
        except ValidationError as e:
            return f"Erro de validação: {e.message}"

        livros = carregar_livros()
        if any(l["id"] == id for l in livros):
            return "ID já existe"
        livros.append(novo_livro)
        salvar_livros(livros)
        return "Livro adicionado com sucesso"

schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)

app = FastAPI()
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)
app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
