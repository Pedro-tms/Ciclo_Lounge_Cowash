import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, request, jsonify, redirect, url_for, render_template
import requests
from datetime import datetime

app = Flask(__name__)


VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "PIRIQUTINHO_SECRETO_2025")

ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN", "EAAKZCinaRB70BQCKe5koIcNZAZC4Uq7AzMR1KDOu6BlHZB674oPPj32QDIPIXzbIgayvUvJZBKXZCLKlxxWsOgE841v48sdr8yNUZCNmgJEtTZBipujyqTOTmVfAWisiHVjPeaIXR2ayWdRICNvv2lciQ7bK4aVWiZAiJMejGoJWQUSErttXvcaG68NucT1Col0Y0qpWDAXAyYYXgnP0RHlkP41xZBBbeuU4yp1A7Ikv6RVXJzD6gxLRxZAjjaNZCSR9EfhdYjM47lpPerZAwIMxUPFZAX")

PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID", "906558885868072")

DATABASE_URL = os.environ.get("DATABASE_URL")

API_URL = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"


def get_db_connection():
    if not DATABASE_URL:
        print("❌ ERRO CRÍTICO: A variável DATABASE_URL não foi configurada no Render!")
        return None
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

def init_db():
    try:
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            # Cria tabela compatível com Postgres
            cur.execute('''CREATE TABLE IF NOT EXISTS historico 
                        (id SERIAL PRIMARY KEY, 
                        cliente_numero TEXT, 
                        mensagem TEXT, 
                        origem TEXT, 
                        horario TEXT)''')
            conn.commit()
            cur.close()
            conn.close()
            print("✅ Banco de Dados Neon Conectado!")
    except Exception as e:
        print(f"❌ Erro ao conectar no banco: {e}")

if DATABASE_URL:
    init_db()


def processar_mensagem(texto):
    texto = texto.lower()
    saudacoes = ["olá", "ola", "oi", "opa", "buenas", "eai", "fala", "bom", "boa", "salve", "tarde", "noite", "voltar", "inicio", "menu"]
    
    if any(s in texto for s in saudacoes) and not any(n in texto for n in ["1", "2", "3", "4", "5"]):
        return (
            "👋 Olá, seja bem-vindo à *Barbearia Piriquito*!\n"
            "Como podemos te ajudar hoje?\n\n"
            "1️⃣ Agendar horário\n"
            "2️⃣ Serviços & Preços\n"
            "3️⃣ Mais Informações\n"
            "4️⃣ Falar com Atendente"
        )
        
    elif "1" in texto or "agendar" in texto:
        return "📅 *Agendamento Online:*\nhttps://cashbarber.com.br/barbeariapirikito\n\nEnvie *5* se precisar de ajuda."
        
    elif "2" in texto or "serviços" in texto or "preços" in texto:
        return (
            "✂️ *Tabela de Preços:*\n\n"
            "• Corte Tradicional: R$ 38,00\n"
            "• Barba Tradicional: R$ 22,00\n"
            "• Combo (Corte + Barba): R$ 50,00"
        )

    elif "3" in texto or "info" in texto or "endereço" in texto:
        return "📍 *Endereço:* Rua Exemplo, 123.\n⏰ *Horário:* Seg-Sab 09h às 19h."
        
    elif "4" in texto or "5" in texto or "falar" in texto or "humano" in texto:
        return "🧔 *Entendido!* Já chamei o barbeiro no painel. Aguarde um instante."
        
    else:
        return "🤔 Não entendi. Digite o número da opção (1, 2, 3 ou 4)."

def salvar_no_historico(numero, mensagem, origem):
    try:
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            hora = datetime.now().strftime("%H:%M") 
            # Postgres usa %s
            cur.execute("INSERT INTO historico (cliente_numero, mensagem, origem, horario) VALUES (%s, %s, %s, %s)", 
                    (numero, mensagem, origem, hora))
            conn.commit()
            cur.close()
            conn.close()
    except Exception as e:
        print(f"❌ Erro ao salvar no banco: {e}")

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

@app.route("/painel")
def painel():
    cliente_selecionado = request.args.get("cliente")
    try:
        conn = get_db_connection()
        if not conn:
            return "Erro: Configure a DATABASE_URL no Render!"
            
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
    except Exception as e:
        return f"Erro ao carregar painel: {e}"

if __name__ == "__main__":
    app.run(port=5000)