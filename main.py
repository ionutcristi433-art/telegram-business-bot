import os
import time
import requests

TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

API = f"https://api.telegram.org/bot{TOKEN}"
LINK_GRUP = "https://t.me/+etpqxigeQ7FlOGE0"

OFFSET = 0
KNOWN_USERS = set()

# Prompt creat special pentru o conversație umane, ultra-naturală
SYSTEM_PROMPT = """
Ești un admin/asistent super prietenos, amabil și uman pe Telegram.
Numele tău de pe chat este prietenos, vorbești fix ca un om de zi cu zi (folosești emoticoane, prescurtări naturale când e cazul, limbaj cald).

REGULI OBLIGATORII DE COMPORTAMENT:
1. PRIMUL MESAJ DIN CHAT: Trebuie obligatoriu să înceapă FIX cu fraza:
"Salut! Eu sunt un chatbot automat, nu sunt o persoană reală. 🤖"
După această frază, continuă conversația natural.

2. MESAJELE URMĂTOARE: NU mai repeta NICIODATĂ fraza de mai sus! Vorbește direct, scurt (1-3 propoziții), cald și natural.

3. STIL DE CONVERSAȚIE UMANĂ:
- Dacă omul te întreabă "ce faci", "ce mai zici", "ce faci w", răspunde-i ca un prieten (ex: "Uite bine, stau pe acasă și mă mai uit pe mesaje. Tu ce mai faci? 😊").
- Dacă omul zice că e obosit/merge la culcare, dorește-i somn ușor.
- Fii sociabil, nu aduce vorba de IBAN sau plată din proprie inițiativă dacă omul doar face small-talk sau te întreabă de viață.

4. INFORMAȚII PLATĂ & IBAN (Oferă-le DOAR când omul întreabă de plată, bani, acces sau IBAN):
- IBAN: RO36 RNCB 0511 1755 6400 0001
- Titular: Cristian ionut B
- Explică-i scurt și uman: "Trimiți banii în contul de mai sus, iar după ce ai făcut transferul, lasă-mi o poză/screenshot cu dovada direct aici pe chat ca să-ți dau accesul pe loc! 💳✨"
"""


def get_ai_response(chat_id, user_text):
    global KNOWN_USERS

    is_first = chat_id not in KNOWN_USERS
    KNOWN_USERS.add(chat_id)

    instruction = ""
    if is_first:
        instruction = " (ATENȚIE: Acesta este primul mesaj! Începe obligatoriu cu: 'Salut! Eu sunt un chatbot automat, nu sunt o persoană reală. 🤖')"

    if not GROQ_API_KEY:
        print("EROARE CRITICĂ: GROQ_API_KEY nu este setată în Railway!")
        return "Eroare setare AI. Verifică cheia în Railway."

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
        "max_tokens": 180,
        "temperature": 0.8  # Temperatură puțin mai mare pentru un ton mai uman și mai creativ
    }

    try:
        res = requests.post(url, json=payload, headers=headers, timeout=15)
        res_json = res.json()
        if "choices" in res_json:
            return res_json["choices"][0]["message"]["content"].strip()
        else:
            print("Eroare răspuns Groq:", res_json)
            return "Hey! Sunt aici. Cu ce te pot ajuta? 😊"
    except Exception as e:
        print("Eroare conexiune AI:", e)
        return "Sunt online! Spune-mi ce mai zici sau dacă ai nevoie de IBAN."


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

                # Când primește poză (dovada plății)
                if photo:
                    answer = (
                        "Super! Am primit poza cu dovada plății! 💳✅ Îți mulțumesc frumos!\n\n"
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



