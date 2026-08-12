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

@app.route("/", methods=["GET", "POST"])
def index():
    log_user_session()
    
    search_filter = ""
    if request.method == "POST":
        search_filter = request.form.get("search_filter", "").strip().lower()
        
    compiled_articles = []
    
    # Target URL and a solid user-agent to bypass basic cloud anti-bot filters
    url = "https://myschool.ng"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        # Fetch the HTML instead of feed parsing
        response = requests.get(url, headers=headers, timeout=12)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Myschool structures headlines inside <h4> text tags
            news_elements = soup.find_all("h4")
            
            for element in news_elements:
                title = element.get_text().strip()
                title = " ".join(title.split())  # Clean whitespaces
                
                # Filters out generic short strings, buttons, or blank headers
                if len(title) < 16 or "Simulator" in title or "CBT" in title:
                    continue
                
                # Default fallback summary string
                summary_text = "Click below to read full breaking campus details, instructions, and community comment feeds."
                
                # Try to pull the link from an wrapping <a> tag or nearby parent element
                link = url
                parent_a = element.find_parent("a") or element.find("a")
                if parent_a and parent_a.has_attr("href"):
                    link = parent_a["href"]
                    if not link.startswith("http"):
                        link = f"{url}{link}"
                
                # Match against search queries if the student used the filter bar
                if search_filter:
                    if search_filter in title.lower():
                        compiled_articles.append({"title": title, "summary": summary_text, "link": link})
                else:
                    compiled_articles.append({"title": title, "summary": summary_text, "link": link})
                    
                # Cap the maximum returned homepage stories stream to 15 items
                if len(compiled_articles) >= 15:
                    break
    except Exception as e:
        print(f"Scraper Engine Error: {e}")
                
    return render_template_string(HTML_LAYOUT, articles=compiled_articles)

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
                        
