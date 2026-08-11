import os
import uuid
import feedparser
from flask import Flask, render_template_string, request, session
import markdown
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
    rss_url = "https://myschool.ng"
    feed = feedparser.parse(rss_url)
    
    search_filter = ""
    if request.method == "POST":
        search_filter = request.form.get("search_filter", "").strip().lower()
        
    compiled_articles = []
    articles_source = feed.entries if feed.entries else feed.items
    
    if articles_source:
        for entry in articles_source[:15]:
            title = entry.get("title", "")
            summary_text = entry.get("summary", "")
            if "<" in summary_text:
                summary_text = summary_text.split("<")[0]
            if len(summary_text) > 170:
                summary_text = summary_text[:167] + "..."
            link = entry.get("link", "#")
            
            if search_filter:
                if search_filter in title.lower() or search_filter in summary_text.lower():
                    compiled_articles.append({"title": title, "summary": summary_text, "link": link})
            else:
                compiled_articles.append({"title": title, "summary": summary_text, "link": link})
                
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
        
