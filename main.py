import requests
from geopy.distance import geodesic
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()


# Variáveis de ambiente
EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE")
EMAIL_DESTINO = os.getenv("EMAIL_DESTINO")
EMAIL_SENHA = os.getenv("EMAIL_SENHA")

LOCAIS = {
    "Casa Mãe": tuple(float(coord.strip()) for coord in os.getenv("COORDS_CASA", "0,0").split(",")),
    "Casa Pai": tuple(float(coord.strip()) for coord in os.getenv("COORDS_CASA2", "0,0").split(",")),
    "Ramos Ferreira": tuple(float(coord.strip()) for coord in os.getenv("COORDS_RF", "0,0").split(",")),
}

# 🎯 Raio de busca em km
RAIO_KM = 8

def enviar_email(assunto, corpo):
    """Envia um e-mail usando SMTP do Gmail"""
    msg = MIMEMultipart()
    msg["From"] = EMAIL_REMETENTE
    msg["To"] = EMAIL_DESTINO
    msg["Subject"] = assunto
    msg.attach(MIMEText(corpo, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as servidor:
            servidor.ehlo()  # Identifica-se no servidor
            servidor.starttls()  # Inicia conexão segura
            servidor.ehlo()  # Reconfirma após TLS
            servidor.login(EMAIL_REMETENTE, EMAIL_SENHA)  # Login
            servidor.send_message(msg)  # Envia email

        print("📧 Email enviado com sucesso!")

    except smtplib.SMTPAuthenticationError as e:
        print("❌ Erro de autenticação SMTP.")
        print("   - Verifique se EMAIL_REMETENTE é o mesmo usado na senha de App.")
        print("   - Garanta que a senha de App está sem espaços.")
        print("   - Verifique se a verificação em 2 passos está ativa.")
        print("Detalhes:", e)

    except Exception as e:
        print("❌ Erro ao enviar email:", e)

def obter_incendios():
    """Obtém lista de incêndios ativos do fogos.pt"""
    url = "https://api.fogos.pt/v2/incidents/active"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        dados = resp.json()
        return dados.get("data", [])
    except requests.RequestException as e:
        print("❌ Erro ao acessar API:", e)
        return []


def dentro_raio(lat, lng, raio_km, origem):
    """Verifica se a coordenada está dentro do raio definido para um local de origem"""
    try:
        lat = float(lat)
        lng = float(lng)
    except (TypeError, ValueError):
        return False, None

    distancia = geodesic(origem, (lat, lng)).km
    return distancia <= raio_km, distancia



def incendios_proximos_por_local():
    """Retorna incêndios dentro do raio para cada local, com raio customizado"""
    resultados = {}
    incendios = obter_incendios()
    for nome, coords in LOCAIS.items():
        if nome in ["Casa Pai", "Ramos Ferreira"]:
            raio = 3
        else:
            raio = RAIO_KM
        proximos = []
        for incendio in incendios:
            lat = incendio.get("lat")
            lng = incendio.get("lng")
            if lat is not None and lng is not None:
                no_raio, distancia = dentro_raio(lat, lng, raio, coords)
                if no_raio:
                    incendio_local = incendio.copy()
                    incendio_local["distancia_km"] = round(distancia, 2)
                    proximos.append(incendio_local)
        # Ordena do mais perto ao mais longe
        proximos.sort(key=lambda x: x.get("distancia_km", float("inf")))
        resultados[nome] = proximos
    return resultados



if __name__ == "__main__":
    resultados = incendios_proximos_por_local()

    texto_email = ""
    houve_incendios = False
    for nome, proximos in resultados.items():
        raio_local = 3 if nome in ["Casa Pai", "Ramos Ferreira"] else RAIO_KM
        if proximos:
            houve_incendios = True
            texto_email += f"<h3>🔥 Incêndios num raio de {raio_local} km de {nome}:</h3><br>"
            for inc in proximos:
                operacionais = inc.get("man", 0)
                veiculos = inc.get("terrain", 0)
                aereos = inc.get("aerial", 0)
                lat = inc.get("lat")
                lng = inc.get("lng")
                maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}" if lat and lng else ""
                status = inc.get("status", "N/A")
            coord_link = f'<a href="{maps_url}">{lat}, {lng}</a>' if maps_url else f"{lat}, {lng}"
            info = (
                f"<b>- {inc['location']} ({inc['concelho']}) - {inc['distancia_km']} km</b><br>"
                f"🟠 <b>Status:</b> {status}<br>"
                f"🌍 <b>Coordenadas:</b> {coord_link}<br>"
                f"👨‍🚒 <b>Operacionais:</b> {operacionais}<br>"
                f"🚒 <b>Veículos terrestres:</b> {veiculos}<br>"
                f"✈️ <b>Meios aéreos:</b> {aereos}<br><br>"
            )
            texto_email += info
        else:
            texto_email += f"<h3>✅ Nenhum incêndio num raio de {raio_local} km de {nome}.</h3><br>"

    if houve_incendios:
        enviar_email("🔥 Alerta de Incêndio Próximo", texto_email)

