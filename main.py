import os
import time
import requests

TOKEN = os.environ["BOT_TOKEN"]
API = f"https://api.telegram.org/bot{TOKEN}"

OFFSET = 0


def reply_for(text):
    text_lower = text.lower().strip()

    # Întrebări despre grup
    group_words = [
        "grup", "grupul", "grupu",
        "acces la grup",
        "intru in grup", "intru în grup",
        "cum intru in grup", "cum intru în grup"
    ]

    # Întrebări despre preț
    price_words = [
        "pret", "preț", "pretul", "prețul",
        "cat costa", "cât costă",
        "cat e", "cât e",
        "cost", "tarif"
    ]

    if any(word in text_lower for word in group_words):
        return (
            "Sigur 😊 Dacă vrei acces la grup, "
            "spune-mi și îți explic cum funcționează."
        )

    if any(word in text_lower for word in price_words):
        return (
            "Pentru românce este 20 lei pentru o săptămână "
            "sau 50 lei permanent. 😊"
        )

    if any(word in text_lower for word in [
        "bună", "buna", "salut", "hei", "hello"
    ]):
        return "Bună 😊 Cu ce te pot ajuta?"

    if "cum funcționează" in text_lower or "cum functioneaza" in text_lower:
        return "Sigur 😊 Spune-mi ce anume vrei să știi și îți explic."

    if "cum plătesc" in text_lower or "cum platesc" in text_lower:
        return "Sigur 😊 Îți explic imediat cum poți face plata."

    return "Sigur 😊 Spune-mi ce te interesează."


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
