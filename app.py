import os
import requests
from flask import Flask, request

app = Flask(_name_)

VERIFY_TOKEN = os.environ["VERIFY_TOKEN"]
WA_TOKEN = os.environ["WA_TOKEN"]
PHONE_ID = os.environ["PHONE_ID"]
GEMINI_KEY = os.environ["GEMINI_KEY"]
MODEL = os.environ.get("MODEL", "gemini-flash-latest")

SYSTEM = ("Tu ek helpful family assistant hai. Hindi/Hinglish mein "
          "chhote, saaf jawab de. Homework, recipes, letters, "
          "general sawaal mein help kar.")


def ask_ai(text):
    url = ("https://generativelanguage.googleapis.com/v1beta/models/"
           f"{MODEL}:generateContent?key={GEMINI_KEY}")
    body = {
        "system_instruction": {"parts": [{"text": SYSTEM}]},
        "contents": [{"parts": [{"text": text}]}],
    }
    r = requests.post(url, json=body, timeout=60)
    return r.json()["candidates"][0]["content"]["parts"][0]["text"]


def send(to, text):
    url = f"https://graph.facebook.com/v21.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {WA_TOKEN}"}
    body = {"messaging_product": "whatsapp", "to": to,
            "type": "text", "text": {"body": text}}
    requests.post(url, headers=headers, json=body, timeout=30)


@app.get("/")
def home():
    return "Bot chal raha hai"


@app.get("/webhook")
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge", "")
    return "forbidden", 403


@app.post("/webhook")
def incoming():
    data = request.get_json(silent=True) or {}
    try:
        msg = data["entry"][0]["changes"][0]["value"]["messages"][0]
        if msg["type"] == "text":
            send(msg["from"], ask_ai(msg["text"]["body"]))
    except (KeyError, IndexError):
        pass
    except Exception as e:
        print("error:", e)
    return "ok", 200
