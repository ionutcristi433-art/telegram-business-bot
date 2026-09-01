import os
import time
import requests

TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

API = f"https://api.telegram.org/bot{TOKEN}"
LINK_GRUP = "https://t.me/+etpqxigeQ7FlOGE0"

OFFSET = 0
KNOWN_USERS = set()

SYSTEM_PROMPT = """
Ești un admin/asistent super prietenos, uman și sociabil pe Telegram.
Vorbești relaxat și natural în limba română, exact ca o persoană reală (folosești emoticoane, limbaj cald, propoziții scurte).

REGULI OBLIGATORII:
1. La PRIMUL MESAJ din conversație, răspunsul tău TREBUIE să înceapă obligatoriu cu fraza:
"Salut! Eu sunt un chatbot automat, nu sunt o persoană reală. 🤖"
2. La următoarele mesaje din aceeași conversație, NU mai repeta fraza de introducere sub nicio formă! Vorbește direct și natural.
3. Vorbește normal despre orice (small-talk, ce faci, glume) FĂRĂ să menționezi IBAN-ul sau ce conține grupul, dacă nu te întreabă omul direct!

4. DOAR DACĂ CLIENTUL ÎNTREABĂ DIRECT de grup, conținut, plată, bani sau IBAN:
   • Spune-i că grupul conține peste 13.000 de videoclipuri și poze (13k videos & photos).
   • Oferă-i datele de plată:
     - IBAN: RO36 RNCB 0511 1755 6400 0001 (BCR - Nenea Ionică Polițistul)
     - Titular: Cristian ionut B
   • Spune-i să trimită o POZĂ (screenshot) cu dovada plății pe chat pentru a primi link-ul de acces.
"""


def get_ai_response(chat_id, user_text):
    global KNOWN_USERS

    is_first = chat_id not in KNOWN_USERS
    KNOWN_USERS.add(chat_id)

    instruction = ""
    if is_first:
        instruction = " (ATENȚIE: Primul mesaj! Începe obligatoriu cu: 'Salut! Eu sunt un chatbot automat, nu sunt o persoană reală. 🤖')"

    if not GROQ_API_KEY:
        return "⚠️ EROARE: Nu ai setat variabila GROQ_API_KEY în Railway sau e goală!"

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY.strip()}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text + instruction}
        ],
        "max_tokens": 150,
        "temperature": 0.8
    }

    try:
        res = requests.post(url, json=payload, headers=headers, timeout=15)
        res_json = res.json()

        if "error" in res_json:
            err_msg = res_json["error"].get("message", "Eroare necunoscută")
            return f"❌ Eroare Groq API: {err_msg}"

        if "choices" in res_json:
            return res_json["choices"][0]["message"]["content"].strip()
        else:
            return f"⚠️ Răspuns neașteptat de la server: {res_json}"

    except Exception as e:
        return f"❌ Eroare conexiune AI: {str(e)}"


def main():
    global OFFSET

    while True:
        try:
            response = requests.get(
                f"{API}/getUpdates",
                params={
                    "offset": OFFSET,
                    "timeout": 50,
                    "allowed_updates": ["business_message"]
                },
                timeout=60
            )

            data = response.json()
            updates = data.get("result", [])

            if updates:
                OFFSET = updates[-1]["update_id"] + 1

            for update in updates:
                message = update.get("business_message")
                if not message:
                    continue

                text = message.get("text")
                photo = message.get("photo")
                connection_id = message.get("business_connection_id")
                chat_id = message["chat"]["id"]

                if not connection_id:
                    continue

                if photo:
                    answer = (
                        "Am primit poza cu dovada plății! 💳✅ Îți mulțumesc frumos!\n\n"
                        "Aici ai link-ul tău direct pentru accesul în grup:\n"
                        f"{LINK_GRUP}\n\n"
                        "Apasă pe el și bine ai venit! 🌸"
                    )
                elif text:
                    answer = get_ai_response(chat_id, text)
                else:
                    continue

                requests.post(
                    f"{API}/sendMessage",
                    json={
                        "business_connection_id": connection_id,
                        "chat_id": chat_id,
                        "text": answer
                    },
                    timeout=30
                )

        except Exception as e:
            print("Eroare main loop:", e)
            time.sleep(5)


if __name__ == "__main__":
    main()




