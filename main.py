import os
import time
import requests

TOKEN = os.environ["BOT_TOKEN"]
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

API = f"https://api.telegram.org/bot{TOKEN}"
LINK_GRUP = "https://t.me/+etpqxigeQ7FlOGE0"

OFFSET = 0
KNOWN_USERS = set()

# Instrucțiunile pentru AI (păstrat doar IBAN-ul)
SYSTEM_PROMPT = f"""
Ești un asistent virtual pe Telegram.
Rolul tău este să vorbești scurt, natural și prietenos în limba română.

REGULI OBLIGATORII:
1. La PRIMUL mesaj dintr-o conversație nouă, începe RĂSPUNSUL exact cu fraza: "Salut! Eu sunt un chatbot automat, nu sunt o persoană reală. 🤖"
2. La următoarele mesaje din aceeași conversație, NU mai repeta fraza de introducere. Răspunde direct și scurt (1-2 propoziții).
3. Răspunde la orice întrebare de zi cu zi (ce faci, dormi, glume, chestii umane) relaxat și prietenos.

INFORMAȚII PLATĂ (le oferi când clientul întreabă de plată sau iban):
- Date plată IBAN: RO36 RNCB 0511 1755 6400 0001 (BCR - Nenea Ionică Polițistul), Titular: Cristian ionut B.
- Spune-i clientului că după ce face plata, trebuie să trimită o POZĂ (screenshot) cu dovada plății direct pe chat pentru a primi link-ul de acces.
"""


def get_ai_response(chat_id, user_text):
    global KNOWN_USERS

    is_first_message = chat_id not in KNOWN_USERS
    KNOWN_USERS.add(chat_id)

    context_instruction = ""
    if is_first_message:
        context_instruction = " (Aceasta este prima interacțiune cu utilizatorul. Nu uita să începi cu fraza obligatorie: 'Salut! Eu sunt un chatbot automat, nu sunt o persoană reală. 🤖')"

    if not GROQ_API_KEY:
        return "Salut! Eu sunt un chatbot automat. Scrie-mi 'iban' pentru datele de plată!"

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text + context_instruction}
        ],
        "max_tokens": 150,
        "temperature": 0.7
    }

    try:
        res = requests.post(url, json=payload, headers=headers, timeout=15)
        data = res.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("Eroare AI:", e)
        return "Uite bine! Tu ce mai faci? 😊 Scrie-mi 'iban' pentru datele de plată."


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

                # 1. Dacă trimite poză (dovada plății)
                if photo:
                    answer = (
                        "Am primit poza cu dovada plății! 💳✅ Îți mulțumim!\n\n"
                        "Uite link-ul tău direct de acces în grup:\n"
                        f"{LINK_GRUP}\n\n"
                        "Intră pe link și bucură-te de conținut! 🌸"
                    )
                # 2. Dacă trimite text
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
            print("Eroare:", e)
            time.sleep(5)


if __name__ == "__main__":
    main()


