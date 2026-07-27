from datetime import datetime
import json
import os
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, redirect, render_template, request, url_for
import requests

app = Flask(__name__)
ARQUIVO_AVISOS = "avisos.json"

# --- CONFIGURAÇÕES DA EVOLUTION API ---
EVOLUTION_URL = "https://evolution-condominio.onrender.com"
INSTANCE_NAME = "condominio_bot"
API_KEY = "MinhaChaveSuperSecreta123"  

# ID do grupo obtido no WhatsApp (formato @g.us para Evolution API v2)
GRUPO_ID = "120363426637457947@g.us"


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


# --- LÓGICA DE DISPARO VIA EVOLUTION API ---
def enviar_mensagem_whatsapp(texto):
  # Endpoint oficial da Evolution API v2 para envio de mensagem de texto
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
  hoje = datetime.now().date()
  hora_atual = datetime.now().strftime("%H:%M")

  for aviso in avisos:
    data_fim = datetime.strptime(aviso["data_fim"], "%Y-%m-%d").date()
    if hoje <= data_fim:
      if hora_atual in aviso["horarios"]:
        enviar_mensagem_whatsapp(aviso["mensagem"])


# Inicializa o Agendador em segundo plano (roda a cada 1 minuto)
scheduler = BackgroundScheduler()
scheduler.add_job(verificar_e_disparar_avisos, "interval", minutes=1)
scheduler.start()


# --- ROTAS DO PAINEL WEB ---
@app.route("/")
def index():
  avisos = carregar_avisos()
  return render_template("index.html", avisos=avisos)


@app.route("/adicionar", methods=["POST"])
def adicionar():
  identificador = request.form.get("id")
  mensagem = request.form.get("mensagem")
  data_fim = request.form.get("data_fim")
  horario1 = request.form.get("horario1")
  horario2 = request.form.get("horario2")

  horarios = [h for h in [horario1, horario2] if h]

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


@app.route("/deletar/<id_aviso>")
def deletar(id_aviso):
  avisos = carregar_avisos()
  avisos = [a for a in avisos if a["id"] != id_aviso]
  salvar_avisos(avisos)
  return redirect(url_for("index"))


if __name__ == "__main__":
  # Pega a porta automática do Render ou usa 5000 se rodar local
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port, debug=False)