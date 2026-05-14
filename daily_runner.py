import time #gere les attentes
import os  #verif de l existences des files / idem que pathlib
from datetime import datetime
from auto_email_workflow import run_auto_email_workflow #afin de le lancer automaticly

# Paramètres de l'heure cible
TARGET_HOUR = 16
TARGET_MINUTE = 0

LAST_RUN_FILE = "last_run.txt"


def load_last_run_date():
    if os.path.exists(LAST_RUN_FILE):
        try:
            with open(LAST_RUN_FILE, "r") as f:
                return f.read().strip()
        except:
            return None
    return None


def save_last_run_date():
    with open(LAST_RUN_FILE, "w") as f:
        f.write(datetime.now().strftime("%Y-%m-%d"))


def should_run_today():
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    last_run = load_last_run_date()

    # 1. Déjà exécuté aujourd’hui ?
    if last_run == today:
        return False

    # 2. Retourne True si l'heure cible est atteinte/dépassée, sinon False
    return (now.hour > TARGET_HOUR) or (now.hour == TARGET_HOUR and now.minute >= TARGET_MINUTE)


if __name__ == "__main__":
    print(f"🚀 Scheduler démarré. Cible : {TARGET_HOUR:02d}h{TARGET_MINUTE:02d}")

    while True:
        if should_run_today():
            print("\n📅 Heure atteinte ou rattrapage nécessaire...")
            try:
                run_auto_email_workflow()
                save_last_run_date()
                print("✅ Workflow terminé et date sauvegardée.")
            except Exception as e:
                print(f"❌ Erreur pendant le workflow : {e}")

        # On attend 1 minute avant de vérifier à nouveau
        time.sleep(60)