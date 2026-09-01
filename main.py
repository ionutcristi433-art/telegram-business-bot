import os
import time
import requests

TOKEN = os.environ["BOT_TOKEN"]
API = f"https://api.telegram.org/bot{TOKEN}"

OFFSET = 0


def reply_for(text):
    text_lower = text.lower().strip()

    # 1. Întrebări despre faptul că e bot / om
    if any(w in text_lower for w in ["esti om", "ești om", "esti bot", "ești bot", "vreau sa fiu om", "vreau să fiu om", "real"]):
        return "Sunt un chatbot creat să ajut pe aici, dar vorbesc aproape ca un om. 😅 Tu ce faci?"

    # 2. Întrebări / răspunsuri de tipul "ce faci", "dorm", "stau"
    if any(w in text_lower for w in ["dorm", "ma culc", "mă culc"]):
        return "Somn ușor! 😴 Vorbim când te trezești dacă te interesează ceva."

    if any(w in text_lower for w in ["ce faci", "ce fac", "cf", "ce mai faci", "ce zici"]):
        return "Uite, bine, răspund la mesaje. Tu ce faci? 😊"

    if any(w in text_lower for w in ["bine", "stau", "nimic", "frec menta"]):
        return "Super! Dacă ai nevoie de vreo informație despre grup sau plată, să-mi zici. 👌"

    # 3. Întrebări despre Plată / IBAN / Cum se plătește
    if any(w in text_lower for w in ["plata", "plată", "iban", "banca", "bancă", "revolut", "card", "transfer", "cum platesc", "cum plătesc"]):
        return (
            "Uite datele pentru plată: 💳\n\n"
            "Titular: Cristian ionut B\n"
            "Banca: BCR (Nenea Ionică Polițistul)\n"
            "IBAN: RO36 RNCB 0511 1755 6400 0001\n\n"
            "După ce trimiți banii, trimite-mi o poză cu dovada și îți dau accesul imediat!"
        )

    # 4. Întrebări despre Preț
    if any(w in text_lower for w in ["pret", "preț", "pretul", "prețul", "cat costa", "cât costă", "cat e", "cât e", "cost"]):
        return "Accesul este 20 lei pentru o săptămână sau 50 lei permanent. 😊"

    # 5. Întrebări despre Grup / Ce conține
    if any(w in text_lower for w in ["grup", "grupul", "grupu", "acces", "intru", "cum functioneaza", "cum funcționează", "ce are", "ce contine", "ce conține"]):
        return "Grupul are peste 13.000 de videoclipuri și 2.000 de poze. 🎥📸 Spune-mi dacă vrei să intri și îți dau IBAN-ul!"

    # 6. Saluturi
    if any(w in text_lower for w in ["bună", "buna", "salut", "hei", "hello", "buna ziua"]):
        return "Bună! 😊 Ce mai faci?"

    # Răspuns scurt, uman, dacă nu se potrivește nicio regulă
    return "Mă bucur de conversație! Spune-mi dacă vrei detalii despre grup sau IBAN-ul pentru acces. 😊"


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

            for update in data.get("result", []):
                OFFSET = update["update_id"] + 1

                message = update.get("business_message")

                if not message:
                    continue

                text = message.get("text")
                connection_id = message.get("business_connection_id")
                chat_id = message["chat"]["id"]

                if not text or not connection_id:
                    continue

                answer = reply_for(text)

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

