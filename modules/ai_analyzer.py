import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser#pour verifie qu ereponse ai respecte mon form

load_dotenv()
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai").lower()


# 1. PYDANTIC : Le moule strict pour tes données

class EmailAnalysis(BaseModel):#on cree la forme oblig de la reponse AI
    domaine: str = Field(description="Le domaine de l'email (ex: Cours, Administration, Personnel)")
    resume: str = Field(description="Un résumé clair et ultra-concis de l'email")
    urgence: str = Field(description="Niveau d'urgence strict : 'faible', 'moyenne', ou 'haute'")
    deadline: str = Field(description="La date limite (ex: '2026-05-15', 'aujourd'hui' ou 'non détectée')")
    statut_action: str = Field(description="Statut strict : 'action requise' ou 'information seulement'")
    action_attendue: str = Field(description="L'action précise à effectuer, ou 'Aucune' si informatif")
    raison_priorite: str = Field(description="Explication courte justifiant le niveau d'urgence choisi")
#we gave ces fields pour aider l ai à quoi ecrire

# 2. Création de l'OutputParser basé sur ton modèle Pydantic
parser = PydanticOutputParser(pydantic_object=EmailAnalysis)




# 3. LE PROMPT : pas besoin d'écrire le format JSON à la main

# ai_analyzer.py (Partie Prompt uniquement)

PROMPT_RULES = """
Tu es un assistant IA expert en gestion académique pour Salma, une étudiante à l'ENSA.
Ton rôle est d'analyser cet email récent (reçu il y a moins de 24h) et d'en extraire la substance utile.

CONTEXTE DE L'EMAIL :
- Sujet : {subject}
- Corps : {body}

TES MISSIONS :
1. ANALYSE CRITIQUE : Identifie s'il s'agit d'une information simple ou d'une action concrète à faire (devoir, inscription, réunion).
2. PRIORISATION : Évalue l'urgence en fonction du ton et des dates mentionnées.
3. EXTRACTION : Trouve la deadline précise (ex: "Demain à 18h", "Vendredi prochain") si elle existe.
4. RÉSUMÉ : Rédige une seule phrase très claire qui résume l'essentiel pour une lecture rapide sur mobile.

CONSIGNE PARTICULIÈRE :
Sois très précis sur les noms de professeurs, les matières (ex: Big Data, Chimie) et les plateformes mentionnées (ex: Moodle, Classroom).

{format_instructions}
"""

prompt = ChatPromptTemplate.from_template(PROMPT_RULES)


# 4. INITIALISATION DU MODÈLE ET DE LA CHAÎNE (LCEL)

if AI_PROVIDER == "ollama":
    from langchain_ollama import ChatOllama

    llm = ChatOllama(model="llama3.2:3b", temperature=0)
else:
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)#serieux satable pas de creativite

#La syntaxe de chaînage moderne
# La magie LCEL : Prompt -> LLM -> Pydantic Validation
chain = prompt | llm | parser


def analyze_email(email_data: dict) -> dict:
    """Analyse un email et retourne un dictionnaire formaté et vérifié."""
    try:
        # On injecte les instructions générées automatiquement par Pydantic
        result = chain.invoke({
            "subject": email_data.get("subject", ""),
            "body": email_data.get("body", ""),
            "format_instructions": parser.get_format_instructions()
        })
        # On convertit l'objet Pydantic en dictionnaire classique pour le reste de ton code
        return result.model_dump()

    except Exception as e:
        print(f"⚠️ Erreur d'analyse Pydantic pour '{email_data.get('subject')}': {e}")
        # En cas d'erreur grave, on retourne des valeurs par défaut pour ne pas faire planter l'app
        return {
            "domaine": "Erreur",
            "resume": "Erreur d'analyse IA",
            "urgence": "faible",
            "deadline": "non détectée",
            "statut_action": "information seulement",
            "action_attendue": "Aucune",
            "raison_priorite": "Erreur système"
        }