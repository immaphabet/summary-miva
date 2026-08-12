import os
import uuid
import time
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template_string, request, session
from templates import HTML_LAYOUT, ADMIN_LAYOUT

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "gistpulse_secure_session_key_2026")

ACTIVE_SESSIONS = {}

# --- NEW: SYSTEM STORAGE CACHE FOR INSTANT LOADING ---
NEWS_CACHE = {
    "articles": [],
    "last_updated": 0
}
CACHE_DURATION_SECONDS = 900  # 15 minutes (15 * 60)

def log_user_session():
    if "user_uuid" not in session:
        session["user_uuid"] = str(uuid.uuid4())
    user_agent = request.headers.get('User-Agent', 'Unknown Device')
    ACTIVE_SESSIONS[session["user_uuid"]] = user_agent

# --- SOURCE 1: MYSCHOOL.NG ---
def scrape_myschool(headers):
    articles = []
    url = "https://myschool.ng"
    try:
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            for element in soup.find_all("h4")[:12]:
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

# --- SOURCE 2: PULSE NIGERIA CAMPUS ---
def scrape_pulse_nigeria(headers):
    articles = []
    url = "https://pulse.ng"
    try:
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            for card in soup.find_all("a")[:35]:
                title = " ".join(card.get_text().split()).strip()
                if len(title) < 25 or not card.has_attr("href"):
                    continue
                if "Pulse" in title or "Terms" in title:
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

# --- SOURCE 3: PUNCH EDUCATION NEWS ---
def scrape_punch_edu(headers):
    articles = []
    url = "https://punchng.com"
    try:
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            for item in soup.find_all("h2", class_="post-title")[:12]:
                card_a = item.find("a")
                if card_a and card_a.has_attr("href"):
                    title = " ".join(card_a.get_text().split()).strip()
                    link = card_a["href"]
                    articles.append({
                        "title": title,
                        "summary": "Click to monitor institutional board decisions, ASUU/NUC policies, and national educational directives.",
                        "link": link,
                        "source": "Punch Education"
                    })
    except Exception as e:
        print(f"Punch Scraper Error: {e}")
    return articles

# --- SOURCE 4: OFFICIAL JAMB BOARD REFORMS ---
def scrape_jamb_bulletin(headers):
    articles = []
    url = "https://jamb.gov.ng"
    try:
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            for row in soup.find_all(["h3", "h2", "a"])[:40]:
                title = " ".join(row.get_text().split()).strip()
                if len(title) < 30 or ("JAMB" not in title and "UTME" not in title):
                    continue
                
                link = url if not row.has_attr("href") else row["href"]
                if not link.startswith("http"):
                    link = f"https://jamb.gov.ng{link}"
                    
                articles.append({
                    "title": title,
                    "summary": "Click to verify official Joint Admissions and Matriculation Board (JAMB) regular statements, guidelines, and directives.",
                    "link": link,
                    "source": "JAMB Official"
                })
    except Exception as e:
        print(f"JAMB Portal Scraper Error: {e}")
    return articles

@app.route("/", methods=["GET", "POST"])
def index():
    log_user_session()
    current_time = time.time()
    
    search_filter = ""
    if request.method == "POST":
        search_filter = request.form.get("search_filter", "").strip().lower()
        
    shared_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    
    # ⚡ CHECK CACHE FIRST: If 15 minutes haven't passed, use saved copy instead of scraping again
    if not NEWS_CACHE["articles"] or (current_time - NEWS_CACHE["last_updated"] > CACHE_DURATION_SECONDS):
        print("Cache expired or empty. Running all scrapers in background...")
        all_articles = []
        all_articles.extend(scrape_jamb_bulletin(shared_headers))
        all_articles.extend(scrape_myschool(shared_headers))
        all_articles.extend(scrape_punch_edu(shared_headers))
        all_articles.extend(scrape_pulse_nigeria(shared_headers))
        
        # Universal title deduplication handler
        seen_titles = set()
        unique_articles = []
        for a in all_articles:
            if a["title"].lower() not in seen_titles:
                seen_titles.add(a["title"].lower())
                unique_articles.append(a)
        
        # Save results to memory and update timestamp
        NEWS_CACHE["articles"] = unique_articles
        NEWS_CACHE["last_updated"] = current_time
        print(f"Successfully cached {len(unique_articles)} unique articles.")
    else:
        print("Serving news instantly from server memory cache.")
        
    # Read the pool directly from the active cache matrix
    cached_pool = NEWS_CACHE["articles"]
    
    # Process dynamic user search engine keywords
    compiled_articles = []
    for art in cached_pool:
        if search_filter:
            if search_filter in art["title"].lower() or search_filter in art["source"].lower():
                compiled_articles.append(art)
        else:
            compiled_articles.append(art)
            
    return render_template_string(HTML_LAYOUT, articles=compiled_articles[:40])

@app.route("/admin", methods=["GET", "POST"])
def admin_panel():
    secure_key = "admin123"
    if request.method == "GET":
        is_auth = session.get("admin_logged_in", False)
        return render_template_string(ADMIN_LAYOUT, authenticated=is_auth, active_count=len(ACTIVE_SESSIONS), error=None)
        
    password_input = request.form.get("admin_password", "")
    if password_input == secure_key:
        session["admin_logged_in"] = True
        return render_template_string(ADMIN_LAYOUT, authenticated=True, active_count=len(ACTIVE_SESSIONS), error=None)
    else:
        return render_template_string(ADMIN_LAYOUT, authenticated=False, error="Invalid authentication key. Identity validation rejected.")

if __name__ == '__main__':
    app.run(debug=True)
                
