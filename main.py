import os
import uuid
import time
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template_string, request, session, make_response
from templates import HTML_LAYOUT, ADMIN_LAYOUT

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "gistpulse_secure_session_key_2026")
ADMIN_KEY = os.environ.get("GISTPULSE_ADMIN_KEY", "pulse2026")

ACTIVE_SESSIONS = {}

NEWS_CACHE = {
    "articles": [],
    "last_updated": 0
}
# Cut cache timing entirely to 60 seconds for debugging live updates
CACHE_DURATION_SECONDS = 60

def log_user_session():
    if "user_uuid" not in session:
        session["user_uuid"] = str(uuid.uuid4())
    user_agent = request.headers.get('User-Agent', 'Unknown Device')
    ACTIVE_SESSIONS[session["user_uuid"]] = user_agent

def parse_rss_feed(url, source_name, summary_text, headers):
    articles = []
    try:
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "xml")
            for item in soup.find_all("item")[:12]:
                title_node = item.find("title")
                link_node = item.find("link")
                
                if title_node and link_node:
                    title = " ".join(title_node.get_text().split()).strip()
                    link = link_node.get_text().strip()
                    
                    if len(title) > 15:
                        articles.append({
                            "title": title,
                            "summary": summary_text,
                            "link": link,
                            "source": source_name
                        })
    except Exception as e:
        print(f"Feed Error on {source_name}: {e}")
    return articles

def scrape_jamb_bulletin(headers):
    articles = []
    url = "https://jamb.gov.ng"
    try:
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            for row in soup.find_all(["h5", "h3"])[:15]:
                title = " ".join(row.get_text().split()).strip()
                if len(title) < 20 or "slide" in title.lower():
                    continue
                card_a = row.find("a") or row.find_parent("a")
                link = card_a["href"] if card_a and card_a.has_attr("href") else url
                articles.append({
                    "title": title,
                    "summary": "Verify the latest official Joint Admissions and Matriculation Board statements.",
                    "link": link if link.startswith("http") else f"https://jamb.gov.ng{link}",
                    "source": "JAMB Official"
                })
    except Exception as e:
        print(f"JAMB Local Parser Error: {e}")
    return articles

def scrape_myschool(headers):
    articles = []
    url = "https://myschool.ng"
    try:
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            for element in soup.find_all("h3")[:20]:
                title = " ".join(element.get_text().split()).strip()
                if len(title) < 25 or "software" in title.lower() or "app" in title.lower():
                    continue
                card_a = element.find("a") or element.find_parent("a")
                link = card_a["href"] if card_a and card_a.has_attr("href") else url
                articles.append({
                    "title": title,
                    "summary": "Click to view full admission schedules, school cut-off marks, and post-UTME tracking briefs.",
                    "link": link if link.startswith("http") else f"https://myschool.ng{link}",
                    "source": "Myschool Portal"
                })
    except Exception as e:
        print(f"Myschool Parser Error: {e}")
    return articles

@app.route("/", methods=["GET", "POST"])
def index():
    log_user_session()
    current_time = time.time()
    search_filter = request.form.get("search_filter", "").strip().lower()
    
    shared_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    
    time_diff = current_time - NEWS_CACHE["last_updated"]
    
    # FORCE NEW INSTANCE RUN: Completely wipe list array to block loop persistence
    if not NEWS_CACHE["articles"] or time_diff > CACHE_DURATION_SECONDS:
        all_articles = []
        
        all_articles.extend(scrape_jamb_bulletin(shared_headers))
        all_articles.extend(scrape_myschool(shared_headers))
        
        all_articles.extend(parse_rss_feed(
            "https://punchng.com", 
            "Punch Education", 
            "Click to monitor institutional board decisions, ASUU/NUC policies, and national educational directives.", 
            shared_headers
        ))
        all_articles.extend(parse_rss_feed(
            "https://premiumtimesng.com", 
            "Premium Times", 
            "Click to read investigative education reports, university admission breakdowns, and structural policy updates.", 
            shared_headers
        ))
        all_articles.extend(parse_rss_feed(
            "https://vanguardngr.com", 
            "Vanguard Edu", 
            "Click to review trending campus activities, national matriculation news, and tertiary grading briefs.", 
            shared_headers
        ))
        all_articles.extend(parse_rss_feed(
            "https://pulse.ng", 
            "Pulse Campus", 
            "Click to read trending Nigerian student lifestyle trends, university gists, and entertainment news.", 
            shared_headers
        ))
        
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
            
    # CRITICAL FIX: Explicitly disable device layout browser caches
    rendered_content = render_template_string(HTML_LAYOUT, articles=compiled_articles)
    response = make_response(rendered_content)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    return response

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

if __name__ == "__main__":
    app.run(debug=True)
                
