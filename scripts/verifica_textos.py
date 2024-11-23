import requests

# URL da consulta
url = "http://10.5.132.51:8081/janus/documentos/"
params = {"numero": "600268-39.2020.6.05.0007"}

# Cabeçalhos da consulta
headers = {"accept": "*/*"}

# Realizando a solicitação GET
response = requests.get(url, headers=headers, params=params)

# Verificando o status e exibindo a resposta
if response.status_code == 200:
    print("Consulta realizada com sucesso!")
    print("Resposta:", response.json())  # Supondo que a resposta seja JSON
else:
    print(f"Erro na consulta. Status: {response.status_code}")
    print("Detalhes:", response.text)
