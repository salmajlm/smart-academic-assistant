def clean_text(text: str) -> str:
    text = text.strip()
    text = text.replace("\n", " ")
    text = " ".join(text.split())#un seul espace entre les mots de text
    return text


def preprocess_emails(emails: list) -> list:
    cleaned_emails = []

    for email in emails:
        cleaned_email = {
            "id": email["id"],
            "sender": email["sender"],
            "subject": clean_text(email["subject"]),
            "body": clean_text(email["body"]),
            "date": email["date"]
        }
        cleaned_emails.append(cleaned_email)

    return cleaned_emails