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

Răspunde normal și direct la ceea ce spune utilizatorul.

IMPORTANT:
Dacă utilizatorul vorbește normal, răspunde normal.
NU aduce singur în discuție grupul, accesul, prețul, plata, IBAN-ul,
videoclipurile, pozele sau dovada plății.

Nu face reclamă grupului și nu schimba conversația către grup.

Vorbești despre grup DOAR dacă utilizatorul întreabă direct despre:
- grup
- acces
- vreau acces
- vreau să intru
- cât costă
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

Atunci poți spune:

Grupul conține:

13.000+ videoclipuri 🎥
2.000+ poze 📸

Dacă utilizatorul cere datele de plată, trimite:

Nume titular:

Cristian Ionut B

IBAN:

RO36 RNCB 0511 1755 6400 0001

După efectuarea plății, spune-i să trimită o poză/screenshot
cu dovada plății pentru a primi accesul.

NU inventa alte date.
NU modifica IBAN-ul.
NU modifica numele titularului.

La primul mesaj al utilizatorului începe obligatoriu cu:

Salut! Eu sunt un chatbot automat, nu sunt o persoană reală. 🤖

Această frază se spune doar la primul mesaj.
La următoarele mesaje nu o mai repeta.
"""

GEMINI_MODELS = [
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash"
]


def ask_gemini(model, user_text):

    url = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/{model}:generateContent"
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
                        "text": user_text
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.8,
            "maxOutputTokens": 250
        }
    }

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

        return None, message

    candidates = data.get("candidates", [])

    if not candidates:
        return None, "Gemini nu a returnat niciun răspuns."

    parts = candidates[0].get(
        "content", {}
    ).get("parts", [])

    if not parts:
        return None, "Gemini a returnat un răspuns gol."

    answer = parts[0].get("text", "").strip()

    if not answer:
        return None, "Gemini a returnat un răspuns gol."

    return answer, None


def get_ai_response(chat_id, user_text):

    global KNOWN_USERS

    is_first = chat_id not in KNOWN_USERS

    KNOWN_USERS.add(chat_id)

    if not GEMINI_API_KEY:
        return "⚠️ GEMINI_API_KEY nu este setat în Railway!"

    if is_first:

        user_text = (
            "Acesta este primul mesaj al utilizatorului.\n"
            "Începe obligatoriu răspunsul cu:\n"
            "Salut! Eu sunt un chatbot automat, "
            "nu sunt o persoană reală. 🤖\n\n"
            + user_text
        )

    errors = []

    for model in GEMINI_MODELS:

        try:

            answer, error = ask_gemini(
                model,
                user_text
            )

            if answer:

                print(
                    f"Gemini OK: {model}"
                )

                return answer

            errors.append(
                f"{model}: {error}"
            )

            print(
                f"Gemini eroare {model}: {error}"
            )

        except Exception as e:

            errors.append(
                f"{model}: {str(e)}"
            )

            print(
                f"Gemini exception {model}: {e}"
            )

    print("Toate modelele Gemini au eșuat:")
    print("\n".join(errors))
return (
    "❌ Eroare Gemini:\n\n"
    + "\n".join(errors)
)
    


def main():

    global OFFSET

    if not TOKEN:

        print("❌ BOT_TOKEN nu este setat în Railway!")

        return

    if not GEMINI_API_KEY:

        print("❌ GEMINI_API_KEY nu este setat în Railway!")

        return

    print("==============================")
    print("BOT PORNIT")
    print("AI: GOOGLE GEMINI")
    print("==============================")

    while True:

        try:

            response = requests.get(
                f"{API}/getUpdates",
                params={
                    "offset": OFFSET,
                    "timeout": 50,
                    "allowed_updates": [
                        "business_message"
                    ]
                },
                timeout=60
            )

            data = response.json()

            updates = data.get(
                "result",
                []
            )

            if updates:

                OFFSET = (
                    updates[-1]["update_id"] + 1
                )

            for update in updates:

                message = update.get(
                    "business_message"
                )

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

                # POZA = DOVADA PLĂȚII

                if photo:

                    answer = (
                        "Am primit poza cu dovada plății! 💳✅\n\n"
                        "Îți mulțumesc frumos!\n\n"
                        "Aici este linkul de acces:\n"
                        f"{LINK_GRUP}\n\n"
                        "Bine ai venit! 🌸"
                    )

                # TEXT = GEMINI

                elif text:

                    answer = get_ai_response(
                        chat_id,
                        text
                    )

                else:

                    continue

                # TRIMITE RĂSPUNSUL

                requests.post(
                    f"{API}/sendMessage",
                    json={
                        "business_connection_id":
                            connection_id,
                        "chat_id":
                            chat_id,
                        "text":
                            answer
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
