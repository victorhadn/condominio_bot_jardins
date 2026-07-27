from datetime import datetime
import json
import os
from urllib.parse import unquote
import zoneinfo  # Biblioteca nativa do Python 3.9+
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, redirect, render_template, request, url_for
import requests

app = Flask(__name__)
ARQUIVO_AVISOS = "avisos.json"

# Configurações da Evolution API
EVOLUTION_URL = os.getenv(
    "EVOLUTION_URL", "https://evolution-condominio.onrender.com"
)
INSTANCE_NAME = os.getenv("INSTANCE_NAME", "condominio_bot")
API_KEY = os.getenv("API_KEY", "MinhaChaveSuperSecreta123")
GRUPO_ID = os.getenv("GRUPO_ID", "558398322454-1547988466@g.us")


def carregar_avisos():
  if not os.path.exists(ARQUIVO_AVISOS):
    return []
  with open(ARQUIVO_AVISOS, "r", encoding="utf-8") as f:
    try:
      return json.load(f)
    except json.JSONDecodeError:
      return []


def salvar_avisos(avisos):
  with open(ARQUIVO_AVISOS, "w", encoding="utf-8") as f:
    json.dump(avisos, f, ensure_ascii=False, indent=2)


def enviar_mensagem_whatsapp(texto):
  url = f"{EVOLUTION_URL}/message/sendText/{INSTANCE_NAME}"
  headers = {"Content-Type": "application/json", "apikey": API_KEY}
  payload = {"number": GRUPO_ID, "text": texto}

  try:
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code in [200, 201]:
      print(
          f"[{datetime.now().strftime('%H:%M')}] 🚀 Mensagem enviada via"
          " Evolution API!"
      )
    else:
      print(
          f"❌ Erro na Evolution API ({response.status_code}): {response.text}"
      )
  except Exception as e:
    print(f"❌ Erro ao enviar mensagem no WhatsApp: {e}")


def verificar_e_disparar_avisos():
  avisos = carregar_avisos()

  # Força a busca do horário oficial de Brasília/São Paulo
  fuso_br = zoneinfo.ZoneInfo("America/Sao_Paulo")
  agora_br = datetime.now(fuso_br)

  hoje = agora_br.date()
  hora_atual = agora_br.strftime("%H:%M")

  for aviso in avisos:
    data_fim = datetime.strptime(aviso["data_fim"], "%Y-%m-%d").date()
    if hoje <= data_fim:
      if hora_atual in aviso["horarios"]:
        enviar_mensagem_whatsapp(aviso["mensagem"])


# Inicializa o agendador no fuso horário do Brasil
fuso_br = zoneinfo.ZoneInfo("America/Sao_Paulo")
scheduler = BackgroundScheduler(timezone=fuso_br)
scheduler.add_job(verificar_e_disparar_avisos, "interval", minutes=1)
scheduler.start()


@app.route("/")
def index():
  avisos = carregar_avisos()
  return render_template("index.html", avisos=avisos)


@app.route("/adicionar", methods=["POST"])
def adicionar():
  identificador = request.form.get("id")
  mensagem = request.form.get("mensagem")
  data_fim = request.form.get("data_fim")

  campos_horarios = [
      request.form.get("horario1"),
      request.form.get("horario2"),
      request.form.get("horario3"),
      request.form.get("horario4"),
      request.form.get("horario5"),
      request.form.get("horario6"),
  ]

  horarios = [h for h in campos_horarios if h]

  novo_aviso = {
      "id": identificador,
      "mensagem": mensagem,
      "data_fim": data_fim,
      "horarios": horarios,
  }

  avisos = carregar_avisos()
  avisos.append(novo_aviso)
  salvar_avisos(avisos)

  return redirect(url_for("index"))


@app.route("/deletar/<path:id_aviso>")
def deletar(id_aviso):
  avisos = carregar_avisos()
  id_limpo = unquote(id_aviso).strip()
  avisos = [a for a in avisos if str(a.get("id", "")).strip() != id_limpo]
  salvar_avisos(avisos)
  return redirect(url_for("index"))


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port, debug=False)
