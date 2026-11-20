import requests
import json

APP_ID = "TON_APP_ID"
APP_SECRET = "TA_CLE_SECRETE"
USER_TOKEN_TEMP = "TON_USER_TOKEN_TEMPORAIRE"

# 1. Transformer le token temporaire en token longue durée (60 jours)
url_long = "https://facebook.com"
res_long = requests.get(url_long, params={
    "grant_type": "fb_exchange_token",
    "client_id": APP_ID,
    "client_secret": APP_SECRET,
    "fb_exchange_token": USER_TOKEN_TEMP
}).json()

user_token_60j = res_long["access_token"]

# 2. Récupérer les Tokens PERMANENTS ("Jamais") de toutes tes pages d'un coup !
res_pages = requests.get("https://facebook.com", params={
    "access_token": user_token_60j,
    "limit": 100
}).json()

mes_pages = []
for page in res_pages.get("data", []):
    mes_pages.append({
        "nom": page["name"],
        "page_id": page["id"],
        "token_permanent": page["access_token"]
    })
    print(f"✅ {page['name']} (ID: {page['id']}) -> Token permanent récupéré !")

with open("mes_20_pages.json", "w", encoding="utf-8") as f:
    json.dump(mes_pages, f, indent=2, ensure_ascii=False)

print(f"\nTerminé ! {len(mes_pages)} pages sauvegardées dans mes_20_pages.json")
