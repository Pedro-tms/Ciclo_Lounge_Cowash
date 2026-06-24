import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, request, jsonify, redirect, url_for, render_template
import requests
from datetime import datetime

app = Flask(__name__)

clientes_pausados = set()

VERIFY_TOKEN = "PIRIQUTINHO_SECRETO_2025"
ACCESS_TOKEN = "EAAKZCinaRB70BRxhEtDX2q0Hiko3MfLZAAhE5KkZCe0g1JD6dPXk3PNIrts1tGrciwAPSLzYIwBtDktk1ZBxcjNPbcbyY8qhL7FxBoE11xjfL0JjVofl10EGsw4UVZACUEEvEVXOHLbg3oYqV9vKeMmIftyevavOuBZBzkeuw3uHMcL1VZB2VtY1fFG5PZCQGgqBp4FSRQjp7rIDZCZAuBcdc214aLMic8tRZAf9uyP7sXd44xirR0Bfcy0TLayZAFWk1TEyX12aKoIZAEaskmGngnema"
PHONE_NUMBER_ID = "1202161662978511"
DATABASE_URL = "postgresql://neondb_owner:npg_Ux8NcsB6MTDq@ep-damp-heart-ac8f0me5-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
API_URL = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

def get_db_connection():
    if DATABASE_URL:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    else:
        print("❌ ERRO: DATABASE_URL não encontrada!")
        return None

def init_db():
    try:
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            cur.execute('''CREATE TABLE IF NOT EXISTS historico 
                        (id SERIAL PRIMARY KEY, 
                        cliente_numero TEXT, 
                        mensagem TEXT, 
                        origem TEXT, 
                        horario TEXT)''')
            conn.commit()
            cur.close()
            conn.close()
            print("✅ Banco de Dados Conectado!")
    except Exception as e:
        print(f"❌ Erro ao conectar no banco: {e}")

if DATABASE_URL:
    init_db()

def processar_mensagem(texto, numero):
    global clientes_pausados
    texto = texto.lower()
    
    comandos_voltar = ["0", "voltar", "menu", "inicio", "início"]
    if any(comando in texto.split() for comando in comandos_voltar) or texto.strip() == "0":
        if numero in clientes_pausados:
            clientes_pausados.remove(numero)
            
        return (
            "👋 *Menu Principal - Ciclo Lounge Cowash* 🧺✨\n\n"
            "Como podemos te ajudar hoje?\n"
            "1️⃣ Como funciona (Lavanderia & Lounge)\n"
            "2️⃣ Serviços & Preços\n"
            "3️⃣ Endereço e Horários\n"
            "4️⃣ Falar com Atendente"
        )
    
    if numero in clientes_pausados:
        return None
        
    saudacoes = ["olá", "ola", "oi", "opa", "buenas", "eai", "fala", "bom", "boa", "salve", "tarde", "noite"]
    if any(s in texto.split() for s in saudacoes) and not any(n in texto for n in ["1", "2", "3", "4", "5"]):
        return (
            "👋 Olá, seja bem-vindo à *Ciclo Lounge Cowash*! 🧺✨\n"
            "Muito mais que uma lavanderia, um espaço para você.\n"
            "Como podemos te ajudar hoje?\n\n"
            "1️⃣ Como funciona (Lavanderia & Lounge)\n"
            "2️⃣ Serviços & Preços\n"
            "3️⃣ Endereço e Horários\n"
            "4️⃣ Falar com Atendente"
        )
        
    elif "1" in texto or "funciona" in texto or "lounge" in texto or "coleta" in texto:
        return (
            "A *Ciclo Lounge Cowash* é o seu novo conceito de lavanderia! 🫧🛋️\n\n"
            "Temos duas modalidades para você com a mesma qualidade de sempre:\n\n"
            "🔄 *Autoatendimento:* Mais liberdade para cuidar das suas roupas no seu tempo.\n"
            "🏠 *Em Casa:* Cuidado premium com coleta, lavagem, secagem e entrega expressa à combinar.\n\n"
            "📱 *Conheça nosso espaço no Instagram:*\n"
            "https://www.instagram.com/cicloloungecowash/\n\n"
            "👉 *Envie 4 para falar com nossa equipe e agendar uma coleta!*\n\n"
            "🔙 *Digite 0 ou Menu para voltar.*"
        )
        
    elif "2" in texto or "serviços" in texto or "preços" in texto or "valor" in texto or "ciclo" in texto:
        return (
            "Aqui estão nossos serviços e valores 🫧\n\n"
            "🧺 *Self-Service (Faça você mesmo)*\n"
            "• Ciclo de Lavagem – R$ 18,00\n"
            "• Ciclo de Secagem – R$ 18,00\n\n"
            "👔 *Drop & Go (Deixe com a gente)*\n"
            "• Cesto Completo (Lavar + Secar + Dobrar) – R$ 45,00\n\n"
            "☕ *Lounge*\n"
            "• Wi-Fi e Café cortesia para clientes no local!\n\n"
            "🔙 *Digite 0 ou Menu para voltar.*"
        )

    elif "3" in texto or "informações" in texto or "info" in texto or "endereço" in texto or "onde" in texto:
        return (
            "📍 *Ciclo Lounge Cowash*\n\n"
            "🏢 *Endereço:*\n"
            "Av. Farroupilha, 8030 - São José, Canoas - RS, 92425-056\n\n"
            "⏰ *Horário de Funcionamento:*\n"
            "Segunda a Sábado: 07h30 às 22h30\n"
            "Domingos e Feriados: 08h00 às 22h00\n\n"
            "⚠️ *Avisos Importantes:*\n"
            "• Não possuímos estacionamento no local.\n\n"
            "📱 *Siga nosso Instagram:*\n"
            "https://www.instagram.com/cicloloungecowash/\n\n"
            "🔙 *Digite 0 ou Menu para voltar.*"
        )
        
    elif "4" in texto or "5" in texto or "falar" in texto or "humano" in texto or "atendente" in texto:
        # Coloca o cliente na lista de silenciados
        clientes_pausados.add(numero)
        return (
            "👤 *Entendido!*\n\n"
            "Já notifiquei nossa equipe e um de nossos atendentes vai assumir essa conversa em instantes.\n"
            "Pode escrever sua dúvida abaixo enquanto aguarda no nosso lounge virtual! 👇\n\n"
            "🔙 *Se resolveu sua dúvida e quiser cancelar o atendimento, digite 0 para voltar ao menu.*"
        )
        
    else:
        return (
            "🤔 Desculpe, não entendi.\n\n"
            "Por favor, digite o número da opção desejada:\n"
            "1️⃣ Como funciona (Lavanderia & Lounge)\n"
            "2️⃣ Serviços & Preços\n"
            "3️⃣ Endereço e Horários\n"
            "4️⃣ Falar com Atendente\n\n"
            "🔙 *Ou digite 0 para voltar ao menu inicial.*"
        )

def salvar_no_historico(numero, mensagem, origem):
    try:
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            hora = datetime.now().strftime("%H:%M") 
            cur.execute("INSERT INTO historico (cliente_numero, mensagem, origem, horario) VALUES (%s, %s, %s, %s)", 
                    (numero, mensagem, origem, hora))
            conn.commit()
            cur.close()
            conn.close()
    except Exception as e:
        print(f"Erro banco: {e}")

def send_whatsapp_message(to_number, text_message):
    global API_URL, ACCESS_TOKEN 

    if len(to_number) == 12 and to_number.startswith("55"):
        to_number = to_number[:4] + "9" + to_number[4:]
        print(f"🔧 Número corrigido: {to_number}")

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text_message},
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        print(f"Status Envio: {response.status_code}")
        if response.status_code != 200:
            print(f"❌ Resposta detalhada do erro da Meta: {response.json()}")
    except Exception as e:
        print(f"Erro conexão: {e}")

@app.route("/webhook", methods=["GET"])
def handle_verification():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return jsonify({"status": "Falha"}), 403

@app.route("/webhook", methods=["POST"])
def handle_message():
    data = request.get_json()

    print("\n📦 --- NOVO WEBHOOK DA META ---")
    print(json.dumps(data, indent=2))
    print("-------------------------------\n")

    try:
        if data.get("entry") and data["entry"][0].get("changes"):
            value = data["entry"][0]["changes"][0]["value"]
            if value.get("messages"):
                message_data = value["messages"][0]
                from_number = message_data["from"] 
                if message_data["type"] == "text":
                    text_content = message_data["text"]["body"]
                    salvar_no_historico(from_number, text_content, "Cliente")
                    resposta_bot = processar_mensagem(text_content, from_number)
                    if resposta_bot:
                        salvar_no_historico(from_number, resposta_bot, "Bot")
                        send_whatsapp_message(from_number, resposta_bot)
    except Exception as e:
        print(f"Erro webhook: {e}")
    return jsonify({"status": "ok"}), 200

@app.route("/enviar_manual", methods=["POST"])
def enviar_manual():
    numero = request.form.get("numero")
    mensagem = request.form.get("mensagem")
    if numero and mensagem:
        salvar_no_historico(numero, mensagem, "Atendente")
        send_whatsapp_message(numero, mensagem)
    return redirect(url_for('painel', cliente=numero))

@app.route("/")
def index():
    return redirect(url_for('painel'))

@app.route("/encerrar_atendimento", methods=["POST"])
def encerrar_atendimento():
    global clientes_pausados
    numero = request.form.get("numero")
    
    if numero in clientes_pausados:
        clientes_pausados.remove(numero)
        
        mensagem_encerramento = (
            "✅ *Atendimento encerrado.*\n\n"
            "Agradecemos o contato! Voltando ao menu inicial:\n"
            "1️⃣ Como funciona (Lavanderia & Lounge)\n"
            "2️⃣ Serviços & Preços\n"
            "3️⃣ Endereço e Horários\n"
            "4️⃣ Falar com Atendente"
        )
        
        salvar_no_historico(numero, mensagem_encerramento, "Bot")
        send_whatsapp_message(numero, mensagem_encerramento)
        
    return redirect(url_for('painel', cliente=numero))


@app.route("/deletar_conversa", methods=["POST"])
def deletar_conversa():
    numero = request.form.get("numero")
    if numero:
        try:
            conn = get_db_connection()
            if conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM historico WHERE cliente_numero = %s", (numero,))
                conn.commit()
                cur.close()
                conn.close()
        except Exception as e:
            print(f"Erro ao deletar: {e}")
            
    return redirect(url_for('painel'))

@app.route("/painel")
def painel():
    cliente_selecionado = request.args.get("cliente")
    try:
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            
            cur.execute("""
                SELECT cliente_numero, MAX(id) as ultimo_id 
                FROM historico 
                GROUP BY cliente_numero 
                ORDER BY ultimo_id DESC
            """)
            clientes = [dict(row) for row in cur.fetchall()]
            
            mensagens = []
            if cliente_selecionado:
                cur.execute("SELECT * FROM historico WHERE cliente_numero = %s ORDER BY id ASC", (cliente_selecionado,))
                mensagens = [dict(row) for row in cur.fetchall()]
            
            cur.close()
            conn.close()
            
            return render_template("painel.html", clientes=clientes, mensagens=mensagens, selecionado=cliente_selecionado)
        else:
            return "Erro de Conexão com o Banco"
    except Exception as e:
        return f"Erro Painel: {e}"

if __name__ == "__main__":
    app.run(port=5000)