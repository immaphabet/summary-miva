import os
import uuid
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template_string, request, session
from templates import HTML_LAYOUT, ADMIN_LAYOUT

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "gistpulse_secure_session_key_2026")

ACTIVE_SESSIONS = {}

def log_user_session():
    if "user_uuid" not in session:
        session["user_uuid"] = str(uuid.uuid4())
    user_agent = request.headers.get('User-Agent', 'Unknown Device')
    ACTIVE_SESSIONS[session["user_uuid"]] = user_agent

# --- SCRAPER 1: MYSCHOOL.NG ---
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

# --- SCRAPER 2: PULSE NIGERIA CAMPUS ---
def scrape_pulse_nigeria(headers):
    articles = []
    url = "https://pulse.ng"
    try:
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            # Pulse uses custom anchor classes for headings
            for card in soup.find_all("a", class_="card-title-link")[:10]:
                title = " ".join(card.get_text().split()).strip()
                if len(title) < 15:
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

@app.route("/", methods=["GET", "POST"])
def index():
    log_user_session()
    
    search_filter = ""
    if request.method == "POST":
        search_filter = request.form.get("search_filter", "").strip().lower()
        
    shared_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    
    # Run all scrapers and combine results into one pool
    all_articles = []
    all_articles.extend(scrape_myschool(shared_headers))
    all_articles.extend(scrape_pulse_nigeria(shared_headers))
    
    # Filter by user keyword if provided
    compiled_articles = []
    for art in all_articles:
        if search_filter:
            if search_filter in art["title"].lower() or search_filter in art["source"].lower():
                compiled_articles.append(art)
        else:
            compiled_articles.append(art)
            
    # Deduplicate matching titles
    seen = set()
    unique_articles = []
    for a in compiled_articles:
        if a["title"] not in seen:
            seen.add(a["title"])
            unique_articles.append(a)
            
    return render_template_string(HTML_LAYOUT, articles=unique_articles[:35])

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
