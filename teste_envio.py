import requests

# --- SUAS CONFIGURAÇÕES ---
TOKEN = "EAAKZCinaRB70BQCKe5koIcNZAZC4Uq7AzMR1KDOu6BlHZB674oPPj32QDIPIXzbIgayvUvJZBKXZCLKlxxWsOgE841v48sdr8yNUZCNmgJEtTZBipujyqTOTmVfAWisiHVjPeaIXR2ayWdRICNvv2lciQ7bK4aVWiZAiJMejGoJWQUSErttXvcaG68NucT1Col0Y0qpWDAXAyYYXgnP0RHlkP41xZBBbeuU4yp1A7Ikv6RVXJzD6gxLRxZAjjaNZCSR9EfhdYjM47lpPerZAwIMxUPFZAX"
PHONE_ID = "906558885868072"
URL = f"https://graph.facebook.com/v19.0/{PHONE_ID}/messages"

def enviar_teste(numero_destino, descricao):
    print(f"\n--- Testando envio para: {numero_destino} ({descricao}) ---")
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": numero_destino,
        "type": "text",
        "text": {"body": f"Teste de envio direto para {descricao}"}
    }
    
    try:
        response = requests.post(URL, headers=headers, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Resposta da Meta: {response.text}")
    except Exception as e:
        print(f"Erro de conexão: {e}")

# --- EXECUÇÃO ---

# TESTE 1: Número SEM o 9 (Como veio no Webhook)
# Formato: 55 + 51 + 82873027
enviar_teste("555182873027", "SEM O NOVE")

# TESTE 2: Número COM o 9 (Padrão Brasil atual)
# Formato: 55 + 51 + 9 + 82873027
enviar_teste("5551982873027", "COM O NOVE")