import urllib3
import requests

# Desativa os avisos de SSL inseguro no terminal
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 1. Suas informações da Z-API
INSTANCE_ID = "3F6BF878939291639BF64AA8B0DE2FDC"
TOKEN = "7FA1FEB1FB5BF16E30268A66"
CLIENT_TOKEN = "Fb30c72ce35354f678a9bf65c8bd07b91S"

# 2. Endpoint correto para BUSCAR CHATS/GRUPOS
url = f"https://api.z-api.io/instances/{INSTANCE_ID}/token/{TOKEN}/chats?page=1&pageSize=50"

headers = {"Client-Token": CLIENT_TOKEN}

try:
  # verify=False pula a verificação do certificado SSL que estava travando
  response = requests.get(url, headers=headers, verify=False)

  if response.status_code == 200:
    dados = response.json()
    print("\n--- 📋 BUSCANDO GRUPOS ---")

    encontrou_grupo = False
    for chat in dados:
      if chat.get("isGroup") is True:
        encontrou_grupo = True
        nome = chat.get("name")
        group_id = chat.get("phone")  # ID do grupo no formato xxxxx-group ou xxxxx@g.us

        print(f"📌 Nome do Grupo: {nome}")
        print(f"🆔 GRUPO_ID: {group_id}")
        print("-" * 30)

    if not encontrou_grupo:
      print("Nenhum grupo encontrado nesta conta do WhatsApp.")
  else:
    print(f"Erro na API ({response.status_code}): {response.text}")

except Exception as e:
  print(f"Erro ao buscar: {e}")