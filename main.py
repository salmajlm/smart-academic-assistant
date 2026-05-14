from modules.gmail_collector import load_real_emails
from modules.preprocessor import preprocess_emails
from modules.ai_analyzer import analyze_email
from modules.scraper_ensa import get_new_announcements

print(" MODE TEST MANUEL ACTIVÉ - Aucun message WhatsApp ne sera envoyé.\n")

# 1. Collecte
print(" Récupération des emails (Dernières 24h)...")
emails = load_real_emails()
cleaned_emails = preprocess_emails(emails)

print(" Récupération des annonces ENSA...")
announcements = get_new_announcements()

# 2. Analyse des Emails
print("\n=====  ANALYSE DES EMAILS =====")
if not cleaned_emails:
    print("   _Aucun email à analyser._")
else:
    for email in cleaned_emails:
        print(f"\n Sujet : {email['subject']}")
        analysis = analyze_email(email)
        print(f"    Action attendue : {analysis.get('action_attendue', 'Lire')}")
        print(f"    Deadline : {analysis.get('deadline', 'Aucune')}")

# 3. Analyse des Annonces ENSA
print("\n=====  ANALYSE DES ANNONCES ENSA =====")
useless_titles = [
    "Accueil", "Agenda", "Actualités", "Avis aux étudiants",
    "Category: Avis aux étudiants", "Category: Avis de Soutenance",
    "Cycle doctoral", "Planning d’organisation des enseignements"
]

annonces_valides = 0
for announcement in announcements:
    title = announcement.get("title", "")
    content = announcement.get("content", "")

    if title in useless_titles or len(content.strip()) < 50:
        continue

    annonces_valides += 1
    print(f"\n Titre : {title}")

    message = {"subject": title, "body": content}
    analysis = analyze_email(message)

    print(f"    Action attendue : {analysis.get('action_attendue', 'Lire')}")
    print(f"    Deadline : {analysis.get('deadline', 'Aucune')}")
    print(f"    Lien : {announcement.get('url', '')}")

if annonces_valides == 0:
    print("   _Aucune nouvelle annonce valide._")

print("\nFin du test manuel. Pour envoyer le vrai résumé WhatsApp, lance 'auto_email_workflow.py' !")