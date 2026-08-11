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
    articles_source = list(feed.entries) if (hasattr(feed, 'entries') and feed.entries) else []
    
    if not articles_source and hasattr(feed, 'items'):
        raw_items = feed.items() if callable(feed.items) else feed.items
        articles_source = list(raw_items)
        
    if articles_source:
        for entry in articles_source[:15]:
            # --- CRITICAL FIX: Direct string parsing to avoid built-in method address crashes ---
            if isinstance(entry, dict):
                raw_title = entry.get("title", "")
                summary_text = entry.get("summary", "")
                link = entry.get("link", "#")
            else:
                raw_title = getattr(entry, "title", "")
                summary_text = getattr(entry, "summary", "")
                link = getattr(entry, "link", "#")
            
            # Guarantees the title evaluates strictly to a clean text string, dropping method references
            if hasattr(raw_title, '__call__') or callable(raw_title):
                title = str(raw_title)
            else:
                title = str(raw_title).strip()
                
            # Fallback if text data string converts to library object tags
            if "built-in method" in title or "str object at" in title:
                title = "Breaking Campus News Update"
                if isinstance(entry, dict) and "title" in entry:
                    title = str(entry["title"])
                elif hasattr(entry, "title"):
                    title = str(entry.title)
            
            if summary_text:
                summary_text = str(summary_text)
                if "<" in summary_text:
                    summary_text = summary_text.split("<")[0].strip()
                else:
                    summary_text = summary_text.strip()
                    
                if len(summary_text) > 170:
                    summary_text = summary_text[:167] + "..."
            else:
                summary_text = "Click below to read full breaking article details."
                
            if title and "built-in method" not in str(title):
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
                
