import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, request, jsonify, redirect, url_for, render_template
import requests
from datetime import datetime

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "PIRIQUTINHO_SECRETO_2025")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN", "EAAKZCinaRB70BQCKe5koIcNZAZC4Uq7AzMR1KDOu6BlHZB674oPPj32QDIPIXzbIgayvUvJZBKXZCLKlxxWsOgE841v48sdr8yNUZCNmgJEtTZBipujyqTOTmVfAWisiHVjPeaIXR2ayWdRICNvv2lciQ7bK4aVWiZAiJMejGoJWQUSErttXvcaG68NucT1Col0Y0qpWDAXAyYYXgnP0RHlkP41xZBBbeuU4yp1A7Ikv6RVXJzD6gxLRxZAjjaNZCSR9EfhdYjM47lpPerZAwIMxUPFZAX")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID", "906558885868072")
DATABASE_URL = os.environ.get("DATABASE_URL") # URL do Neon (Vem do Render)

API_URL = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"


def get_db_connection():
    # Se tiver URL do banco (Render), usa PostgreSQL
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

def processar_mensagem(texto):
    texto = texto.lower()
    
    saudacoes = ["olá", "ola", "oi", "opa", "buenas", "eai", "fala", "bom", "boa", "salve", "tarde", "noite", "voltar", "inicio", "início", "menu"]
    
    if any(s in texto for s in saudacoes) and not any(n in texto for n in ["1", "2", "3", "4", "5"]):
        return (
            "👋 Olá, seja bem-vindo à *Barbearia Piriquito*!\n"
            "Como podemos te ajudar hoje?\n\n"
            "1️⃣ Agendar horário\n"
            "2️⃣ Serviços & Preços\n"
            "3️⃣ Mais Informações\n"
            "4️⃣ Falar com Atendente"
        )
        
    elif "1" in texto or "agendar" in texto or "marcar" in texto:
        return (
            "Ótima escolha! 😄✂️\n\n"
            "Para agendar seu horário agora, é só clicar no link abaixo:\n\n"
            "📅 *Agendamento Online:*\n"
            "https://cashbarber.com.br/barbeariapirikito\n\n"
            "Se tiver dificuldade ou quiser falar com a gente, envie:\n"
            "5️⃣ Falar com atendente"
        )
        
    elif "2" in texto or "serviços" in texto or "preços" in texto or "valor" in texto:
        return (
            "Aqui estão nossos serviços disponíveis ✂️\n\n"
            "💈 *Cabelo*\n"
            "• Corte Tradicional – R$ 35\n"
            "• Corte Navalhado – R$ 40\n"
            "• Corte Máquina – R$ 30\n\n"
            "🧔 *Barba*\n"
            "• Barba Tradicional – R$ 30\n"
            "• Barba Navalhada – R$ 35\n"
            "• Barba + Hidratação – R$ 45\n\n"
            "🔥 *Combos*\n"
            "• Corte + Barba – R$ 60\n"
            "• Corte + Barba + Sobrancelha – R$ 70\n\n"
            "✨ *Extras*\n"
            "• Sobrancelha – R$ 10\n"
            "• Hidratação – R$ 20\n"
            "• Pigmentação – R$ 25\n\n"
            "👉 *O que deseja fazer?*\n"
            "1️⃣ Agendar agora\n"
            "4️⃣ Falar com Atendente"
        )

    elif "3" in texto or "informações" in texto or "info" in texto or "endereço" in texto or "onde" in texto:
        return (
            "📍 *Barbearia Piriquito*\n\n"
            "🏢 *Endereço:*\n"
            "Rua Exemplo, 123 - Centro\n"
            "(Ao lado da Padaria Central)\n\n"
            "⏰ *Horário de Atendimento:*\n"
            "Seg a Sex: 09h às 19h\n"
            "Sábado: 09h às 17h\n\n"
            "🚗 *Estacionamento:* Gratuito na frente.\n\n"
            "Digite *Voltar* para ver o menu."
        )
        
    elif "4" in texto or "5" in texto or "falar" in texto or "humano" in texto or "atendente" in texto:
        return (
            "🧔 *Entendido!*\n\n"
            "Já notifiquei um de nossos barbeiros e ele vai assumir essa conversa em instantes.\n"
            "Pode escrever sua dúvida abaixo enquanto aguarda! 👇"
        )
        
    else:
        return (
            "🤔 Desculpe, não entendi.\n\n"
            "Por favor, digite o número da opção:\n"
            "1️⃣ Agendar\n"
            "2️⃣ Preços\n"
            "3️⃣ Informações\n"
            "4️⃣ Falar com Atendente"
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
    import requests 
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
    try:
        if data.get("entry") and data["entry"][0].get("changes"):
            value = data["entry"][0]["changes"][0]["value"]
            if value.get("messages"):
                message_data = value["messages"][0]
                from_number = message_data["from"] 
                if message_data["type"] == "text":
                    text_content = message_data["text"]["body"]
                    
                    salvar_no_historico(from_number, text_content, "Cliente")
                    resposta_bot = processar_mensagem(text_content)
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
