          
import os
import time
import requests

TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

API = f"https://api.telegram.org/bot{TOKEN}"
LINK_GRUP = "https://t.me/+etpqxigeQ7FlOGE0"

OFFSET = 0
KNOWN_USERS = set()

SYSTEM_PROMPT = """
Ești un chatbot prietenos care vorbește natural în limba română.

REGULA PRINCIPALĂ:
Răspunde natural și direct la ceea ce spune utilizatorul.

FOARTE IMPORTANT:
Dacă utilizatorul vorbește normal, răspunde normal.
NU aduce singur în discuție grupul, accesul, prețul, plata, IBAN-ul,
videoclipurile, pozele sau dovada plății.

Nu face reclamă grupului.
Nu încerca să convingi utilizatorul să cumpere.
Nu schimba o conversație normală într-o conversație despre grup.

EXEMPLE DE CONVERSAȚIE NORMALĂ:

Utilizator: Salut
Tu: Salut! 😄 Ce faci?

Utilizator: Ce faci?
Tu: Sunt pe aici 😄 Tu ce faci?

Utilizator: Ce vreme e?
Tu: Sper să fie o zi frumoasă 😄

La conversațiile normale vorbești ca un chatbot prietenos
și răspunzi doar la subiectul discutat.

MODUL GRUP:

Vorbești despre grup DOAR dacă utilizatorul întreabă direct despre:
- grup
- acces
- vreau acces
- vreau să intru
- cât costă
- cât este
- preț
- plata
- cum plătesc
- unde plătesc
- IBAN
- cont bancar
- date de plată
- ce conține
- câte videoclipuri sunt
- câte poze sunt

Atunci poți explica:

Grupul conține:

13.000+ videoclipuri 🎥
2.000+ poze 📸

Dacă utilizatorul dorește acces și întreabă despre plată,
poți oferi datele de plată.

DATE DE PLATĂ:

Nume titular:

Cristian Ionut B

IBAN:

RO36 RNCB 0511 1755 6400 0001

După efectuarea plății, utilizatorul trebuie să trimită o poză/screenshot
cu dovada plății pentru a primi accesul.

NU inventa alte date.
NU modifica IBAN-ul.
NU modifica numele titularului.

PRIMUL MESAJ:

La primul mesaj al utilizatorului trebuie să începi exact cu:

Salut! Eu sunt un chatbot automat, nu sunt o persoană reală. 🤖

Această frază se spune DOAR la primul mesaj.
La mesajele următoare NU o mai repeta.

IMPORTANT:
Dacă utilizatorul nu întreabă despre grup, acces, preț sau plată,
continuă conversația normală și NU menționa aceste lucruri.
"""


def get_ai_response(chat_id, user_text):
    global KNOWN_USERS

    is_first = chat_id not in KNOWN_USERS
    KNOWN_USERS.add(chat_id)

    if not GEMINI_API_KEY:
        return "⚠️ EROARE: GEMINI_API_KEY nu este setat în Railway!"

    first_instruction = ""

    if is_first:
        first_instruction = """
Acesta este PRIMUL mesaj al utilizatorului.

Începe obligatoriu răspunsul cu:
Salut! Eu sunt un chatbot automat, nu sunt o persoană reală. 🤖
"""

    url = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models/gemini-3.7-flash:generateContent"
    )

    headers = {
        "x-goog-api-key": GEMINI_API_KEY.strip(),
        "Content-Type": "application/json"
    }

    payload = {
        "system_instruction": {
            "parts": [
                {
                    "text": SYSTEM_PROMPT
                }
            ]
        },
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": user_text + "\n\n" + first_instruction
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.8,
            "maxOutputTokens": 250
        }
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=30
        )

        data = response.json()

        if response.status_code != 200:
            error = data.get("error", {})
            message = error.get(
                "message",
                "Eroare necunoscută Gemini"
            )

            return f"❌ Eroare Gemini API: {message}"

        candidates = data.get("candidates", [])

        if not candidates:
            return "⚠️ Gemini nu a returnat niciun răspuns."

        parts = candidates[0].get("content", {}).get("parts", [])

        if not parts:
            return "⚠️ Gemini a returnat un răspuns gol."

        answer = parts[0].get("text", "").strip()

        if not answer:
            return "⚠️ Gemini a returnat un răspuns gol."

        return answer

    except requests.exceptions.Timeout:
        return "❌ Gemini nu a răspuns la timp."

    except requests.exceptions.RequestException as e:
        return f"❌ Eroare conexiune Gemini: {str(e)}"

    except Exception as e:
        return f"❌ Eroare AI: {str(e)}"


def main():
    global OFFSET

    if not TOKEN:
        print("EROARE: BOT_TOKEN nu este setat!")
        return

    if not GEMINI_API_KEY:
        print("EROARE: GEMINI_API_KEY nu este setat!")
        return

    print("================================")
    print("BOT PORNIT")
    print("AI: GOOGLE GEMINI")
    print("================================")

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

                connection_id = message.get(
                    "business_connection_id"
                )

                chat_id = message["chat"]["id"]

                if not connection_id:
                    continue

                # =========================
                # POZĂ = DOVADĂ PLATĂ
                # =========================

                if photo:

                    answer = (
                        "Am primit poza cu dovada plății! 💳✅\n\n"
                        "Îți mulțumesc frumos!\n\n"
                        "Aici este linkul de acces:\n"
                        f"{LINK_GRUP}\n\n"
                        "Bine ai venit! 🌸"
                    )

                # =========================
                # TEXT = GEMINI
                # =========================

                elif text:

                    answer = get_ai_response(
                        chat_id,
                        text
                    )

                else:
                    continue

                # =========================
                # TRIMITE MESAJ TELEGRAM
                # =========================

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

            print(
                "Eroare main loop:",
                e
            )

            time.sleep(5)


if __name__ == "__main__":
    main()


