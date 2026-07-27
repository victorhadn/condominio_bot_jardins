from datetime import datetime
import json
import os

ARQUIVO_AVISOS = "avisos.json"


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


def cadastrar_novo_aviso():
  print("\n--- 📝 CADASTRO DE NOVO AVISO / LEMBRETE ---")

  identificador = input(
      "Identificador do aviso (ex: elevador_agosto): "
  ).strip()

  print(
      "\nDigite a mensagem do aviso (pode usar *negrito* do WhatsApp)."
      " Digite 'FIM' em uma linha separada para encerrar a mensagem:"
  )

  linhas_mensagem = []
  while True:
    linha = input()
    if linha.strip() == "FIM":
      break
    linhas_mensagem.append(linha)

  mensagem = "\n".join(linhas_mensagem)

  # Validação de Data
  while True:
    data_fim = input(
        "\nData limite para envio (Formato DD/MM/AAAA): "
    ).strip()
    try:
      data_dt = datetime.strptime(data_fim, "%d/%m/%Y")
      data_fim_iso = data_dt.strftime("%Y-%m-%d")
      break
    except ValueError:
      print("❌ Data inválida! Use o formato DD/MM/AAAA.")

  # Horários de envio
  print("\nDigite os horários em que a mensagem deve ser enviada.")
  horarios = []
  qtd = input("Quantas vezes por dia deseja enviar? (Padrão = 2): ").strip()
  qtd = int(qtd) if qtd.isdigit() else 2

  for i in range(1, qtd + 1):
    while True:
      hora = input(
          f"Horário {i} (Formato HH:MM, ex: 08:00 ou 13:30): "
      ).strip()
      try:
        datetime.strptime(hora, "%H:%M")
        horarios.append(hora)
        break
      except ValueError:
        print("❌ Horário inválido! Use o formato HH:MM (ex: 08:00).")

  # Monta a estrutura do novo aviso
  novo_aviso = {
      "id": identificador,
      "mensagem": mensagem,
      "data_fim": data_fim_iso,
      "horarios": horarios,
  }

  avisos = carregar_avisos()
  avisos.append(novo_aviso)
  salvar_avisos(avisos)

  print(f"\n✅ Aviso '{identificador}' cadastrado com sucesso!")


def listar_avisos():
  avisos = carregar_avisos()
  if not avisos:
    print("\nNenhum aviso cadastrado.")
    return

  print("\n--- 📋 AVISOS CADASTRADOS ---")
  for idx, a in enumerate(avisos, 1):
    data_br = datetime.strptime(a["data_fim"], "%Y-%m-%d").strftime("%d/%m/%Y")
    print(f"\n[{idx}] ID: {a['id']}")
    print(f"    Data limite: {data_br}")
    print(f"    Horários: {', '.join(a['horarios'])}")
    print(f"    Mensagem:\n{a['mensagem']}")
    print("-" * 30)


def menu():
  while True:
    print("\n=== GERENCIADOR DE AVISOS DO CONDOMÍNIO ===")
    print("1. Cadastrar novo aviso")
    print("2. Listar avisos cadastrados")
    print("3. Sair")

    opcao = input("\nEscolha uma opção: ").strip()

    if opcao == "1":
      cadastrar_novo_aviso()
    elif opcao == "2":
      listar_avisos()
    elif opcao == "3":
      print("Saindo...")
      break
    else:
      print("Opção inválida.")


if __name__ == "__main__":
  menu()