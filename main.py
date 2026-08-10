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
        /* Core Reset & Global Styles */
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            margin: 0; 
            padding: 0; 
            background: #f1f5f9;
            color: #0f172a; 
            min-height: 100vh; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            justify-content: center; 
            overflow-x: hidden; 
        }
        
        /* introduction Screen */
        #intro-screen { background: rgba(255, 255, 255, 0.96); max-width: 520px; width: 90%; padding: 35px 25px; border-radius: 24px; box-shadow: 0 20px 40px rgba(15, 23, 42, 0.08); text-align: center; box-sizing: border-box; margin: 20px auto; backdrop-filter: blur(10px); }
        .intro-title { color: #0284c7; font-size: 32px; margin-bottom: 15px; font-weight: 700; }
        
        /* Profile Avatar Styling */
        .profile-avatar { width: 110px; height: 110px; border-radius: 50%; object-fit: cover; border: 4px solid #0284c7; margin: 0 auto 15px auto; box-shadow: 0 4px 15px rgba(2, 132, 199, 0.2); display: block; opacity: 0; transform: scale(0.8); }
        
        .intro-bio { font-size: 14px; color: #475569; line-height: 1.6; margin-bottom: 20px; text-align: left; }
        
        /* Features Card Layout */
        .features-box { text-align: left; background: rgba(248, 250, 252, 0.8); border: 1px solid #e2e8f0; padding: 15px 20px; border-radius: 12px; margin-bottom: 20px; opacity: 0; }
        .features-title { font-size: 15px; font-weight: 700; color: #0284c7; margin-bottom: 10px; }
        .feature-item { font-size: 13px; color: #334155; margin-bottom: 8px; line-height: 1.5; display: flex; align-items: flex-start; gap: 8px; }
        .feature-item:last-child { margin-bottom: 0; }
        .feature-icon { color: #0284c7; font-weight: bold; }

        /* Consent Agreement Box */
        .slide-right-target { background: #f1f5f9; padding: 15px; border-radius: 12px; margin-bottom: 25px; display: flex; align-items: flex-start; text-align: left; gap: 12px; border: 1px solid #e2e8f0; opacity: 0; }
        .agreement-card input { width: 20px; height: 20px; margin-top: 2px; cursor: pointer; accent-color: #0284c7; }
        .agreement-text { font-size: 13px; color: #334155; line-height: 1.5; font-weight: 500; }
        
        /* Action Buttons */
        .primary-btn { width: 100%; padding: 16px; background: #0284c7; color: white; border: none; border-radius: 12px; font-size: 16px; font-weight: bold; cursor: pointer; transition: 0.2s; opacity: 0; }
        .primary-btn:hover { background: #0369a1; }
        .primary-btn:disabled { background: #cbd5e1; cursor: not-allowed; }

        /* CSS Keyframe Timelines */
        @keyframes popAvatar { to { opacity: 1; transform: scale(1); } }
        @keyframes slideInLeft { from { transform: translateX(-100px); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
        @keyframes slideInRight { from { transform: translateX(100px); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
        @keyframes fadeInButton { to { opacity: 1; } }

        .animate-avatar { animation: popAvatar 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) forwards; }
        .animate-left { animation: slideInLeft 0.8s ease-out 0.3s forwards; }
        .animate-right { animation: slideInRight 0.8s ease-out 0.6s forwards; }
        .animate-button { animation: fadeInButton 0.5s ease-out 0.9s forwards; }

        /* Dark Theme Workspace */
        #app-screen { background: #0e1118; color: #e3e8f0; max-width: 600px; width: 95%; margin: 30px auto; padding: 25px; border-radius: 20px; box-shadow: 0 12px 40px rgba(0,0,0,0.3); display: none; box-sizing: border-box; }
        h2 { color: #38bdf8; text-align: center; font-size: 28px; margin-bottom: 5px; margin-top: 0; }
        .subtitle { text-align: center; font-size: 14px; color: #94a3b8; margin-bottom: 20px; }
        
        form { display: flex; flex-direction: column; gap: 15px; }
        textarea { width: 100%; height: 180px; padding: 15px; border: 2px solid #334155; border-radius: 12px; font-size: 16px; background: #1e293b; color: white; box-sizing: border-box; resize: none; }
        textarea:focus { border-color: #38bdf8; outline: none; }
        
        .result-box { background: #1e293b; padding: 20px; border-radius: 12px; border-left: 5px solid #38bdf8; margin-top: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); text-align: left; }
        h3 { margin-top: 0; color: #38bdf8; }
        .result-text { line-height: 1.6; font-size: 15px; color: #e3e8f0; white-space: pre-wrap; }
        .footer { text-align: center; font-size: 12px; color: #64748b; margin-top: 40px; border-top: 1px solid #334155; padding-top: 15px; }
    </style>
</head>
<body>

    <!-- STAGE 1: WELCOME CARD -->
    <div id="intro-screen">
        <div class="intro-title">⚡ Summary Miva</div>
        <div id="bio-text" class="intro-bio">
            Welcome to the academic study assistant. This platform compresses long university slide data into clear exam briefing summaries using AI.
        </div>
        
        <div id="agree-card" class="agreement-card">
            <input type="checkbox" id="consent-check" onchange="toggleLaunchButton()">
            <label for="consent-check" class="agreement-text">
                I agree that this tool is strictly an auxiliary study companion alongside official materials.
            </label>
        </div>
        <br>
        <button id="start-btn" class="primary-btn" disabled onclick="launchWorkspace()">Start Here &rarr;</button>
    </div>

    <!-- STAGE 2: MAIN APPLICATION WORKSPACE -->
    <div id="app-screen">
        <h2>⚡ Summary Miva Web</h2>
        <div class="subtitle">Unofficial Academic Study Companion</div>
        
        <form method="POST">
            <textarea name="lecture_text" placeholder="Paste your lecture notes or slide text here..." required>{{ request.form.get('lecture_text', '') }}</textarea>
            <button type="submit" class="primary-btn" style="opacity:1;">Generate Briefing Summary</button>
        </form>

        {% if summary %}
        <div class="result-box">
            <h3>📝 AI Study Briefing</h3>
            <div class="result-text">{{ summary }}</div>
        </div>
        {% endif() %}
    </div>

    <script>
        // Trigger animations immediately on load
        window.onload = function() {
            document.getElementById('bio-text').classList.add('animate-left');
            document.getElementById('agree-card').classList.add('animate-right');
            document.getElementById('start-btn').classList.add('animate-button');
            
            // Keep workspace visible if a summary was just generated
            {% if summary %}
                launchWorkspace();
            {% endif %}
        };

        function toggleLaunchButton() {
            const checkBox = document.getElementById("consent-check");
            const startBtn = document.getElementById("start-btn");
            startBtn.disabled = !checkBox.checked;
        }

        function launchWorkspace() {
            document.getElementById("intro-screen").style.display = "none";
            document.getElementById("app-screen").style.display = "block";
        }
    </script>
</body>
</html>
"""  # <--- Closed the HTML triple-quoted string safely here

@app.route("/", methods=["GET", "POST"])
def index():
    summary = ""
    if request.method == "POST":
        lecture_text = request.form.get("lecture_text")
        if lecture_text:
            try:
                # Log student activity metrics metadata
                VISITOR_LOGS.append({
                    "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                    "ip": request.remote_addr,
                    "length": len(lecture_text)
                })
                # Call Gemini Flash API 
                response = model.generate_content(
                    f"Please provide a crisp, clear exam-prep briefing summary for this academic slide material:\n\n{lecture_text}"
                )
                summary = response.text
            except Exception as e:
                summary = f"API Error: {str(e)}"
                
    return render_template_string(HTML_LAYOUT, summary=summary)

@app.route(f"/{SECRET_ADMIN_PATH}")
def admin_logs():
    return {"total_summaries_generated": len(VISITOR_LOGS), "logs": VISITOR_LOGS}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
