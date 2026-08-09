from flask import Flask, render_template_string, request
import google.generativeai as genai
from datetime import datetime

app = Flask(__name__)

# Your Active Google Gemini API Engine Key Pre-configured
genai.configure(api_key="AQ.Ab8RN6LzjBRO6-riXiNGS2amPS7")
model = genai.GenerativeModel('gemini-2.5-flash')

# Your Secret Custom Keyword Path for Admin Tracker Logs
SECRET_ADMIN_PATH = "mysecretstats123"

# Memory array to automatically store student activity data
VISITOR_LOGS = []

HTML_LAYOUT = """
<!DOCTYPE html>
<html>
<head>
    <title>Summary Miva Web</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 30px auto; padding: 20px; background: #0e1118; color: #e3e8f0; }
        h2 { color: #38bdf8; text-align: center; font-size: 28px; margin-bottom: 5px; }
        .subtitle { text-align: center; font-size: 14px; color: #94a3b8; margin-bottom: 10px; }
        .dev-badge { text-align: center; margin: 0 auto 25px auto; padding: 8px 15px; background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 50px; width: fit-content; font-size: 13px; font-weight: 500; color: #38bdf8; }
        textarea { width: 100%; height: 180px; padding: 15px; border: 2px solid #334155; border-radius: 12px; font-size: 16px; background: #1e293b; color: white; box-sizing: border-box; resize: none; }
        textarea:focus { border-color: #38bdf8; outline: none; }
        button { width: 100%; padding: 15px; background: #0284c7; color: white; border: none; border-radius: 12px; font-size: 16px; font-weight: bold; cursor: pointer; margin-top: 12px; transition: 0.2s; }
        button:hover { background: #0369a1; }
        .result-box { background: #1e293b; padding: 20px; border-radius: 12px; border-left: 5px solid #38bdf8; margin-top: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
        h3 { margin-top: 0; color: #38bdf8; }
        p { line-height: 1.6; font-size: 15px; }
        .footer { text-align: center; font-size: 12px; color: #64748b; margin-top: 40px; border-top: 1px solid #334155; padding-top: 15px; }
    </style>
</head>
<body>
    <h2>⚡ Summary Miva Web</h2>
    <div class="subtitle">Unofficial Academic Study Companion</div>
    <div class="dev-badge">🛠️ Engineered by: Immaculate (B.Sc. Computer Science)</div>
    
    <form method="POST">
        <textarea name="user_text" placeholder="Paste your long Miva lecture text or assignment slides here..." required></textarea>
        <button type="submit">Summarize Now</button>
    </form>

    {% if summary %}
    <div class="result-box">
        <h3>📚 Study Briefing Breakdown:</h3>
        <p>{{ summary | replace('\n', '<br>') | safe }}</p>
    </div>
    {% endif %}

    <div class="footer">
        © 2026 Summary Miva • Designed & Maintained by Immaculate
    </div>
</body>
</html>
"""

ADMIN_LAYOUT = """
<!DOCTYPE html>
<html>
<head>
    <title>Developer Admin Control Panel</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background: #0f172a; color: #f8fafc; }
        h1 { color: #38bdf8; }
        .stat-card { background: #1e293b; padding: 15px; margin-bottom: 10px; border-radius: 8px; border-bottom: 2px solid #334155; font-size: 14px; }
        .highlight { color: #f43f5e; font-weight: bold; }
        .info { color: #38bdf8; }
    </style>
</head>
<body>
    <h1>📊 Live Developer Admin Panel</h1>
    <p>Total Server Activity Logs: <span class="highlight">{{ total_logs }}</span></p>
    <hr style="border-color: #334155;">
    
    {% for log in logs %}
    <div class="stat-card">
        ⏰ <b>Time:</b> {{ log.time }} <br>
        🌐 <b>IP Address:</b> <span class="info">{{ log.ip }}</span> <br>
        📱 <b>Hardware Device Spec:</b> {{ log.device }} <br>
        📝 <b>Character Input Length:</b> {{ log.length }} chars
    </div>
    {% endfor %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    summary_output = ""
    if request.method == "POST":
        raw_text = request.form.get("user_text")
        
        log_entry = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ip": request.headers.get('X-Forwarded-For', request.remote_addr),
            "device": request.headers.get('User-Agent'),
            "length": len(raw_text)
        }
        VISITOR_LOGS.insert(0, log_entry)
        
        prompt = f"Summarize this university academic material into crisp, student-friendly bullet points with core definitions and exam-prep highlights:\n\n{raw_text}"
        response = model.generate_content(prompt)
        summary_output = response.text
        
    return render_template_string(HTML_LAYOUT, summary=summary_output)

@app.route("/" + SECRET_ADMIN_PATH)
def admin_panel():
    return render_template_string(ADMIN_LAYOUT, logs=VISITOR_LOGS, total_logs=len(VISITOR_LOGS))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
