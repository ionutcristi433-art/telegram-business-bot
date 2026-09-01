import os
import random
import time
import requests

TOKEN = os.environ["BOT_TOKEN"]
API = f"https://api.telegram.org/bot{TOKEN}"

# LINK-UL TĂU REAL DE LA GRUP:
LINK_GRUP = "https://t.me/+etpqxigeQ7FlOGE0"

OFFSET = 0


def reply_for(text, has_photo=False):
    # 1. Dacă clientul a trimis o poză (dovada plății)
    if has_photo:
        return (
            "Salut! Eu sunt un chatbot automat, nu o persoană reală. 🤖\n\n"
            "Am primit poza cu dovada plății! 💳✅ Îți mulțumim!\n\n"
            "Uite link-ul tău direct de acces în grup:\n"
            f"{LINK_GRUP}\n\n"
            "Intră pe link și bucură-te de conținut! 🌸"
        )

    text_lower = text.lower().strip() if text else ""

    # 2. Om / Bot / Vreau să fiu om
    if any(w in text_lower for w in ["esti om", "ești om", "esti bot", "ești bot", "vreau sa fiu om", "vreau să fiu om", "real"]):
        options = [
            "Salut! Eu sunt un chatbot automat, nu sunt o persoană reală. 🤖 Sunt aici să te ajut cu accesul în grup. Tu ce faci?",
            "Salut! Sunt un chatbot automat creat special să răspund rapid la mesaje. Tu ești om real sau mă verifici? 😁",
            "Salut! Sunt doar un chatbot automat programat să îți ofer detalii despre grup și plată."
        ]
        return random.choice(options)

    # 3. Somn / Oboseală / Culcat
    if any(w in text_lower for w in ["dorm", "ma culc", "mă culc", "nani", "somn", "obosit"]):
        options = [
            "Salut! Eu sunt un chatbot automat. Somn ușor! 😴 Vorbim când te trezești.",
            "Salut! Eu sunt un chatbot automat. Noapte bună și odihnă plăcută! 🌙"
        ]
        return random.choice(options)

    # 4. Ce faci / Ce mai zici
    if any(w in text_lower for w in ["ce faci", "ce fac", "cf", "ce mai faci", "ce zici", "ce faci w"]):
        options = [
            "Salut! Eu sunt un chatbot automat, nu sunt o persoană reală. 🤖 Uite, răspund la mesaje pe aici. Tu ce faci? 😊",
            "Salut! Sunt un chatbot automat și stau pe aici să ajut lumea cu detaliile despre grup. Tu ce mai zici?",
            "Salut! Sunt un chatbot automat și totul e ok la mine! Tu ce treabă ai azi?"
        ]
        return random.choice(options)

    # 5. Starea de bine / Stau / Plictiseală
    if any(w in text_lower for w in ["bine", "stau", "nimic", "frec menta", "plictisesc", "plictisit"]):
        options = [
            "Salut! Eu sunt un chatbot automat. Mă bucur! Dacă ai vreo întrebare legată de grup, scrie-mi direct. 👌",
            "Salut! Eu sunt un chatbot automat. Clasic, și eu la fel! 😁",
            "Salut! Eu sunt un chatbot automat. Fain așa, relaxare totală!"
        ]
        return random.choice(options)

    # 6. Plată / IBAN / Cum se plătește
    if any(w in text_lower for w in ["plata", "plată", "iban", "banca", "bancă", "revolut", "card", "transfer", "cum platesc", "cum plătesc"]):
        return (
            "Salut! Eu sunt un chatbot automat, nu o persoană reală. 🤖 Uite datele pentru plată: 💳\n\n"
            "Titular: Cristian ionut B\n"
            "Banca: BCR (Nenea Ionică Polițistul)\n"
            "IBAN: RO36 RNCB 0511 1755 6400 0001\n\n"
            "⚠️ Tariful este de 20 lei (o săptămână) sau 50 lei (permanent).\n"
            "După ce faci plata, trimite-mi o poză cu dovada (chitanța) aici pe chat și îți trimit automat link-ul de acces!"
        )

    # 7. Preț / Tarife
    if any(w in text_lower for w in ["pret", "preț", "pretul", "prețul", "cat costa", "cât costă", "cat e", "cât e", "cost", "tarif"]):
        return (
            "Salut! Eu sunt un chatbot automat, nu o persoană reală. 🤖\n\n"
            "Prețurile pentru accesul în grup sunt:\n"
            "• 20 lei – acces pentru 1 săptămână 🗓️\n"
            "• 50 lei – acces permanent (lifetime) ♾️\n\n"
            "Grupul conține peste 13.000 de videoclipuri și 2.000 de poze! 🎥📸\n"
            "Dacă vrei să plătești, scrie-mi 'iban' sau 'plată'!"
        )

    # 8. Grup / Ce conține / Detalii
    if any(w in text_lower for w in ["grup", "grupul", "grupu", "acces", "intru", "cum functioneaza", "cum funcționează", "ce are", "ce contine", "ce conține", "detalii"]):
        return (
            "Salut! Eu sunt un chatbot automat. 🤖\n\n"
            "Grupul este foarte bogat și conține:\n"
            "• Peste 13.000 de videoclipuri 🎥\n"
            "• Peste 2.000 de poze 📸\n\n"
            "Costă 20 lei pentru o săptămână sau 50 lei permanent.\n"
            "Spune-mi dacă dorești datele bancare (IBAN) pentru înscriere! 😊"
        )

    # 9. Saluturi
    if any(w in text_lower for w in ["bună", "buna", "salut", "hei", "hello", "buna ziua", "neata", "neața"]):
        options = [
            "Salut! Eu sunt un chatbot automat, nu sunt o persoană reală. 😊 Ce mai faci?",
            "Salut! Sunt un chatbot automat. Cu ce te pot ajuta legat de grup, prețuri sau plată?",
            "Salut! Sunt un chatbot automat. Spune-mi ce informații dorești!"
        ]
        return random.choice(options)

    # 10. Răspuns de rezervă (pentru orice alt mesaj text)
    default_options = [
        "Salut! Eu sunt un chatbot automat, nu sunt o persoană reală. 🤖\nGrupul are 13k video și 2k poze. Prețul este 20 lei/săptămână sau 50 lei permanent. Scrie-mi 'iban' pentru plată!",
        "Salut! Sunt un chatbot automat. 😊 Spune-mi dacă te interesează accesul în grup (20 lei/săptămână sau 50 lei permanent) sau datele de plată (IBAN).",
        "Salut! Sunt un chatbot automat. Dacă vrei detalii despre grup sau IBAN-ul pentru plată, zi-mi oricând!"
    ]
    return random.choice(default_options)


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
                photo = message.get("photo")  # Verifică dacă mesajul conține poză
                connection_id = message.get("business_connection_id")
                chat_id = message["chat"]["id"]

                if not connection_id:
                    continue

                # Dacă există poză sau text, trimitem răspunsul corespunzător
                if text or photo:
                    answer = reply_for(text, has_photo=bool(photo))

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

