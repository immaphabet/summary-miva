import os
import uuid
import feedparser
from flask import Flask, render_template_string, request, session
import markdown

app = Flask(__name__)
# Set a secret key to enable secure browser session cookie tracking
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "gistpulse_secure_session_key_2026")

# Server-level in-memory registry dictionary to track live device hits natively
ACTIVE_SESSIONS = {}

HTML_LAYOUT = """
<!DOCTYPE html>
<html>
<head>
    <title>GistPulse | Campus News & Gist Hub</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #000000; color: #ffffff; min-height: 100vh; overflow-x: hidden; }
        #viewport-slider { display: flex; width: 200vw; min-height: 100vh; transition: transform 0.6s cubic-bezier(0.16, 1, 0.3, 1); transform: translateX(0); }
        .page-screen-view { width: 100vw; min-height: 100vh; box-sizing: border-box; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 30px; position: relative; }
        .intro-title { font-size: 42px; font-weight: 700; color: #ffffff; margin-bottom: 8px; letter-spacing: -1px; text-shadow: 0 2px 4px rgba(0,0,0,0.5); }
        .intro-subtitle { font-size: 15px; color: #64748b; text-align: center; max-width: 320px; line-height: 1.5; margin-bottom: 40px; }
        .agreement-pill-box { background: #11141b; border: 1px solid #1e293b; padding: 20px; border-radius: 20px; max-width: 360px; margin-bottom: 35px; box-shadow: 0 4px 12px rgba(0,0,0,0.4); }
        .agreement-row { display: flex; align-items: flex-start; gap: 12px; }
        .agreement-row input[type="checkbox"] { width: 18px; height: 18px; accent-color: #38bdf8; margin-top: 2px; cursor: pointer; flex-shrink: 0; }
        .agreement-text { font-size: 13px; color: #cbd5e1; line-height: 1.5; text-align: left; }
        .enter-hub-btn { background: #38bdf8; color: #000000; border: none; padding: 14px 45px; border-radius: 25px; font-size: 15px; font-weight: 600; cursor: pointer; opacity: 0.5; pointer-events: none; transition: all 0.3s ease; box-shadow: 0 4px 10px rgba(56,189,248,0.2); }
        .enter-hub-btn.active { opacity: 1; pointer-events: auto; }
        .enter-hub-btn.active:active { transform: scale(0.97); background: #0ea5e9; }
        .dashboard-screen { width: 100vw; min-height: 100vh; box-sizing: border-box; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; padding: 20px; position: relative; }
        .workspace-body { width: 100%; max-width: 600px; display: flex; flex-direction: column; justify-content: flex-start; padding-bottom: 140px; margin-top: 10px; }
        .gemini-greeting { font-size: 34px; font-weight: 600; line-height: 1.2; color: #ffffff; letter-spacing: -1px; margin-bottom: 4px; text-align: left; }
        .sub-greeting { font-size: 14px; color: #64748b; margin-bottom: 25px; text-align: left; }
        .output-stream { width: 100%; display: flex; flex-direction: column; gap: 16px; }
        .summary-box { background: #11141b; border: 1px solid #1e293b; padding: 20px; border-radius: 16px; width: 100%; box-sizing: border-box; display: flex; flex-direction: column; gap: 8px; }
        .card-tag { font-size: 11px; color: #38bdf8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
        .card-title { font-size: 18px; font-weight: 600; color: #ffffff; margin: 2px 0; line-height: 1.4; }
        .ai-markdown-bubble { color: #cbd5e1; font-size: 14px; line-height: 1.6; text-align: left; }
        .read-more-btn { align-self: flex-shrink; margin-top: 6px; font-size: 13px; background: #005c4b; color: #ffffff; padding: 6px 14px; border-radius: 20px; text-decoration: none; font-weight: 500; display: inline-block; width: max-content; }
        .no-results { color: #64748b; font-size: 14px; text-align: center; padding: 4px; }
        .bottom-dock { position: fixed; bottom: 0; left: 0; right: 0; background: linear-gradient(transparent, #000000 25%); padding: 20px 0; display: flex; flex-direction: column; align-items: center; z-index: 10; width: 100%; }
        .grok-disclosure-line { font-size: 12px; color: #475569; margin-bottom: 8px; text-align: center; font-weight: 500; }
        .console-pill { width: 92%; max-width: 600px; background: #11141b; border: 1px solid #1e293b; border-radius: 28px; padding: 8px 16px; box-sizing: border-box; display: flex; flex-direction: column; gap: 6px; }
        .input-text-group { display: flex; align-items: center; gap: 10px; width: 100%; }
        textarea { flex: 1; height: 44px; padding: 12px 4px 0 4px; border: none; background: transparent; color: #ffffff; resize: none; font-size: 15px; font-family: inherit; box-sizing: border-box; }
        textarea:focus { outline: none; }
        textarea::placeholder { color: #475569; }
        .action-send-btn { width: 40px; height: 40px; background: #38bdf8; border: none; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; color: #000000; flex-shrink: 0; padding-left: 4px; }
        .action-send-btn svg { fill: #000000; width: 18px; height: 18px; }
    </style>
</head>
<body>
    <div id="viewport-slider">
        <div class="page-screen-view">
            <div class="intro-title">GistPulse</div>
            <div class="intro-subtitle">Unified campus data syndication pipeline. View verified announcements and student gist instantly.</div>
            <div class="agreement-pill-box">
                <div class="agreement-row">
                    <input type="checkbox" id="consent-gate" onchange="toggleEnterPermission(this)">
                    <label class="agreement-text" for="consent-gate">
                        I agree to launch the GistPulse workspace interface and accept that headlines are synchronized live from public university news feeds.
                    </label>
                </div>
            </div>
            <button type="button" class="enter-hub-btn" id="gate-btn" onclick="executeHorizontalSlideTransition()">Enter Workspace</button>
        </div>
        
        <div class="dashboard-screen">
            <div class="workspace-body">
                <div class="gemini-greeting">GistPulse</div>
                <div class="sub-greeting">Latest verified campus news feeds & student gist bundles.</div>
                <div class="output-stream">
                    {% if articles %}
                        {% for item in articles %}
                        <div class="summary-box">
                            <div class="card-tag">Campus Wire</div>
                            <div class="card-title">{{ item.title }}</div>
                            <div class="ai-markdown-bubble">{{ item.summary }}</div>
                            <a href="{{ item.link }}" target="_blank" class="read-more-btn">Read Full Gist</a>
                        </div>
                        {% endfor %}
                    {% else %}
                        <div class="no-results">No trending feeds matching your current filter. Try searching something else!</div>
                    {% endif %}
                </div>
            </div>
            <div class="bottom-dock">
                <div class="grok-disclosure-line">Developed by Emmanuel Olorunjuwonlo</div>
                <div class="console-pill">
                    <form method="POST" action="/" id="engine-form" style="margin:0; display:flex; flex-direction:column; gap:6px;">
                        <div class="input-text-group">
                            <textarea name="search_filter" id="user-input" placeholder="Filter gist (e.g. JAMB, Admission, Miva)..." required></textarea>
                            <button type="submit" class="action-send-btn">
                                <svg viewBox="0 0 24 24">
                                    <path d="M2,21L23,12L2,3V10L17,12L2,14V21Z" />
                                </svg>
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
    <script>
        window.onload = function() {
            const hasQuery = "{{ is_post }}";
            if(hasQuery === "True") {
                document.getElementById("viewport-slider").style.transform = "translateX(-100vw)";
                document.body.style.overflowY = "auto";
            } else {
                document.body.style.overflowY = "hidden";
            }
        };
        function toggleEnterPermission(checkbox) {
            const btn = document.getElementById("gate-btn");
            if(checkbox.checked) { btn.classList.add("active"); } 
            else { btn.classList.remove("active"); }
        }
        function executeHorizontalSlideTransition() {
            document.getElementById("viewport-slider").style.transform = "translateX(-100vw)";
            document.body.style.overflowY = "auto";
        }
    </script>
</body>
</html>
"""

ADMIN_LAYOUT = """
<!DOCTYPE html>
<html>
<head>
    <title>GistPulse | Co-Founder Admin</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: -apple-system, sans-serif; background: #000000; color: #ffffff; padding: 30px; }
        .container { max-width: 500px; margin: 40px auto; background: #11141b; border: 1px solid #1e293b; padding: 24px; border-radius: 16px; text-align: center; }
        h2 { color: #38bdf8; margin-top: 0; }
        .metric-circle { width: 120px; height: 120px; border-radius: 50%; background: #005c4b; display: flex; align-items: center; justify-content: center; font-size: 36px; font-weight: bold; margin: 20px auto; color: #ffffff; border: 2px solid #38bdf8; }
        .text { color: #64748b; font-size: 14px; line-height: 1.5; }
