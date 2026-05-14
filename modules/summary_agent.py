import os
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain_core import output_parsers
from langchain_core.prompts import ChatPromptTemplate#pour la creation d un prompt dynamique
from langchain_core.output_parsers import StrOutputParser#retourne text simple

load_dotenv()

AI_PROVIDER = os.getenv("AI_PROVIDER", "openai").lower()

def prepare_tasks_for_summary(tasks: list) -> str:
    """Simplifie les données pour le LLM en incluant le type (EMAIL ou ANNONCE)."""
    simplified = []
    for task in tasks:
        analysis = task.get("analysis", {})
        simplified.append({
            "type": task.get("type", "INFO"), # Distingue Email d'Annonce
            "titre": task.get("title", ""),
            "urgence": analysis.get("urgence", ""),
            "deadline": analysis.get("deadline", ""),
            "action": analysis.get("action_attendue", ""),
            "resume": analysis.get("resume", "")
        })
    return json.dumps(simplified, ensure_ascii=False, indent=2)#Car le LLM lit mieux du texte JSON structuré

# ---------------------------------------------------------
# 1. LE PROMPT MIS À JOUR (Gère Emails + Site ENSA)
# ---------------------------------------------------------
PROMPT_SMART_SUMMARY = """
Tu es l'assistant personnel de Salma. Ton rôle est de lui rédiger un résumé WhatsApp matinal basé sur ses emails ET les nouvelles annonces du site de son école (ENSA).

Ton ton doit être complice, motivant et clair. S'il y a des annonces de l'ENSA, mentionne-les fièrement car c'est important pour sa scolarité.

Date actuelle : {today}

Données récoltées (Emails et Annonces site ENSA) :
{tasks_json}

Règles STRICTES :
1. Salue Salma chaleureusement (ex: "Bonjour Salma ! Voici ton briefing ENSA & Gmail...").
2. Fusionne les informations. Si une annonce ENSA concerne un examen et qu'un email en parle aussi, fais un seul point.
3. Utilise des emojis pour différencier les sources (📧 pour Email, 🌐 pour le site ENSA).
4. Ne mets pas de sections vides.
5. Termine par une petite phrase d'encouragement personnalisée.
6. Garde un formatage simple (pas de gras/italique complexe pour WhatsApp).

Structure recommandée :
🌟 PRIORITÉS (Annonces ENSA importantes ou emails urgents)
📅 À NOTER (Dates limites, examens, inscriptions)
💡 INFOS & NEWS (Le reste des actualités)

Commence directement ton message.
"""

# 2. INITIALISATION LLM

if AI_PROVIDER == "ollama":
    from langchain_ollama import ChatOllama
    llm = ChatOllama(model="llama3.2:3b", temperature=0.2)
elif AI_PROVIDER == "openai":
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)#plus humain
else:
    raise ValueError("AI_PROVIDER doit être 'openai' ou 'ollama'.")


# 3. CHAÎNE LCEL

prompt = ChatPromptTemplate.from_template(PROMPT_SMART_SUMMARY)
chain = prompt | llm | StrOutputParser()

def generate_smart_summary(tasks: list) -> str:
    # Si rien n'a été trouvé (Emails vides et Pas de nouvelles annonces ENSA)
    if not tasks:
        return ("Bonjour Salma ! 🌟\n\n"
                "Rien de nouveau sur le site de l'ENSA ni dans tes emails ce matin.\n"
                "C'est le moment idéal pour avancer sur tes projets actuels ! Passe une excellente journée. ✨")

    tasks_json = prepare_tasks_for_summary(tasks)
    today = datetime.now().strftime("%d/%m/%Y")

    try:
        summary = chain.invoke({
            "tasks_json": tasks_json,
            "today": today
        })
        return summary.strip()[:1550]

    except Exception as e:
        print(f" Erreur de génération : {e}")
        return "Bonjour Salma, j'ai eu un petit souci technique, mais vérifie tes mails et le site ENSA au cas où ! Bonne journée !"



