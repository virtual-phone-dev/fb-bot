import os
import requests
from dotenv import load_dotenv

# Charger les variables du fichier .env
load_dotenv()

# Récupérer les identifiants
PAGE_ID = os.getenv("PAGE_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

# Vérifier la configuration
if not PAGE_ID or not ACCESS_TOKEN:
    raise ValueError("FB_PAGE_ID ou FB_PAGE_TOKEN manquant dans .env")

# URL de publication Facebook
url = f"https://graph.facebook.com/v27.0/{PAGE_ID}/feed"

# Contenu de la publication
data = {
    "message": "13:09 , Bonjour à tous ! on publie sur hirondelle fr ",
    "access_token": ACCESS_TOKEN
}

# Envoyer la publication
try:
    response = requests.post(url, data=data, timeout=30)

    print("Code HTTP :", response.status_code)
    print("Réponse Facebook :", response.json())

    if response.ok:
        print("Publication publiée avec succès !")
    else:
        print("Erreur lors de la publication.")

except requests.RequestException as e:
    print("Erreur de connexion :", e)

