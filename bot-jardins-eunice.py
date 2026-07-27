from datetime import datetime
import json
import os
from apscheduler.schedulers.blocking import BlockingScheduler
import requests

# Configurações da API de WhatsApp (Ex: Evolution API)
API_URL = "https://sua-api-whatsapp.com/message/sendText"
API_TOKEN = "SEU_TOKEN_DE_AUTENTICACAO"
GRUPO_ID = "120363123456789@g.us"  # ID do grupo de comunicados


def enviar_mensagem_whatsapp(texto):
  payload = {"number": GRUPO_ID, "textMessage": {"text": texto}}
  headers = {"Content-Type": "application/json", "apikey": API_TOKEN}

  try:
    response = requests.post(API_URL, json=payload, headers=headers)
    if response.status_code in [200, 201]:
      print(
          f"[{datetime.now().strftime('%d/%m/%Y %H:%M')}] Lembrete enviado com"
          " sucesso!"
      )
    else:
      print(f"Erro ao enviar: {response.text}")
  except Exception as e:
    print(f"Erro de conexão com a API: {e}")


def verificar_e_disparar_avisos():
  if not os.path.exists("avisos.json"):
    print("Arquivo avisos.json não encontrado.")
    return

  with open("avisos.json", "r", encoding="utf-8") as f:
    avisos = json.load(f)

  hoje = datetime.now().date()
  hora_atual = datetime.now().strftime("%H:%M")

  print(
      f"Executando verificação de rotina... Horário atual: {hora_atual} | Data:"
      f" {hoje}"
  )

  for aviso in avisos:
    data_fim = datetime.strptime(aviso["data_fim"], "%Y-%m-%d").date()

    # Verifica se a data de hoje ainda está no período do aviso
    if hoje <= data_fim:
      # Verifica se o horário atual bate com algum dos horários configurados
      if hora_atual in aviso["horarios"]:
        print(f"Disparando aviso ativo: {aviso['id']}")
        enviar_mensagem_whatsapp(aviso["mensagem"])


# Configurando o Agendador
scheduler = BlockingScheduler()

# Roda a função de verificação a cada minuto para checar se bateu o horário
scheduler.add_job(verificar_e_disparar_avisos, "interval", minutes=1)

print("🤖 Bot de Lembretes do Condomínio iniciado. Aguardando horários...")

try:
  scheduler.start()
except (KeyboardInterrupt, SystemExit):
  print("Bot encerrado.")