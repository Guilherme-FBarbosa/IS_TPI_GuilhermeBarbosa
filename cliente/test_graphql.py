import requests

url = "http://192.168.246.26:8003/graphql"
query = """
{
  hello
}
"""

response = requests.post(url, json={"query": query})
print("Resposta GraphQL:", response.json())