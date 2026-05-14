
from modules.gmail_collector import load_real_emails, mark_as_read  #==>collecte+marque
from modules.preprocessor import preprocess_emails    #nettoyeur(pour economiser tokens)
from modules.ai_analyzer import analyze_email #ai
from modules.scraper_ensa import get_new_announcements
from modules.summary_agent import generate_smart_summary  #==>l agent qui redige le messg final poli
from modules.notifier import send_whatsapp  #module twilio pour l envoi


def run_auto_email_workflow():
    print("🚀 Lancement du workflow automatisé...")

    # 1. Collecte des EMAILS (Dernières 24h)
    print("📥 Récupération des emails...")
    emails = load_real_emails()#collecte des mssg non lus
    cleaned_emails = preprocess_emails(emails)#on enleve ce qui inutile

    # 2. Collecte des ANNONCES ENSA (Uniquement les nouvelles)
    print("🌐 Vérification des nouvelles annonces sur le site ENSA...")
    new_announcements = get_new_announcements()

    all_tasks = []#panier où on stocke mails + annonces

    print("===== ANALYSE IA EN COURS =====")

    # 3. Analyse des Emails via l'IA
    if cleaned_emails:#si c est vide cad false ==> on saute cette etape
        print(f"📩 Analyse de {len(cleaned_emails)} emails...")
        for email in cleaned_emails:
            # On analyse l'email
            analysis = analyze_email(email)#L'IA lit le mail et remplit ton "moule" Pydantic (Urgence, Deadline, Action).
            all_tasks.append({
                "type": "EMAIL",
                "title": email["subject"],
                "analysis": analysis
            })



            # Une fois l'analyse terminée, on marque l'email comme LU sur Gmail
            # pour qu'il ne soit plus repris dans le prochain scan.
            email_id = email.get("id")
            if email_id:
                mark_as_read(email_id)


    # 4. Traitement des Annonces
    if new_announcements:
        print(f"📢 {len(new_announcements)} nouvelles annonces détectées !")
        for annonc in new_announcements:
            all_tasks.append({
                "type": "ANNONCE_ENSA",
                "title": annonc["title"],
                "analysis": {
                    "resume": annonc["title"],
                    "urgence": "moyenne",
                    "action_attendue": f"Consulter l'annonce ici : {annonc['url']}",
                    "deadline": "Voir lien"
                }
            })

    print("\n===== GÉNÉRATION DU RÉSUMÉ INTELLIGENT =====")

    summary_message = generate_smart_summary(all_tasks)#==> panier complet à l ai==>messg court

    # Optionnel : Afficher dans le terminal pour débugger
    print("\n--- MESSAGE GÉNÉRÉ ---\n", summary_message, "\n----------------------")

    # 6. Envoi WhatsApp
    print("📱 Envoi du message WhatsApp...")
    try:
        sid = send_whatsapp(summary_message)#appel de twilio pour envoyer mssg
        print(f"✅ Workflow terminé avec succès ! (SID: {sid})")
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi WhatsApp : {e}")


if __name__ == "__main__":
    run_auto_email_workflow()

