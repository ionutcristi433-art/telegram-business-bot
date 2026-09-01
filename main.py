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
            "Acesta este primul mesaj al utilizatorului. "
            "Începe obligatoriu cu: "
            "Salut! Eu sunt un chatbot automat, nu sunt o persoană reală. 🤖\n\n"
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

    return (
        "❌ Gemini nu a putut răspunde momentan.\n\n"
        + "\n".join(errors)
    )
