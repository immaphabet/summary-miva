from flask import Flask, render_template_string, request
import google.generativeai as genai
from datetime import datetime

app = Flask(__name__)

# 🔑 Active production-stable model string configuration
genai.configure(api_key="AQ.Ab8RN6LzjBRO6-riXiNGS2amPS7")
model = genai.GenerativeModel('gemini-2.5-flash')

# 🤫 Your Secret Keyword Path for Developer Tracking Logs
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
        body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background: #f8fafc; color: #0f172a; min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; }
        #intro-screen { background: white; max-width: 500px; width: 90%; padding: 40px 30px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); text-align: center; box-sizing: border-box; }
        .intro-title { color: #0284c7; font-size: 32px; margin-bottom: 15px; font-weight: 700; }
        .profile-avatar { width: 120px; height: 120px; border-radius: 50%; object-fit: cover; border: 4px solid #0284c7; margin: 0 auto 20px auto; box-shadow: 0 4px 15px rgba(2, 132, 199, 0.2); display: block; }
        .intro-bio { font-size: 15px; color: #475569; line-height: 1.6; margin-bottom: 25px; text-align: left; }
        .agreement-card { background: #f1f5f9; padding: 15px; border-radius: 12px; margin-bottom: 25px; display: flex; align-items: flex-start; text-align: left; gap: 12px; border: 1px solid #e2e8f0; }
        .agreement-card input { width: 20px; height: 20px; margin-top: 2px; cursor: pointer; accent-color: #0284c7; }
        .agreement-text { font-size: 13px; color: #334155; line-height: 1.5; font-weight: 500; }
        .primary-btn { width: 100%; padding: 16px; background: #0284c7; color: white; border: none; border-radius: 12px; font-size: 16px; font-weight: bold; cursor: pointer; transition: 0.2s; }
        .primary-btn:hover { background: #0369a1; }
        .primary-btn:disabled { background: #cbd5e1; cursor: not-allowed; }
        #app-screen { background: #0e1118; color: #e3e8f0; max-width: 600px; width: 95%; margin: 30px auto; padding: 25px; border-radius: 20px; box-shadow: 0 12px 40px rgba(0,0,0,0.3); display: none; box-sizing: border-box; }
        h2 { color: #38bdf8; text-align: center; font-size: 28px; margin-bottom: 5px; margin-top: 0; }
        .subtitle { text-align: center; font-size: 14px; color: #94a3b8; margin-bottom: 10px; }
        .dev-badge { text-align: center; margin: 0 auto 25px auto; padding: 8px 15px; background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 50px; width: fit-content; font-size: 13px; font-weight: 500; color: #38bdf8; }
        textarea { width: 100%; height: 180px; padding: 15px; border: 2px solid #334155; border-radius: 12px; font-size: 16px; background: #1e293b; color: white; box-sizing: border-box; resize: none; }
        textarea:focus { border-color: #38bdf8; outline: none; }
        .result-box { background: #1e293b; padding: 20px; border-radius: 12px; border-left: 5px solid #38bdf8; margin-top: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); text-align: left; }
        h3 { margin-top: 0; color: #38bdf8; }
        .result-text { line-height: 1.6; font-size: 15px; color: #e3e8f0; }
        .footer { text-align: center; font-size: 12px; color: #64748b; margin-top: 40px; border-top: 1px solid #334155; padding-top: 15px; }
    </style>
</head>
<body>
    <div id="intro-screen">
        <img class="profile-avatar" src="https://imgur.com" alt="Emmanuel Olorunjuwonlo">
        <div class="intro-title">⚡ Summary Miva</div>
        <div class="intro-bio">
            Welcome to the official Minimum Viable Product (MVP) of your academic study assistant. This platform was engineered by <b>Emmanuel Olorunjuwonlo</b>, a dedicated B.Sc. Computer Science student, to compress long university slide data into clear exam briefing summaries using real-time artificial intelligence core structures.
        </div>
        <div class="agreement-card">
            <input type="checkbox" id="consent-check" onchange="toggleLaunchButton()">
            <div class="agreement-text">
                I agree that this tool is strictly an auxiliary study companion. I will use the generated briefings responsibly alongside official Miva Open University lecture materials.
            </div>
        </div>
        <button id="start-btn" class="primary-btn" disabled onclick="launchWorkspace()">Start Here &rarr;</button>
    </div>

    <div id="app-screen">
        <h2>⚡ Summary Miva Web</h2>
        <div class="subtitle">Unofficial Academic Study Companion</div>
        <div class="dev-badge">🛠️ Engineered by: Emmanuel Olorunjuwonlo (B.Sc. CS Student)</div>
        <form method="POST">
            <textarea name="user_text" placeholder="Paste your long Miva lecture text or assignment slides here..." required>{{ raw_input }}</textarea>
            <button type="submit" class="primary-btn" style="background:#0284c7; margin-top:12px;">Summarize Now</button>
        </form>
        {% if summary %}
        <div class="result-box">
            <h3>📚 Study Briefing Breakdown:</h3>
            <div class="result-text">{{ summary | replace('\n', '<br>') | safe }}</div>
        </div>
        {% endif %}
        <div class="footer">
            © 2026 Summary Miva • Designed & Maintained by Emmanuel Olorunjuwonlo
        </div>
    </div>

    <script>
        {% if summary %}
            document.getElementById("intro-screen").style.display = "none";
            document.getElementById("app-screen").style.display = "block";
            document.body.style.background = "#0e1118";
        {% endif %}
        function toggleLaunchButton() {
            var checkBox = document.getElementById("consent-check");
            var startBtn = document.getElementById("start-btn");
            startBtn.disabled = !checkBox.checked;
        }
        function launchWorkspace() {
            document.getElementById("intro-screen").style.display = "none";
            document.getElementById("app-screen").style.display = "block";
            document.body.style.background = "#0e1118";
        }
    </script>
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
        body { font-family: Arial, sans-serif; padding: 20px; background: #0f172a; color: #f8fafc; display: block; }
        h1 { color: #38bdf8; }
        .stat-card { background: #1e293b; padding: 15px; margin-bottom: 10px; border-radius: 8px; border-bottom: 2px solid #334155; font-size: 14px; text-align: left; }
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
    user_input_text = ""
    if request.method == "POST":
        user_input_text = request.form.get("user_text")
        log_entry = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ip": request.headers.get('X-Forwarded-For', request.remote_addr),
            "device": request.headers.get('User-Agent'),
            "length": len(user_input_text)
        }
        VISITOR_LOGS.insert(0, log_entry)
        prompt = f"Summarize this university academic material into crisp, student-friendly bullet points with core definitions and exam-prep highlights:\n\n{user_input_text}"
        response = model.generate_content(prompt)
        summary_output = response.text
    return render_template_string(HTML_LAYOUT, summary=summary_output, raw_input=user_input_text)

@app.route("/" + SECRET_ADMIN_PATH)
def admin_panel():
    return render_template_string(ADMIN_LAYOUT, logs=VISITOR_LOGS, total_logs=len(VISITOR_LOGS))

if __name__ == "__main__":
    app.run()
