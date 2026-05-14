import requests #telecharge le code HTML de la page web
from bs4 import BeautifulSoup
import json
from pathlib import Path
from datetime import datetime, timedelta

BASE_URL = "https://ensa.uit.ac.ma/"
OUTPUT_FILE = Path("../data/ensa_announcements.json")
HEADERS = {"User-Agent": "Mozilla/5.0"}# navigateur va voir qui veut entre / on lui dira que je suis mozilla


def scrape_home_carousel():
    try:
        r = requests.get(BASE_URL, headers=HEADERS, timeout=20)#connexion au site
        soup = BeautifulSoup(r.text, "html.parser")
        items = []
        posts = soup.select(".carousel-container .swiper-slide.post")#dans chaq container(carroussel)je rasseble ses articles(post)

        for p in posts:
            title_tag = p.select_one(".post-title a")
            if not title_tag: continue

            items.append({
                "title": title_tag.text.strip(),
                "url": title_tag.get("href"),
                "date_str": p.select_one(".post-date .meta-value").text.strip() if p.select_one(
                    ".post-date .meta-value") else "",
                "scraped_at": datetime.now().isoformat()
            })
        return items
    except Exception as e:
        print(f" Erreur : {e}")
        return []


def get_new_announcements():
    """Compare le site avec le JSON et retourne uniquement les nouveautés"""
    # 1. Charger l'ancien historique
    old_announcements = []
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            old_announcements = json.load(f)

    old_urls = {a['url'] for a in old_announcements}

    # 2. Scraper le site
    current_announcements = scrape_home_carousel()

    # 3. Trouver les nouvelles (URL pas dans l'ancien fichier)
    new_items = [item for item in current_announcements if item['url'] not in old_urls]

    # 4. Mettre à jour le fichier JSON avec tout (pour la prochaine fois)
    # On peut aussi limiter aux 20 dernières pour ne pas que le fichier grossisse à l'infini
    updated_list = (new_items + old_announcements)[:30]#mémoire glissante(sliding wind)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(updated_list, f, ensure_ascii=False, indent=4)

    return new_items