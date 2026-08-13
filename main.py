import os
import uuid
import time
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template_string, request, session, redirect, url_for
from templates import HTML_LAYOUT, ADMIN_LAYOUT

app = Flask(__name__)
# Secure secret session key
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "gistpulse_secure_session_key_2026")
ADMIN_KEY = os.environ.get("GISTPULSE_ADMIN_KEY", "pulse2026")

ACTIVE_SESSIONS = {}

NEWS_CACHE = {
    "articles": [],
    "last_updated": 0
}
# 10 minutes cache duration to keep things fresh
CACHE_DURATION_SECONDS = 600

def log_user_session():
    if "user_uuid" not in session:
        session["user_uuid"] = str(uuid.uuid4())
    user_agent = request.headers.get('User-Agent', 'Unknown Device')
    ACTIVE_SESSIONS[session["user_uuid"]] = user_agent

def scrape_myschool(headers):
    articles = []
    url = "https://myschool.ng"
    try:
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            for element in soup.find_all("h4")[:15]:
                title = " ".join(element.get_text().split()).strip()
                if len(title) < 15 or "Simulator" in title:
                    continue
                link = url
                parent_a = element.find_parent("a") or element.find("a")
                if parent_a and parent_a.has_attr("href"):
                    link = parent_a["href"] if parent_a["href"].startswith("http") else f"{url}{parent_a['href']}"
                articles.append({
                    "title": title,
                    "summary": "Click to view full admission schedules, past questions updates, and cutoff announcements.",
                    "link": link,
                    "source": "Myschool Portal"
                })
    except Exception as e:
        print(f"Myschool Scraper Error: {e}")
    return articles

def scrape_pulse_nigeria(headers):
    articles = []
    url = "https://pulse.ng"
    try:
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            for card in soup.find_all("a")[:35]:
                title = " ".join(card.get_text().split()).strip()
                if len(title) < 25 or not card.has_attr("href") or "Pulse" in title or "Terms" in title:
                    continue
                link = card["href"] if card["href"].startswith("http") else f"https://pulse.ng{card['href']}"
                articles.append({
                    "title": title,
                    "summary": "Click to read trending Nigerian student lifestyle trends, university gists, and entertainment news.",
                    "link": link,
                    "source": "Pulse Campus"
                })
    except Exception as e:
        print(f"Pulse Scraper Error: {e}")
    return articles

def scrape_punch_edu(headers):
    articles = []
    url = "https://punchng.com"
    try:
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            headers_list = soup.find_all("h2") + soup.find_all("h2", class_="post-title")
            for item in headers_list[:15]:
                card_a = item.find("a") or (item if item.name == "a" else None)
                if card_a and card_a.has_attr("href"):
                    title = " ".join(card_a.get_text().split()).strip()
                    if len(title) < 20:
                        continue
                    articles.append({
                        "title": title,
                        "summary": "Click to monitor institutional board decisions, ASUU/NUC policies, and national educational directives.",
                        "link": card_a["href"] if card_a["href"].startswith("http") else f"https://punchng.com{card_a['href']}",
                        "source": "Punch Education"
                    })
    except Exception as e:
        print(f"Punch Scraper Error: {e}")
    return articles

def scrape_jamb_bulletin(headers):
    articles = []
    url = "https://jamb.gov.ng"
    try:
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            for row in soup.find_all(["h5", "h3", "h2"])[:25]:
                title = " ".join(row.get_text().split()).strip()
                if len(title) < 20 or "slide" in title.lower():
                    continue
                link = url
                card_a = row.find("a") or row.find_parent("a")
                if card_a and card_a.has_attr("href"):
                    link = card_a["href"] if card_a["href"].startswith("http") else f"https://jamb.gov.ng{card_a['href']}"
                articles.append({
                    "title": title,
                    "summary": "Click to verify official Joint Admissions and Matriculation Board (JAMB) regular statements and guidelines.",
                    "link": link,
                    "source": "JAMB Official"
                })
    except Exception as e:
        print(f"JAMB Portal Scraper Error: {e}")
    return articles

def scrape_premium_times(headers):
    articles = []
    url = "https://premiumtimesng.com"
    try:
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            for header in soup.find_all("h3")[:20]:
                card_a = header.find("a") or (header if header.name == "a" else None)
                if card_a and card_a.has_attr("href"):
                    title = " ".join(card_a.get_text().split()).strip()
                    if len(title) < 20 or "click" in title.lower():
                        continue
                    articles.append({
                        "title": title,
                        "summary": "Click to read investigative education reports, university admission breakdowns, and structural policy updates.",
                        "link": card_a["href"] if card_a["href"].startswith("http") else f"https://premiumtimesng.com{card_a['href']}",
                        "source": "Premium Times"
                    })
    except Exception as e:
        print(f"Premium Times Scraper Error: {e}")
    return articles

def scrape_vanguard_edu(headers):
    articles = []
    url = "https://vanguardngr.com"
    try:
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            for header in soup.find_all("h2", class_="entry-title")[:15]:
                card_a = header.find("a")
                if card_a and card_a.has_attr("href"):
                    title = " ".join(card_a.get_text().split()).strip()
                    articles.append({
                        "title": title,
                        "summary": "Click to review trending campus activities, national matriculation news, and tertiary grading briefs.",
                        "link": card_a["href"],
                        "source": "Vanguard Edu"
                    })
    except Exception as e:
        print(f"Vanguard Scraper Error: {e}")
    return articles

@app.route("/", methods=["GET", "POST"])
def index():
    log_user_session()
    current_time = time.time()
    search_filter = request.form.get("search_filter", "").strip().lower()
    
    shared_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    
    # Check cache age or if an explicit reload is needed
    time_diff = current_time - NEWS_CACHE["last_updated"]
    if not NEWS_CACHE["articles"] or len(NEWS_CACHE["articles"]) < 5 or time_diff > CACHE_DURATION_SECONDS:
        all_articles = []
        all_articles.extend(scrape_jamb_bulletin(shared_headers))
        all_articles.extend(scrape_myschool(shared_headers))
        all_articles.extend(scrape_punch_edu(shared_headers))
        all_articles.extend(scrape_pulse_nigeria(shared_headers))
        all_articles.extend(scrape_premium_times(shared_headers))
        all_articles.extend(scrape_vanguard_edu(shared_headers))
        
        seen_titles = set()
        unique_articles = []
        for a in all_articles:
            norm_title = a["title"].lower().strip()
            if norm_title not in seen_titles:
                seen_titles.add(norm_title)
                unique_articles.append(a)
                
        NEWS_CACHE["articles"] = unique_articles
        NEWS_CACHE["last_updated"] = current_time

    cached_pool = NEWS_CACHE["articles"]
    compiled_articles = []
    
    for art in cached_pool:
        if search_filter:
            title_lower = str(art.get("title", "")).lower()
            source_lower = str(art.get("source", "")).lower()
            if search_filter in title_lower or search_filter in source_lower:
                compiled_articles.append(art)
        else:
            compiled_articles.append(art)
            
    return render_template_string(HTML_LAYOUT, articles=compiled_articles)

# NEW: The Admin Console Engine linking to your ADMIN_LAYOUT template
@app.route("/admin", methods=["GET", "POST"])
def admin():
    error = None
    if request.method == "POST":
        input_password = request.form.get("admin_password")
        if input_password == ADMIN_KEY:
            session["authenticated"] = True
        else:
            error = "Invalid Administrator Access Key Context."
            
    authenticated = session.get("authenticated", False)
    active_count = len(ACTIVE_SESSIONS)
    
    return render_template_string(
        ADMIN_LAYOUT, 
        authenticated=authenticated, 
        active_count=active_count, 
        error=error
    )

