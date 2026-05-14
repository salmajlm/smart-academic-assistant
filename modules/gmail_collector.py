import os.path
import base64 #car google envoie email(img,piece,texte...) en base 64 ==>fallait le decrypté

#biblio de google,pour gerer securité(OAuth) et la connexion
from google.auth.transport.requests import Request#demande à goog de renouveler le token
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow#ouvre navig pour autoriser
from googleapiclient.discovery import build #cree connexion final avec gmail

# Le scope "modify" est requis pour pouvoir enlever le label UNREAD
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def get_gmail_service():
    creds = None#ensuite ici on va stocker l autorist

    if os.path.exists("token.json"):#si existe on charge les permissions enregistré
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            #Le token est expiré MAIS on possède un refresh_token==> on demande en arriere à google de refrechir sans ouvrir navig
        else:
            #cas de première connexion ==> we use the identity of app
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())#on le cree et on fait dedans les permissions

    return build("gmail", "v1", credentials=creds)#connexion final entr script et gmail


def extract_body(payload):
    body = ""

    if "parts" in payload:
        for part in payload["parts"]:
            if part.get("mimeType") == "text/plain":#car l ai prefere text simple
                data = part.get("body", {}).get("data")
                if data:
                    decoded = base64.urlsafe_b64decode(data)
                    body += decoded.decode(errors="ignore")
    else:
        data = payload.get("body", {}).get("data")
        if data:
            decoded = base64.urlsafe_b64decode(data)
            body = decoded.decode(errors="ignore")

    return body


def load_real_emails(max_results=50):
    service = get_gmail_service()#connexion api-gmail
    print(" Recherche des emails NON LUS des dernières 24h...")

    try:
        #  C'est ici : "newer_than:1d" pour les dernières 24h
        results = service.users().messages().list(
            userId="me",
            q="is:unread newer_than:1d",
            maxResults=max_results#on peut deja la supp
        ).execute()

        messages = results.get("messages", [])#liste des IDS des emails

        if not messages:
            print(" Aucun nouvel email à traiter depuis hier.")
            return []

        emails = []

        for msg in messages:
            msg_data = service.users().messages().get(
                userId="me",
                id=msg["id"]
            ).execute()#on charge chaq mail

            # On récupère le timestamp exact de Google
            internal_date = msg_data.get("internalDate", "")

            payload = msg_data.get("payload", {})
            headers = payload.get("headers", [])#metadata(sujet,date,...)

            subject = ""
            sender = ""
            date_header = ""

            # On récupère aussi la date texte dans les headers
            for header in headers:
                if header["name"].lower() == "subject":
                    subject = header["value"]
                elif header["name"].lower() == "from":
                    sender = header["value"]
                elif header["name"].lower() == "date":
                    date_header = header["value"]

            body = extract_body(payload)#decoder le contenu

            emails.append({
                "id": msg["id"],
                "sender": sender,
                "subject": subject,
                "body": body,
                "date": date_header,  # Date texte
                "internalDate": internal_date  # Timestamp Google
            })

        return emails

    except Exception as e:
        print(f" Erreur API Gmail : {e}")
        return []


def mark_as_read(msg_id):
    """ Supprime le label 'UNREAD' (Non lu) de l'email directement sur Gmail """
    service = get_gmail_service()#tj etablie conn avec api gmail
    try:
        service.users().messages().modify(
            userId='me',
            id=msg_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
        print(f" Email {msg_id} marqué comme LU sur Gmail.")
    except Exception as e:
        print(f" Impossible de marquer l'email {msg_id} comme lu : {e}")


if __name__ == "__main__":
    print(" Tentative de connexion à Google...")
    service = get_gmail_service()
    print("Connexion réussie et token valide !")