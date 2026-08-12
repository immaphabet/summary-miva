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

# --- SYSTEM MEMORY CACHE ---
NEWS_CACHE = {
    "articles": [],
    "last_updated": 0
}
CACHE_DURATION_SECONDS = 900  # 15 minutes

def log_user_session():
    if "user_uuid" not in session:
        session["user_uuid"] = str(uuid.uuid4())
    user_agent = request.headers.get('User-Agent', 'Unknown Device')
    ACTIVE_SESSIONS[session["user_uuid"]] = user_agent

# --- HELPER FUNCTION TO BYPASS FIREWALL BLOCKS ---
def fetch_html_safely(target_url, headers):
    # Pulls the secret proxy key securely from your Render dashboard settings
    api_key = os.environ.get("SCRAPER_API_KEY")
    if not api_key:
        print("Warning: SCRAPER_API_KEY environment variable missing on Render!")
        # Fallback to direct request if key isn't set yet
        try:
            r = requests.get(target_url, headers=headers, timeout=8)
            return r.text if r.status_code == 200 else None
        except:
            return None
            
    # Routes through the free proxy cluster mimicking a standard household browser
    proxy_url = "http://scraperapi.com"
    payload = {'api_key': api_key, 'url': target_url}
    try:
        response = requests.get(proxy_url, params=payload, timeout=15)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"Proxy Fetch failed for {target_url}: {e}")
    return None

# --- SOURCE 1: MYSCHOOL.NG ---
def scrape_myschool(headers):
    articles = []
    url = "https://myschool.ng"
    html = fetch_html_safely(url, headers)
    if html:
        try:
            soup = BeautifulSoup(html, "html.parser")
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
            print(f"Myschool parser error: {e}")
    return articles

# --- SOURCE 2: PULSE NIGERIA CAMPUS ---
def scrape_pulse_nigeria(headers):
    articles = []
    url = "https://pulse.ng"
    html = fetch_html_safely(url, headers)
    if html:
        try:
            soup = BeautifulSoup(html, "html.parser")
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
            print(f"Pulse parser error: {e}")
    return articles

# --- SOURCE 3: PUNCH EDUCATION NEWS ---
def scrape_punch_edu(headers):
    articles = []
    url = "https://punchng.com"
    html = fetch_html_safely(url, headers)
    if html:
        try:
            soup = BeautifulSoup(html, "html.parser")
            for item in soup.find_all("h2", class_="post-title")[:15]:
                card_a = item.find("a")
                if card_a and card_a.has_attr("href"):
                    title = " ".join(card_a.get_text().split()).strip()
                    articles.append({
                        "title": title,
                        "summary": "Click to monitor institutional board decisions, ASUU/NUC policies, and national educational directives.",
                        "link": card_a["href"],
                        "source": "Punch Education"
                    })
        except Exception as e:
            print(f"Punch parser error: {e}")
    return articles

# --- SOURCE 4: OFFICIAL JAMB BOARD REFORMS ---
def scrape_jamb_bulletin(headers):
    articles = []
    url = "https://jamb.gov.ng"
    html = fetch_html_safely(url, headers)
    if html:
        try:
            soup = BeautifulSoup(html, "html.parser")
            for row in soup.find_all(["h3", "h2", "a"])[:40]:
                title = " ".join(row.get_text().split()).strip()
                if len(title) < 20:
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
            print(f"JAMB parser error: {e}")
    return articles

# --- SOURCE 5: PREMIUM TIMES EDUCATION ---
def scrape_premium_times(headers):
    articles = []
    url = "https://premiumtimesng.com"
    html = fetch_html_safely(url, headers)
    if html:
        try:
            soup = BeautifulSoup(html, "html.parser")
            for header in soup.find_all("h3", class_="a-story-title")[:15]:
                card_a = header.find("a")
                if card_a and card_a.has_attr("href"):
                    title = " ".join(card_a.get_text().split()).strip()
                    articles.append({
                        "title": title,
                        "summary": "Click to read investigative education reports, university admission breakdowns, and structural policy updates.",
                        "link": card_a["href"],
                        "source": "Premium Times"
                    })
        except Exception as e:
            print(f"Premium Times parser error: {e}")
    return articles

# --- SOURCE 6: VANGUARD NEWS EDUCATION ---
def scrape_vanguard_edu(headers):
    articles = []
    url = "https://vanguardngr.com"
    html = fetch_html_safely(url, headers)
    if html:
        try:
            soup = BeautifulSoup(html, "html.parser")
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
            print(f"Vanguard parser error: {e}")
    return articles

@app.route("/", methods=["GET", "POST"])
def index():
    log_user_session()
    current_time = time.time()
    
    search_filter = request.form.get("search_filter", "")
    if search_filter:
        search_filter = str(search_filter).strip().lower()
        
    shared_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    
    # Refresh cache if empty, running too low, or if 15 minutes expired
    if not NEWS_CACHE["articles"] or len(NEWS_CACHE["articles"]) < 6 or (current_time - NEWS_CACHE["last_updated"] > CACHE_DURATION_SECONDS):
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
            if a["title"].lower() not in seen_titles:
                seen_titles.add(a["title"].lower())
                unique_articles.append(a)
        
        NEWS_CACHE["articles"] = unique_articles
        NEWS_CACHE["last_updated"] = current_time
        
    cached_pool = NEWS_CACHE["articles"]
    
    compiled_articles = []
    for art in cached_pool:
        if search_filter:
            title_lower = str(art.get("title", "")).lower()
            source_lower = str(art.get("source", "")).lower()
            summary_lower = str(art.get("summary", "")).lower()
            if (search_filter in title_lower) or (search_filter in source_lower) or (search_filter in summary_lower):
                compiled_articles.append(art)
        else:
            compiled_articles.append(art)
            
    return render_template_string(HTML_LAYOUT, articles=compiled_articles[:50])

